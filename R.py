import os
import sys
from pygame import Color, mixer, image, surface

from C import GAME_UPDATE_RESULT_SCORE_UP_LEFT, GAME_UPDATE_RESULT_BALL_HIT_TOP_WALL, \
    GAME_UPDATE_RESULT_BALL_HIT_BOTTOM_WALL, GAME_UPDATE_RESULT_BALL_HIT_PADDLE_LEFT, \
    GAME_UPDATE_RESULT_BALL_HIT_PADDLE_RIGHT, GAME_UPDATE_RESULT_SCORE_UP_RIGHT, GAME_UPDATE_RESULT_NORMAL, \
    GAME_UPDATE_RESULT_WON_LEFT, GAME_UPDATE_RESULT_WON_RIGHT, LOCAL_CONFIG_KEY_PLAYER_NAME

from U import get_user_name, remove_all_whitespaces

ID_NONE = -1
ID_LEFT = 0
ID_RIGHT = 1


# Utils
ENCODING = 'utf-8'


def encode_str(msg: str, encoding=ENCODING) -> bytes:
    return bytes(msg, encoding=encoding)


def decode_str(_bytes: bytes, encoding=ENCODING) -> str:
    return _bytes.decode(encoding=encoding)


def gray(i) -> Color:
    return Color(i, i, i)


def load_map(file_path: str, key_value_delimiter: str = '=', comment_token='#',
             remove_whitespaces: bool = True, key_filter=None, value_filter=None) -> dict:
    """
    Load key-value pairs from a given file

    :param file_path: path of input file
    :param key_value_delimiter: delimiter for each entry, line format = key{delimiter}value
    :param comment_token: signifies starting of a comment
    :param remove_whitespaces: whether to remove whitespaces from each line
    :param key_filter: a predicate to decide whether an entry corresponding to key must be included
    :param value_filter: a predicate to decide whether an entry corresponding to value must be included

    :return: dict containing key-value pairs (all as strings)
    """
    _map = {}

    try:
        with open(file_path, "r+") as f:
            for line in f.readlines():
                if comment_token:
                    comment_token_index = line.find(comment_token)
                    if comment_token_index >= 0:
                        line = line[:comment_token_index]
                if remove_whitespaces:
                    line = remove_all_whitespaces(line)
                line = line.replace('\n', '')
                if line:
                    _dat = line.split(key_value_delimiter)
                    if len(_dat) == 2:
                        k, v = _dat[0], _dat[1]
                        if k and (not key_filter or key_filter(k)) and (not value_filter or value_filter(v)):
                            _map[_dat[0]] = _dat[1]
    except Exception as e:
        print(f"Error while loading data from file {file_path}: {e}")

    return _map


DEFAULT_USER_NAME = "Guest"
USER_NAME_LOCAL = get_user_name(default_user_name=DEFAULT_USER_NAME)

# Main Vars
DEFAULT_W_WIDTH, DEFAULT_W_HEIGHT = 1244, 700
DEFAULT_FULLSCREEN = True
FPS = 120
WINNING_SCORE = 10

DISPLAY_TITLE_PART1 = "Ping"
DISPLAY_TITLE_PART2 = "Pong"
DISPLAY_TITLE = "Ping Pong"


DISPLAY_SUMMARY = "Made by RC"
DISPLAY_DESCRIPTION = "A classic online multiplayer Ping-Pong game"
DISPLAY_AUTHOR = "Rohan Chauhan"

EXE_NAME = DISPLAY_TITLE
EXE_VERSION = "1.0.0"

STATUS_TEXT_WINNING_SCORE = "Target"

# Delimiters
REMOTE_PLAYER_DELIMITER = "%"
GAME_STATE_DELIMITER1 = ";"
GAME_STATE_DELIMITER2 = ","
SESSION_INFO_DELIMITER = "|"
STATUS_TEXT_DELIMITER = " | "


