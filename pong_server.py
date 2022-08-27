import sys

import pygame

from C import *
from R import SESSION_INFO_DELIMITER, decode_str, ID_LEFT, ID_RIGHT, DEFAULT_W_WIDTH, DEFAULT_W_HEIGHT
from U import is_valid_ip
from pong_net_config import *
from GameState import GameState
from DifficultyLevel import DifficultyLevel, load_difficulty
from pong_sessions import ServerSession

print("\n")

sessions = []

server_ip = DEFAULT_SERVER_IP
server_port = DEFAULT_SERVER_PORT

if len(sys.argv) > 1:
    _ip = sys.argv[1]
    if is_valid_ip(_ip):
        server_ip = _ip
    else:
        print(f"Invalid input IP Address: {_ip}")

if len(sys.argv) > 2:
    try:
        server_port = int(sys.argv[2])
    except ValueError:
        print(f"Invalid input port: {sys.argv[2]}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    sock.bind((server_ip, server_port))
except Exception as e:
    print(f"Failed to initialize server at IP: {server_ip}, PORT: {server_port} -> {e}")
    if server_ip != DEFAULT_SERVER_IP or server_port != DEFAULT_SERVER_PORT:
        print("Falling back to default ip and port...")
        server_ip = DEFAULT_SERVER_IP
        server_port = DEFAULT_SERVER_PORT
        try:
            sock.bind((server_ip, server_port))
        except Exception as e:
            print(f"Failed to initialize server at default address -> IP: {server_ip}, PORT: {server_port} -> {e}")
            sys.exit(2)
    else:
        sys.exit(2)


if SERVER_TIMEOUT_SECS > 0:
    sock.settimeout(SERVER_TIMEOUT_SECS)
print(f"Server UP -> IP: {DEFAULT_SERVER_IP}, PORT: {DEFAULT_SERVER_PORT}")

pygame.init()
win = pygame.Surface((DEFAULT_W_WIDTH, DEFAULT_W_HEIGHT))       # dummy window


def get_win():
    global win

    return win


def create_session(win_getter, _session_id: int, difficulty: DifficultyLevel) -> ServerSession:
    return ServerSession(_session_id, GameState.create_server(win_getter=win_getter, difficulty=difficulty))


while True:
    try:
        _bytes, addr = sock.recvfrom(SERVER_RECV_BUF_SIZE)
        msg = decode_str(_bytes)

        arr = msg.split(SESSION_INFO_DELIMITER)
        req = arr[0]

        if req == REQ_TYPE_NEW_PLAYER:                # '{req_code}:{difficulty_code}'
            # find an empty session

            _id = len(sessions)
            _difficulty = load_difficulty(int(arr[1]))
            _player_name = arr[2]

            if not sessions:
                sessions.append(create_session(get_win, _id, _difficulty))

            _session: ServerSession = None
            for s in sessions:
                if s.is_vacant and s.game_state.difficulty == _difficulty:
                    _session = s

            if not _session:
                _session = create_session(get_win, _id, _difficulty)
                sessions.append(_session)

            _player = _session.add_player(addr, _player_name)

            # session = sessions[-1]
            # player = session.add_player(addr)
            # if not player:
            #     session = create_session(_id, _difficulty)
            #     sessions.append(session)
            #     player = session.add_player(addr)

            print(f"Session {_session.session_id} -> added {_player}")

            if _session.is_full:
                _session.start()
                print(f"Session {_session.session_id} -> Started")
            else:
                _session.notify_waiting()

        elif req == REQ_TYPE_REMOVE_PLAYER:         # '{req_code}:{session_id}:{player_id}'
            if len(arr) != 3:
                print("Bad remove player request: " + msg)
            else:
                session_id = int(arr[1])
                if session_id < 0 or session_id >= len(sessions):
                    print(f"Invalid session id: {session_id}, full_request: {msg}")
                else:
                    player_id = int(arr[2])
                    if not (player_id == ID_LEFT or player_id == ID_RIGHT):
                        print(f"Invalid player id: {player_id}, full_request: {msg}")
                    else:
                        _player = sessions[session_id].remove_player(player_id)
                        if _player:
                            print(f"Session {session_id} -> removed {_player}")
        elif req == REQ_TYPE_UPDATE_PLAYER_COORDS:  # '{req_code}:{session_id}:{player_id}:{paddle_coords}'
            if len(arr) != 4:
                print("Bad coords update request: " + msg)
            else:
                session_id = int(arr[1])
                if session_id < 0 or session_id >= len(sessions):
                    print(f"Invalid session id: {session_id}, full_request: {msg}")
                else:
                    player_id = int(arr[2])
                    if not (player_id == ID_LEFT or player_id == ID_RIGHT):
                        print(f"Invalid player id: {player_id}, full_request: {msg}")
                    else:
                        sessions[session_id].game_state.load_paddle_coords(arr[3], left=player_id == ID_LEFT)
    except socket.timeout as t_e:
        print("Server Timeout; " + str(t_e))


pygame.quit()
sys.exit(2)
