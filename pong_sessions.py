import threading
import time
import pygame
import socket
from math import floor

from C import *
from R import REMOTE_PLAYER_DELIMITER, SESSION_INFO_DELIMITER, encode_str, decode_str, ID_NONE, ID_LEFT, ID_RIGHT, AUDIO, CLIENT_DEFAULT_SOUNDS_ENABLED, USER_NAME_LOCAL
from GameState import GameState
from GameMode import *
from DifficultyLevel import DifficultyLevel, load_difficulty
from pong_net_config import FPS_SERVER, FPS_CLIENT, CLIENT_RECV_BUF_SIZE, CLIENT_TIMEOUT_SECS


class RemotePlayer:
    def __init__(self, address: tuple, player_id: int, player_name: str):
        self.address = address
        self._id = player_id
        self._name = player_name

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, player_id: int):
        self._id = player_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, player_name: str):
        self._name = player_name

    @property
    def has_id(self):
        return self.id != ID_NONE

    @property
    def ip(self) -> str:
        return self.address[0]

    @property
    def port(self) -> int:
        return self.address[1]

    def __repr__(self):
        return f"RemotePlayer(ID: {self.id}, name: {self.name}, addr: {self.address})"

    def __str__(self):
        return self.__repr__()

    def dump_string(self):
        return f"{self.ip}{REMOTE_PLAYER_DELIMITER}{self.port}{REMOTE_PLAYER_DELIMITER}{self.id}{REMOTE_PLAYER_DELIMITER}{self.name}"

    @classmethod
    def load_string(cls, _str: str):
        a = _str.split(REMOTE_PLAYER_DELIMITER)
        return cls(address=(a[0], int(a[1])), player_id=int(a[2]), player_name=a[3])