# Messages
MSG_SESSION_CONNECTING = "Connecting to server..."
MSG_SESSION_WAITING = "Waiting for players..."
MSG_ENEMY_LEFT_DEFAULT = "Other player left!"
MSG_WON_LEFT = "Left Won!"
MSG_WON_RIGHT = "Right Won!"
MSG_WON_SELF = "You Won!"
MSG_WON_ENEMY = "You Lost!"
MSG_WON_CAPTION = "Press ENTER to continue"

MSG_PAUSED = "Game Paused"
MSG_PAUSED_CAPTION = "Press SPACE to resume"

MSG_CONNECTING_CAPTION = "Press ESCAPE to stop connecting"
MSG_WAITING_CAPTION = "Press ESCAPE to stop matching"
MSG_ENEMY_LEFT_CAPTION = "Press ENTER to continue"

TITLE_CONTROLS = "CONTROLS"
DES_CONTROLS = "Player 1 : UP-DOWN\nPlayer 2 : W-S\nPause : Space\nExit : Escape\nSound : Ctrl-A\nFullscreen : Ctrl-F"

OFFLINE_MULTI_PLAYER_PLAYER1_NAME = "Player 1"
OFFLINE_MULTI_PLAYER_PLAYER2_NAME = "Player 2"
OFFLINE_SINGLE_PLAYER_AI_NAME = "AI"
DEFAULT_ENEMY_NAME = "Opponent"


def format_server_addr(server_ip: str, server_port: int) -> str:
    return f"Server {server_ip}:{server_port}"


def format_player_name(player_name: str) -> str:
    return f"Player : {player_name}"


# def format_score_text(player_name: str, score: int) -> str:
#     return f"{player_name} : {score}" if player_name else str(score)


def get_msg_enemy_left(enemy_name: str, default_msg=MSG_ENEMY_LEFT_DEFAULT) -> str:
    return f"{enemy_name} has left!" if enemy_name else default_msg


# def get_msg_won(self_won: bool, score_diff: int, enemy_name: str, offline_multiplayer: bool, offline_singleplayer: bool) -> tuple:
#     if offline_multiplayer:
#         if self_won:
#             won_name = OFFLINE_MULTIPLAYER_PLAYER1_NAME
#             lost_name = OFFLINE_MULTIPLAYER_PLAYER2_NAME
#             col = COLOR_MSG_WON_SELF
#         else:
#             won_name = OFFLINE_MULTIPLAYER_PLAYER2_NAME
#             lost_name = OFFLINE_MULTIPLAYER_PLAYER1_NAME
#             col = COLOR_MSG_WON_ENEMY
#         won_msg = f"{won_name} won!"
#     else:
#         _enemy_name = enemy_name if enemy_name else OFFLINE_SINGLEPLAER_AI_NAME if offline_singleplayer else DEFAULT_ENEMY_NAME
#         if self_won:
#             won_msg = MSG_WON_SELF
#             lost_name = _enemy_name
#             col = COLOR_MSG_WON_SELF
#         else:
#             won_msg = f"{_enemy_name} won!"
#             lost_name = "You"
#             col = COLOR_MSG_WON_ENEMY
#
#     return won_msg, f"{lost_name} lost by {score_diff} points. {MSG_WON_CAPTION}", col

#
# def get_msg_won_cap(offline_multiplayer: bool, self_won: bool, score_diff: int, enemy_name: str) -> str:
#     if offline_multiplayer:
#         return f"{(OFFLINE_MULTIPLAYER_PLAYER2_NAME if self_won else OFFLINE_MULTIPLAYER_PLAYER1_NAME)} lost by {score_diff} points. {MSG_WON_CAPTION}"
#     return f"{} {'lost' if self_won else 'won'} by {score_diff} points. {MSG_WON_CAPTION}"


def __get_won_msg_cap(player_name: str, score_diff: int, won: bool) -> str:
    return f"{player_name} {'won' if won else 'lost'} by {score_diff} points. {MSG_WON_CAPTION}"


def __get_won_display_info_offline_single_player(self_won: bool, score_diff: int, enemy_name: str = '') -> tuple:
    _enemy_name = enemy_name if enemy_name else OFFLINE_SINGLE_PLAYER_AI_NAME
    if self_won:
        won_msg = MSG_WON_SELF
        col = COLOR_MSG_WON_SELF
    else:
        won_msg = MSG_WON_ENEMY
        col = COLOR_MSG_WON_ENEMY

    won_cap = __get_won_msg_cap(_enemy_name, score_diff, not self_won)
    return won_msg, won_cap, col


def __get_won_display_info_offline_multiplayer(self_won: bool, score_diff: int, enemy_name: str = '') -> tuple:
    if self_won:
        won_name = OFFLINE_MULTI_PLAYER_PLAYER1_NAME
        lost_name = OFFLINE_MULTI_PLAYER_PLAYER2_NAME
        col = COLOR_MSG_WON_SELF
    else:
        won_name = OFFLINE_MULTI_PLAYER_PLAYER2_NAME
        lost_name = OFFLINE_MULTI_PLAYER_PLAYER1_NAME
        col = COLOR_MSG_WON_ENEMY

    won_msg = f"{won_name} won!"
    won_cap = __get_won_msg_cap(lost_name, score_diff, False)
    return won_msg, won_cap, col


def __get_won_display_info_online_multiplayer(self_won: bool, score_diff: int, enemy_name: str = '') -> tuple:
    _enemy_name = enemy_name if enemy_name else DEFAULT_ENEMY_NAME
    if self_won:
        won_msg = MSG_WON_SELF
        col = COLOR_MSG_WON_SELF
    else:
        won_msg = MSG_WON_ENEMY
        col = COLOR_MSG_WON_ENEMY

    won_cap = __get_won_msg_cap(_enemy_name, score_diff, not self_won)
    return won_msg, won_cap, col


def get_self_name_status(name):
    return f"{name} (You)" if name else "You"


def get_enemy_name_status(name):
    return name if name else DEFAULT_ENEMY_NAME


def get_ai_name_status(ai_efficiency_percent: int):
    return f"{OFFLINE_SINGLE_PLAYER_AI_NAME} ({ai_efficiency_percent}%)"


# Home Screen
CLIENT_HOME_SCREEN_PADX = 20
CLIENT_HOME_SCREEN_PADY = 20

CLIENT_HOME_SCREEN_PADX_SOUND_LABEL = 26
CLIENT_HOME_SCREEN_PADY_SOUND_LABEL = 26


# Colors
WHITE = gray(255)
BLACK = gray(0)

BG_DARK = BLACK
BG_MEDIUM = gray(20)
BG_LIGHT = gray(40)

FG_DARK = WHITE
FG_MEDIUM = gray(225)
FG_LIGHT = gray(190)

# COLOR_ACCENT_DARK = Color(57, 206, 255)
# COLOR_ACCENT_MEDIUM = Color(33, 187, 255)
# COLOR_ACCENT_LIGHT = Color(2, 169, 255)

COLOR_ACCENT_DARK = Color(29, 255, 0)
COLOR_ACCENT_MEDIUM = Color(29, 226, 0)
COLOR_ACCENT_LIGHT = Color(29, 190, 0)

COLOR_HIGHLIGHT = Color(253, 255, 52)

COLOR_TRANSPARENT = Color(0, 0, 0, 0)
COLOR_TRANSLUCENT = Color(0, 0, 0, 125)

TINT_SELF_DARK = Color(120, 255, 120)
TINT_SELF_MEDIUM = Color(55, 255, 55)
TINT_SELF_LIGHT = Color(0, 255, 0)

TINT_ENEMY_DARK = Color(255, 120, 120)
TINT_ENEMY_MEDIUM = Color(255, 55, 55)
TINT_ENEMY_LIGHT = Color(255, 0, 0)