class ServerSession:

    def __init__(self, session_id: int, game_state: GameState, player_left: RemotePlayer = None,
                 player_right: RemotePlayer = None):
        self.session_id = session_id
        self.game_state = game_state

        self._socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._run = False
        self._thread: threading.Thread = None

        self._player_left = player_left
        self._player_right = player_right

        self._cooldown_counter = 0

    @property
    def is_vacant(self) -> bool:
        return self._player_left is None or self._player_right is None

    @property
    def is_full(self):
        return not self.is_vacant

    def get_player(self, left: bool) -> RemotePlayer:
        return self._player_left if left else self._player_right

    def get_player_from_id(self, _id: int) -> RemotePlayer:
        if _id == ID_LEFT:
            return self._player_left
        if _id == ID_RIGHT:
            return self._player_right
        return None

    def notify_waiting(self):
        if self._run:
            return

        if self._player_left:
            self._socket.sendto(self.create_session_waiting_msg(self._player_left.id), self._player_left.address)

        if self._player_right:
            self._socket.sendto(self.create_session_waiting_msg(self._player_right.id), self._player_right.address)

    def add_player(self, address: tuple, player_name: str) -> RemotePlayer:
        if not self._player_left:
            self._player_left = RemotePlayer(address=address, player_id=ID_LEFT, player_name=player_name)
            return self._player_left

        if not self._player_right:
            self._player_right = RemotePlayer(address=address, player_id=ID_RIGHT, player_name=player_name)
            return self._player_right

        return None

    def remove_player(self, player_id: int, notify_other_player: bool = True) -> RemotePlayer:
        player = None
        if player_id == ID_LEFT:
            if self._player_left:
                self.stop()
                player = self._player_left
                self._player_left = None

        elif player_id == ID_RIGHT:
            if self._player_right:
                self.stop()
                player = self._player_right
                self._player_right = None

        if player:
            self.game_state.reset()
            if notify_other_player:
                self._send_both(self.create_enemy_left_msg(player))       # as one is already removed

        return player

    def is_running(self):
        return self._run

    def stop(self):
        self._run = False
        self._cooldown_counter = 0

    def start(self):
        if self._run or self.is_vacant:
            return

        self._run = True
        self._cooldown_counter = 0
        self._thread = threading.Thread(target=self._worker)
        self._thread.start()

    def create_session_waiting_msg(self, player_id: int) -> bytes:
        return encode_str(
            f"{MSG_TYPE_SESSION_WAITING}{SESSION_INFO_DELIMITER}{self.session_id}{SESSION_INFO_DELIMITER}{player_id}")

    def create_session_start_msg(self, player_id: int, other_player: RemotePlayer) -> bytes:
        return encode_str(
            f"{MSG_TYPE_SESSION_START}{SESSION_INFO_DELIMITER}{self.session_id}{SESSION_INFO_DELIMITER}{player_id}"
            f"{SESSION_INFO_DELIMITER}{self.game_state.difficulty.id}{SESSION_INFO_DELIMITER}{other_player.dump_string()}")

    def create_coords_update_msg(self, update_result: int) -> bytes:
        return encode_str(f"{MSG_TYPE_COORDS_UPDATE}{SESSION_INFO_DELIMITER}{self.game_state.server_dump_all_coords()}"
                          f"{SESSION_INFO_DELIMITER}{update_result}")

    def create_score_update_msg(self, update_result: int) -> bytes:
        return encode_str(f"{MSG_TYPE_SCORE_UPDATE}{SESSION_INFO_DELIMITER}{self.game_state.dump_score()}"
                          f"{SESSION_INFO_DELIMITER}{update_result}")

    def create_coords_and_score_update_msg(self, update_result: int) -> bytes:
        return encode_str(
            f"{MSG_TYPE_COORDS_AND_SCORE_UPDATE}{SESSION_INFO_DELIMITER}{self.game_state.server_dump_all_coords()}"
            f"{SESSION_INFO_DELIMITER}{self.game_state.dump_score()}"
            f"{SESSION_INFO_DELIMITER}{update_result}")

    @staticmethod
    def create_enemy_left_msg(enemy: RemotePlayer) -> bytes:
        return encode_str(f"{MSG_TYPE_ENEMY_LEFT}{SESSION_INFO_DELIMITER}{enemy.dump_string()}")

    def _send_both(self, msg: bytes):
        if self._player_left:
            self._socket.sendto(msg, self._player_left.address)
        if self._player_right:
            self._socket.sendto(msg, self._player_right.address)

    # def _wait(self, secs: int, initial_delay: float= 0):
    #     if initial_delay:
    #         time.sleep(initial_delay)
    #
    #     for _ in range(secs):
    #         self._send_both(self.create_coords_update_msg())
    #         time.sleep(1)

    def _worker(self):
        p_left, p_right = self._player_left, self._player_right
        if not (self._run and p_left and p_right):
            return

        p_left.id = ID_LEFT
        p_right.id = ID_RIGHT

        sock = self._socket

        # start msg
        sock.sendto(self.create_session_start_msg(player_id=p_left.id, other_player=p_right), p_left.address)
        sock.sendto(self.create_session_start_msg(player_id=p_right.id, other_player=p_left), p_right.address)

        clock = pygame.time.Clock()
        time.sleep(2)  # initial delay so that clients could set up

        while self._run:
            clock.tick(FPS_SERVER)

            if self._cooldown_counter > 0:
                self._cooldown_counter -= 1
                self._send_both(self.create_coords_update_msg(update_result=GAME_UPDATE_RESULT_NORMAL))
            else:
                update_result = self.game_state.update()
                score_changed = is_score_changed(update_result)
                if score_changed:
                    self._send_both(self.create_coords_and_score_update_msg(update_result=update_result))
                    if self.game_state.any_won():  # Game Finished
                        self._run = False
                        break
                    self._cooldown_counter = floor(FPS_SERVER * self.game_state.difficulty.ball_reset_delay_secs)
                else:
                    self._send_both(self.create_coords_update_msg(update_result=update_result))