COLOR_HOME_TITLE_PART1 = COLOR_ACCENT_DARK
COLOR_HOME_TITLE_PART2 = COLOR_HIGHLIGHT
COLOR_HOME_SUMMARY = FG_MEDIUM
COLOR_STATUS_TEXT = FG_LIGHT
COLOR_PLAYER_STATUS_TEXT = COLOR_HIGHLIGHT

COLOR_PADDLE_ENEMY = TINT_ENEMY_DARK
COLOR_PADDLE_SELF = TINT_SELF_DARK

COLOR_BALL = FG_DARK

COLOR_SCORE_SELF = TINT_SELF_MEDIUM
COLOR_SCORE_ENEMY = TINT_ENEMY_MEDIUM

COLOR_MSG_WON_SELF = TINT_SELF_DARK
COLOR_MSG_WON_ENEMY = TINT_ENEMY_DARK

COLOR_VERTICAL_DIVIDER = BG_LIGHT


# Paddle
PADDLE_REL_WIDTH = 0.0075
PADDLE_REL_HEIGHT = 0.11
PADDLE_CORNERS = 4
PADDLE_REL_PAD_X = 0.01
PADDLE_REL_PAD_Y = 0.0027
PADDLE_REL_VEL = 0.01


# Ball
BALL_DEFAULT_REL_RADIUS = 0.0075
BALL_DEFAULT_REL_VEl_MAX_COMPONENT = 0.0075
BALL_DEFAULT_REL_VEl_MIN_COMPONENT_FACTOR = 0.66
BALL_DEFAULT_RESET_DELAY_SECS = 2
BALL_DEFAULT_RANDOM_INITIAL_VEL_ENABLED = True
# BALL_VEl_TOTAL_MAX = ceil(1.4143 * BALL_VEl_COMPONENT_MAX)
# BALL_VEl_X_INITIAL = BALL_VEl_MAX
# BALL_VEl_Y_INITIAL = 0
# BALL_DEFAULT_DRAW_TRAJECTORY = True
# BALL_ACC = 1
# BALL_ACC_ENABLED = True


# Vertical Divider
VERTICAL_DIVIDER_WIDTH = 6
VERTICAL_DIVIDER_REL_HEIGHT = 0.045
VERTICAL_DIVIDER_CORNERS = 4


# ..........................................  External Resources  ................................
FROZEN = getattr(sys, 'frozen', False)
DIR_MAIN = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

DIR_RES = os.path.join(DIR_MAIN, "res")
DIR_RES_IMAGES = os.path.join(DIR_RES, "images")
DIR_RES_SOUND = os.path.join(DIR_RES, "sound")
DIR_RES_FONT = os.path.join(DIR_RES, "font")

DIR_CONFIG = os.path.join(DIR_MAIN, "config")


def is_file(path: str) -> bool:
    return path and os.path.isfile(path)


# Configs
FILE_PATH_CLIENT_LOCAL_CONFIG = os.path.join(DIR_CONFIG, "local_config.ini")
FILE_PATH_CLIENT_NETWORK_CONFIG = os.path.join(DIR_CONFIG, "client_net_config.ini")


class Config:

    def __init__(self):
        self._client_local_config: dict = None
        self._client_network_config: dict = None

    def invalidate(self):
        self._client_local_config = None
        self._client_network_config = None

    def preload(self):
        a = self.client_local_config
        b = self.client_network_config

    @property
    def client_local_config(self) -> dict:
        if not self._client_local_config and is_file(FILE_PATH_CLIENT_LOCAL_CONFIG):
            self._client_local_config = load_map(FILE_PATH_CLIENT_LOCAL_CONFIG)
        return self._client_local_config

    @property
    def client_network_config(self) -> dict:
        if not self._client_network_config and is_file(FILE_PATH_CLIENT_NETWORK_CONFIG):
            self._client_network_config = load_map(FILE_PATH_CLIENT_NETWORK_CONFIG)
        return self._client_network_config

    def get_client_local_config_player_name(self, default=USER_NAME_LOCAL) -> str:
        data = self.client_local_config
        val = data.get(LOCAL_CONFIG_KEY_PLAYER_NAME, '')
        return val if val else default


CONFIG = Config()


# Images (set "" for None)
FILE_PATH_IMG_EXE_ICON = os.path.join(DIR_RES_IMAGES, "icon_64.ico")
FILE_PATH_IMG_WINDOW_ICON = os.path.join(DIR_RES_IMAGES, "pong_window_icon_32.png")
FILE_PATH_IMG_INTRO_ICON = os.path.join(DIR_RES_IMAGES, "pong_icon_dark_squircle_512.png")
FILE_PATH_IMG_HOME_BG = os.path.join(DIR_RES_IMAGES, "pong_home_bg_512.png")


class Images:

    def __init__(self):
        self._window_icon: surface.Surface = None
        self._intro_icon: surface.Surface = None
        self._home_bg: surface.Surface = None

    def invalidate(self):
        self._window_icon = None
        self._intro_icon = None
        self._home_bg = None

    @property
    def window_icon(self) -> surface.Surface:
        if not self._window_icon and is_file(FILE_PATH_IMG_WINDOW_ICON):
            self._window_icon = image.load(FILE_PATH_IMG_WINDOW_ICON)
        return self._window_icon

    @property
    def intro_icon(self) -> surface.Surface:
        if not self._intro_icon and is_file(FILE_PATH_IMG_INTRO_ICON):
            self._intro_icon = image.load(FILE_PATH_IMG_INTRO_ICON)
        return self._intro_icon

    @property
    def home_bg(self) -> surface.Surface:
        if not self._home_bg and is_file(FILE_PATH_IMG_HOME_BG):
            self._home_bg = image.load(FILE_PATH_IMG_HOME_BG)
        return self._home_bg


IMAGES = Images()           # Singleton


# Sounds (set "" for None)
FILE_PATH_SOUND_BALL_HIT_TOP_WALL = os.path.join(DIR_RES_SOUND, "ball_hit_top_wall.wav")
FILE_PATH_SOUND_BALL_HIT_BOTTOM_WALL = os.path.join(DIR_RES_SOUND, "ball_hit_bottom_wall.wav")
FILE_PATH_SOUND_BALL_HIT_SELF_PADDLE = os.path.join(DIR_RES_SOUND, "ball_hit_paddle_self.wav")
FILE_PATH_SOUND_BALL_HIT_ENEMY_PADDLE = os.path.join(DIR_RES_SOUND, "ball_hit_paddle_enemy.wav")
FILE_PATH_SOUND_SCORE_UP_SELF = os.path.join(DIR_RES_SOUND, "score_up_self.wav")
FILE_PATH_SOUND_SCORE_UP_ENEMY = os.path.join(DIR_RES_SOUND, "score_up_enemy.wav")
FILE_PATH_SOUND_WON_SELF = os.path.join(DIR_RES_SOUND, "won_self.wav")
FILE_PATH_SOUND_WON_ENEMY = os.path.join(DIR_RES_SOUND, "won_enemy.wav")

FILE_PATH_SOUND_BUTTON_HOVER = os.path.join(DIR_RES_SOUND, "button_hover.wav")
FILE_PATH_SOUND_BUTTON_CLICK = os.path.join(DIR_RES_SOUND, "button_click.wav")

CLIENT_DEFAULT_SOUNDS_ENABLED = True

ID_SOUND_ON_BUTTON = 0xFF65A
ID_SOUND_OFF_BUTTON = 0xFB4C
LABEL_TEXT_SOUND = "Sound"
SWITCH_TEXT_SOUND_ON = "ON"
SWITCH_TEXT_SOUND_OFF = "OFF"