class ClientSession:

    def __init__(self, win_getter, game_mode: GameMode, server_addr: tuple, player_name: str,
                 sounds_enabled: bool = CLIENT_DEFAULT_SOUNDS_ENABLED):
        self.win_getter = win_getter
        self.game_mode = game_mode
        self.server_addr = server_addr

        self.player_name = player_name
        self.session_id = ID_NONE
        self.player_id = ID_NONE
        self._other_player: RemotePlayer = None

        self._socket: socket.socket = None
        self._game_state: GameState = None
        self._last_req_difficulty: DifficultyLevel = None
        self._thread: threading.Thread = None
        self._sounds_enabled = sounds_enabled

        self._state: int = CLIENT_SESSION_STATE_IDLE
        self._cooldown_counter = 0

    @property
    def win(self):
        return self.win_getter()

    @property
    def socket(self) -> socket.socket:
        if not self._socket:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if CLIENT_TIMEOUT_SECS > 0:
                self._socket.settimeout(CLIENT_TIMEOUT_SECS)
        return self._socket

    @property
    def game_state(self) -> GameState:
        return self._game_state

    @property
    def difficulty(self) -> DifficultyLevel:
        return self.game_state.difficulty if self.game_state else self._last_req_difficulty

    @property
    def other_player(self) -> RemotePlayer:
        return self._other_player

    @property
    def other_player_name(self) -> str:
        return self._other_player.name if self._other_player else ""

    @property
    def state(self) -> int:
        return self._state

    @property
    def is_idle(self) -> bool:
        return self._state == CLIENT_SESSION_STATE_IDLE

    @property
    def is_connecting(self) -> bool:
        return self._state == CLIENT_SESSION_STATE_CONNECTING

    @property
    def is_waiting(self) -> bool:
        return self._state == CLIENT_SESSION_STATE_WAITING

    @property
    def has_enemy_left(self) -> bool:
        return self._state == CLIENT_SESSION_STATE_ENEMY_LEFT

    @property
    def is_running(self) -> bool:
        return self._state == CLIENT_SESSION_STATE_RUNNING

    @property
    def is_self_left(self) -> bool:
        return self.player_id == ID_LEFT if self.game_mode.online else self.game_mode.self_left_preference

    @property
    def sounds_enabled(self) -> bool:
        return self._sounds_enabled

    @sounds_enabled.setter
    def sounds_enabled(self, value: bool):
        self._sounds_enabled = value

    def toggle_sounds_enabled(self):
        self._sounds_enabled = not self._sounds_enabled

    # def stop_receiving(self):
    #     self._session_state = SESSION_STATE_IDLE

    def create_new_session_msg(self, difficulty: DifficultyLevel) -> bytes:
        return encode_str(f"{REQ_TYPE_NEW_PLAYER}{SESSION_INFO_DELIMITER}{difficulty.id}{SESSION_INFO_DELIMITER}{self.player_name}")

    @staticmethod
    def create_logout_msg(session_id: int, player_id: int) -> bytes:
        return encode_str(
            f"{REQ_TYPE_REMOVE_PLAYER}{SESSION_INFO_DELIMITER}{session_id}{SESSION_INFO_DELIMITER}{player_id}")

    def create_coords_update_msg(self) -> bytes:
        return encode_str(
            f"{REQ_TYPE_UPDATE_PLAYER_COORDS}{SESSION_INFO_DELIMITER}{self.session_id}{SESSION_INFO_DELIMITER}{self.player_id}{SESSION_INFO_DELIMITER}{self.game_state.dump_paddle_coords(self.is_self_left)}")

    def _send_msg(self, msg: bytes):
        self.socket.sendto(msg, self.server_addr)

    def log_out(self):
        if self.game_mode.online:
            s_id, p_id = self.session_id, self.player_id
            added = s_id != ID_NONE and p_id != ID_NONE

            if added:
                self._send_msg(self.create_logout_msg(s_id, p_id))

        self._state = CLIENT_SESSION_STATE_IDLE
        self.session_id = self.player_id = ID_NONE

        if self._game_state:
            self._game_state = None

    def set_idle(self):
        self.log_out()

    def _resend_last_new_session_req(self):
        req = self._last_req_difficulty
        if req:
            self._send_msg(self.create_new_session_msg(req))

    def req_new_session(self, difficulty: DifficultyLevel, force: bool = False):
        if not (force or self._state == CLIENT_SESSION_STATE_IDLE or self._state == CLIENT_SESSION_STATE_ENEMY_LEFT):
            return

        self.log_out()
        self._last_req_difficulty = difficulty

        if self.game_mode == GAME_MODE_ONLINE_MULTI_PLAYER:
            req = self.create_new_session_msg(difficulty=difficulty)
            self._state = CLIENT_SESSION_STATE_CONNECTING
            self._send_msg(req)
            self._thread = threading.Thread(target=self._worker)
            self._thread.start()
        else:
            self._game_state = GameState.create_client(win_getter=self.win_getter, difficulty=difficulty,
                                                       self_left=self.game_mode.self_left_preference)
            self._state = CLIENT_SESSION_STATE_RUNNING

    def update_game(self, keys):
        game_state = self._game_state
        if self.is_running and game_state and not game_state.any_won():
            update_game_state = False
            if self.game_mode == GAME_MODE_ONLINE_MULTI_PLAYER:
                game_state.handle_keys_single_player(keys, self.is_self_left)
            elif self.game_mode == GAME_MODE_OFFLINE_SINGLE_PLAYER:
                update_game_state = True
                _self_left = self.is_self_left
                game_state.handle_keys_single_player(keys, _self_left)
                game_state.ai_handle_player(not _self_left)
            elif self.game_mode == GAME_MODE_OFFLINE_MULTI_PLAYER:
                update_game_state = True
                game_state.handle_keys_both_player(keys)
            else:
                print("Invalid Game Mode -> " + repr(self.game_mode))

            if update_game_state:
                if self._cooldown_counter > 0:
                    self._cooldown_counter -= 1
                else:
                    _update_result = game_state.update()

                    if self.sounds_enabled:
                        AUDIO.consider_play_sound(_update_result=_update_result, _self_left=self.is_self_left)

                    _score_changed = is_score_changed(_update_result)
                    if _score_changed and not self.game_state.any_won():  # Game not Finished
                        self._cooldown_counter = floor(FPS_CLIENT * self.game_state.difficulty.ball_reset_delay_secs)

    def _worker(self):
        while self._state != CLIENT_SESSION_STATE_IDLE:
            try:
                _bytes, addr = self.socket.recvfrom(CLIENT_RECV_BUF_SIZE)
            except socket.timeout or socket.error or OSError as e:
                print("Failed to connect to server, Error: " + str(e))
                if self.is_connecting:
                    print("Retrying to connect to server...")
                    self._resend_last_new_session_req()
                # else:
                #     self._session_state =
            else:
                msg = decode_str(_bytes)
                arr = msg.split(SESSION_INFO_DELIMITER)
                m_type = arr[0]

                send_coords_update = False
                update_result = -1

                if self.is_idle:
                    break

                if m_type == MSG_TYPE_SESSION_WAITING:
                    self.session_id = int(arr[1])
                    self.player_id = int(arr[2])
                    self._state = CLIENT_SESSION_STATE_WAITING
                    self._game_state = None
                elif m_type == MSG_TYPE_SESSION_START:
                    self.session_id = int(arr[1])
                    self.player_id = int(arr[2])
                    self._other_player = RemotePlayer.load_string(arr[4])
                    self._game_state = GameState.create_client(win_getter=self.win_getter, difficulty=load_difficulty(int(arr[3])),
                                                               self_left=self.is_self_left)
                    self._state = CLIENT_SESSION_STATE_RUNNING
                elif m_type == MSG_TYPE_COORDS_UPDATE:
                    if self.is_running:
                        self.game_state.client_load_all_coords(arr[1], self.is_self_left)
                        send_coords_update = True
                    update_result = int(arr[2])
                elif m_type == MSG_TYPE_SCORE_UPDATE:
                    if self.is_running:
                        self.game_state.load_score(arr[1])
                    update_result = int(arr[2])
                elif m_type == MSG_TYPE_COORDS_AND_SCORE_UPDATE:
                    if self.is_running:
                        self.game_state.client_load_all_coords(arr[1], self.is_self_left)
                        self.game_state.load_score(arr[2])
                        send_coords_update = True
                    update_result = int(arr[3])
                elif m_type == MSG_TYPE_ENEMY_LEFT:
                    if not self._other_player:
                        self._other_player = RemotePlayer.load_string(arr[1])
                    self._state = CLIENT_SESSION_STATE_ENEMY_LEFT
                    # self._game_state = None
                else:
                    print(f"Unknown message from server -> Type: {m_type}, Full msg: {msg}")

                if self.sounds_enabled and update_result >= 0:
                    AUDIO.consider_play_sound(_update_result=update_result, _self_left=self.is_self_left)

                if send_coords_update:
                    self._send_msg(self.create_coords_update_msg())