STATUS_TEXT_SOUND_ON = "Sound On"
STATUS_TEXT_SOUND_OFF = "Sound Off"

ID_EXIT_BUTTON = -0xFF0AC
EXIT_BUTTON_TEXT = "Quit"


class Audio:

    @staticmethod
    def play_once(sound: mixer.Sound) -> bool:
        if sound:
            sound.play()
            return True
        return False

    def __init__(self):
        self._ball_hit_top_wall: mixer.Sound = None
        self._ball_hit_bottom_wall: mixer.Sound = None
        self._ball_hit_self_paddle: mixer.Sound = None
        self._ball_hit_enemy_paddle: mixer.Sound = None
        self._score_up_self: mixer.Sound = None
        self._score_up_enemy: mixer.Sound = None
        self._won_self: mixer.Sound = None
        self._won_enemy: mixer.Sound = None

        self._button_hover: mixer.Sound = None
        self._button_click: mixer.Sound = None

    def invalidate(self):
        self._ball_hit_top_wall = None
        self._ball_hit_bottom_wall = None
        self._ball_hit_self_paddle = None
        self._ball_hit_enemy_paddle = None
        self._score_up_self = None
        self._score_up_enemy = None
        self._won_self = None
        self._won_enemy = None
        self._button_hover = None
        self._button_click = None

    @property
    def ball_hit_top_wall(self) -> mixer.Sound:
        if not self._ball_hit_top_wall and is_file(FILE_PATH_SOUND_BALL_HIT_TOP_WALL):
            self._ball_hit_top_wall = mixer.Sound(FILE_PATH_SOUND_BALL_HIT_TOP_WALL)
        return self._ball_hit_top_wall

    @property
    def ball_hit_bottom_wall(self) -> mixer.Sound:
        if not self._ball_hit_bottom_wall and is_file(FILE_PATH_SOUND_BALL_HIT_BOTTOM_WALL):
            self._ball_hit_bottom_wall = mixer.Sound(FILE_PATH_SOUND_BALL_HIT_BOTTOM_WALL)
        return self._ball_hit_bottom_wall

    @property
    def ball_hit_self_paddle(self) -> mixer.Sound:
        if not self._ball_hit_self_paddle and is_file(FILE_PATH_SOUND_BALL_HIT_SELF_PADDLE):
            self._ball_hit_self_paddle = mixer.Sound(FILE_PATH_SOUND_BALL_HIT_SELF_PADDLE)
        return self._ball_hit_self_paddle

    @property
    def ball_hit_enemy_paddle(self) -> mixer.Sound:
        if not self._ball_hit_enemy_paddle and is_file(FILE_PATH_SOUND_BALL_HIT_ENEMY_PADDLE):
            self._ball_hit_enemy_paddle = mixer.Sound(FILE_PATH_SOUND_BALL_HIT_ENEMY_PADDLE)
        return self._ball_hit_enemy_paddle

    def get_ball_hit_paddle(self, _self: bool) -> mixer.Sound:
        return self.ball_hit_self_paddle if _self else self.ball_hit_enemy_paddle

    @property
    def score_up_self(self) -> mixer.Sound:
        if not self._score_up_self and is_file(FILE_PATH_SOUND_SCORE_UP_SELF):
            self._score_up_self = mixer.Sound(FILE_PATH_SOUND_SCORE_UP_SELF)
        return self._score_up_self

    @property
    def score_up_enemy(self) -> mixer.Sound:
        if not self._score_up_enemy and is_file(FILE_PATH_SOUND_SCORE_UP_ENEMY):
            self._score_up_enemy = mixer.Sound(FILE_PATH_SOUND_SCORE_UP_ENEMY)
        return self._score_up_enemy

    def get_score_up(self, _self: bool) -> mixer.Sound:
        return self.score_up_self if _self else self.score_up_enemy

    @property
    def won_self(self) -> mixer.Sound:
        if not self._won_self and is_file(FILE_PATH_SOUND_WON_SELF):
            self._won_self = mixer.Sound(FILE_PATH_SOUND_WON_SELF)
        return self._won_self

    @property
    def won_enemy(self) -> mixer.Sound:
        if not self._won_enemy and is_file(FILE_PATH_SOUND_WON_ENEMY):
            self._won_enemy = mixer.Sound(FILE_PATH_SOUND_WON_ENEMY)
        return self._won_enemy

    def get_won(self, _self: bool) -> mixer.Sound:
        return self.won_self if _self else self.won_enemy

    def get(self, _update_result: int, _self_left: bool) -> mixer.Sound:
        _sound = None

        if _update_result == GAME_UPDATE_RESULT_NORMAL:
            pass
        elif _update_result == GAME_UPDATE_RESULT_BALL_HIT_TOP_WALL:
            _sound = self.ball_hit_top_wall
        elif _update_result == GAME_UPDATE_RESULT_BALL_HIT_BOTTOM_WALL:
            _sound = self.ball_hit_bottom_wall
        elif _update_result == GAME_UPDATE_RESULT_BALL_HIT_PADDLE_LEFT:
            _sound = self.get_ball_hit_paddle(_self_left)
        elif _update_result == GAME_UPDATE_RESULT_BALL_HIT_PADDLE_RIGHT:
            _sound = self.get_ball_hit_paddle(not _self_left)
        elif _update_result == GAME_UPDATE_RESULT_SCORE_UP_LEFT:
            _sound = self.get_score_up(_self_left)
        elif _update_result == GAME_UPDATE_RESULT_SCORE_UP_RIGHT:
            _sound = self.get_score_up(not _self_left)
        elif _update_result == GAME_UPDATE_RESULT_WON_LEFT:
            _sound = self.get_won(_self_left)
        elif _update_result == GAME_UPDATE_RESULT_WON_RIGHT:
            _sound = self.get_won(not _self_left)

        return _sound

    def consider_play_sound(self, _update_result: int, _self_left: bool) -> bool:
        _sound = self.get(_update_result=_update_result, _self_left=_self_left)
        return self.play_once(_sound)

    @property
    def button_hover(self) -> mixer.Sound:
        if not self._button_hover and is_file(FILE_PATH_SOUND_BUTTON_HOVER):
            self._button_hover = mixer.Sound(FILE_PATH_SOUND_BUTTON_HOVER)
        return self._button_hover

    def play_button_hover(self) -> bool:
        return self.play_once(self.button_hover)

    @property
    def button_click(self) -> mixer.Sound:
        if not self._button_click and is_file(FILE_PATH_SOUND_BUTTON_CLICK):
            self._button_click = mixer.Sound(FILE_PATH_SOUND_BUTTON_CLICK)
        return self._button_click

    def play_button_click(self) -> bool:
        return self.play_once(self.button_click)

    def play_button_sound(self, hover: bool) -> bool:
        return self.play_button_hover() if hover else self.play_button_click()


AUDIO: Audio = Audio()      # Singleton


# Fonts
FILE_PATH_FONT_PD_SANS = os.path.join(DIR_RES_FONT, 'product_sans_regular.ttf')
FILE_PATH_FONT_PD_SANS_MEDIUM = os.path.join(DIR_RES_FONT, 'product_sans_medium.ttf')
FILE_PATH_FONT_PD_SANS_LIGHT = os.path.join(DIR_RES_FONT, 'product_sans_light.ttf')
FILE_PATH_FONT_AQUIRE = os.path.join(DIR_RES_FONT, 'aquire.otf')
FILE_PATH_FONT_AQUIRE_LIGHT = os.path.join(DIR_RES_FONT, 'aquire_light.otf')
FILE_PATH_FONT_AQUIRE_BOLD = os.path.join(DIR_RES_FONT, 'aquire_bold.otf')
