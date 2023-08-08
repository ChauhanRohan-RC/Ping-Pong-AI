from itertools import chain
from math import ceil
from functools import reduce

from Button import Button
from DifficultyLevel import DIFFICULTY_LEVEL_DEFAULT, DIFFICULTY_LEVELS, load_local_ai_efficiencies
from GameMode import *
from GameState import *
from U import is_valid_ip, blit_text
from pong_net_config import *
from pong_sessions import ClientSession

print("\n")


def create_fullscreen_display() -> pygame.Surface:
    _win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption(DISPLAY_TITLE)
    return _win


def create_non_fullscreen_display(_size: tuple) -> pygame.Surface:
    _win = pygame.display.set_mode(_size, pygame.RESIZABLE)
    pygame.display.set_caption(DISPLAY_TITLE)
    return _win


def update_exit_button_pos(button, win_width, win_height):
    button.x = win_width - button.width - CLIENT_HOME_SCREEN_PADX
    button.y = win_height - button.height - CLIENT_HOME_SCREEN_PADY


def create_exit_button(win_width, win_height):
    button_pad_x = 16
    button_pad_y = 10
    button_corner = 4

    _bt = Button(_id=ID_EXIT_BUTTON, text=EXIT_BUTTON_TEXT, x=0, y=0, pad_x=button_pad_x,
                 pad_y=button_pad_y, corner=button_corner,
                 bg=TINT_ENEMY_MEDIUM, bg_active=TINT_ENEMY_DARK,
                 font=FONT_BUTTONS_MEDIUM, text_color=FG_DARK, text_color_active=BG_DARK)

    update_exit_button_pos(_bt, win_width, win_height)
    return _bt


def update_difficulty_buttons_pos(buttons, win_width, win_height, max_b_height=0):
    _dx = ((win_width - (buttons[-1].x2 - buttons[0].x)) // 2) - buttons[0].x  # to center button horizontally

    if max_b_height <= 0:
        max_b_height = reduce(lambda a, b: a if a.height >= b.height else b, buttons).height

    for _bt in buttons:
        _bt.height = max_b_height
        _bt.y = win_height - max_b_height - CLIENT_HOME_SCREEN_PADY
        _bt.x += _dx


def create_difficulty_buttons(win_width, win_height) -> list:
    buttons = []
    button_pad_x = 16
    button_pad_y = 10
    button_corner = 4

    button_hgap = 28

    last_button_x2 = 0
    max_b_height = 0

    for d in DIFFICULTY_LEVELS:
        _bt = Button(_id=d.id, text=d.display_name, x=last_button_x2 + button_hgap, y=0, pad_x=button_pad_x,
                     pad_y=button_pad_y, corner=button_corner,
                     bg=BG_MEDIUM, bg_active=COLOR_HIGHLIGHT,
                     font=FONT_BUTTONS_MEDIUM, text_color=FG_MEDIUM, text_color_active=BG_DARK)

        _bt.tag = d

        buttons.append(_bt)
        last_button_x2 = _bt.x2
        max_b_height = max(max_b_height, _bt.height)

    update_difficulty_buttons_pos(buttons, win_width, win_height, max_b_height)
    return buttons


def update_game_mode_buttons_pos(buttons, win_width, win_height, vgap=20, max_b_width=0):
    if max_b_width <= 0:
        max_b_width = reduce(lambda a, b: a if a.width >= b.width else b, buttons).width

    last_button_y2 = win_height // 2
    for _bt in buttons:
        _bt.width = max_b_width
        _bt.x = (win_width - max_b_width) // 2
        _bt.y = last_button_y2 + vgap
        _bt.corner = ceil(_bt.height / 2.0)

        last_button_y2 = _bt.y2


def create_game_mode_buttons(win_width, win_height) -> list:
    buttons = []
    button_pad_x = 20
    button_pad_y = 12

    max_b_w = 0

    for _mode in GAME_MODES:
        _bt = Button(_id=_mode.id, text=_mode.display_name, x=0, y=0, pad_x=button_pad_x,
                     pad_y=button_pad_y, corner=0,
                     bg=BG_MEDIUM, bg_active=COLOR_HIGHLIGHT,
                     font=FONT_BUTTONS, text_color=FG_MEDIUM, text_color_active=BG_DARK)

        _bt.tag = _mode

        buttons.append(_bt)
        max_b_w = max(max_b_w, _bt.width)

    update_game_mode_buttons_pos(buttons, win_width, win_height, max_b_width=max_b_w)
    return buttons


def create_sound_buttons():
    # label = FONT_BUTTONS_SMALL.render(LABEL_TEXT_SOUND, True, FG_DARK)

    button_pad_x = 5
    button_pad_y = 7
    button_corner = 6

    bt_on = Button(_id=ID_SOUND_ON_BUTTON, text=SWITCH_TEXT_SOUND_ON, x=0, y=0,
                   pad_x=button_pad_x,
                   pad_y=button_pad_y, corner=button_corner,
                   bg=BG_MEDIUM, bg_active=COLOR_HIGHLIGHT,
                   font=FONT_BUTTONS_SMALL, text_color=FG_MEDIUM, text_color_active=BG_DARK)

    bt_on.tag = True

    bt_off = Button(_id=ID_SOUND_OFF_BUTTON, text=SWITCH_TEXT_SOUND_OFF, x=0, y=0,
                    pad_x=button_pad_x,
                    pad_y=button_pad_y, corner=button_corner,
                    bg=BG_MEDIUM, bg_active=TINT_ENEMY_DARK,
                    font=FONT_BUTTONS_SMALL, text_color=FG_MEDIUM, text_color_active=BG_DARK)

    bt_off.tag = False

    max_b_width = max(bt_on.width, bt_off.width)
    max_b_height = max(bt_on.height, bt_off.height)
    bt_on.width = bt_off.width = max_b_width
    bt_on.height = bt_off.height = max_b_height

    return bt_on, bt_off


def update_sound_buttons_pos(buttons, sound_label_pos, sound_label_size):
    button_hgap = 10
    max_b_h = buttons[0].height

    x = sound_label_pos[0] + sound_label_size[0] + 16
    y = sound_label_pos[1] + (sound_label_size[1] - max_b_h) // 2

    for b in buttons:
        b.x = x
        b.y = y
        x = b.x2 + button_hgap


pygame.mixer.init()
pygame.init()

window_icon = IMAGES.window_icon
if window_icon:
    pygame.display.set_icon(window_icon)

if DEFAULT_FULLSCREEN:
    win = create_fullscreen_display()
else:
    win = create_non_fullscreen_display((DEFAULT_W_WIDTH, DEFAULT_W_HEIGHT))

clock = pygame.time.Clock()  # Main loop clock
# db_clock = pygame.time.Clock()  # double click timer clock

pygame.font.init()
FONT_TITLE = pygame.font.Font(FILE_PATH_FONT_AQUIRE, 60)
FONT_SUMMARY = pygame.font.Font(FILE_PATH_FONT_PD_SANS_LIGHT, 19)
FONT_STATUS = pygame.font.Font(FILE_PATH_FONT_PD_SANS_LIGHT, 14)
FONT_STATUS_PLAYER = pygame.font.Font(FILE_PATH_FONT_PD_SANS, 16)
FONT_BUTTONS = pygame.font.Font(FILE_PATH_FONT_AQUIRE, 18)
FONT_BUTTONS_MEDIUM = pygame.font.Font(FILE_PATH_FONT_AQUIRE, 14)
FONT_BUTTONS_SMALL = pygame.font.Font(FILE_PATH_FONT_PD_SANS, 13)

FONT_SCORE = pygame.font.Font(FILE_PATH_FONT_AQUIRE, 34)
FONT_WON_MSG = pygame.font.Font(FILE_PATH_FONT_PD_SANS_MEDIUM, 42)
FONT_CRITICAL_MSG = pygame.font.Font(FILE_PATH_FONT_PD_SANS, 42)
FONT_MSG_CAPTION = pygame.font.Font(FILE_PATH_FONT_PD_SANS_LIGHT, 18)


def get_win():
    global win

    return win


def _draw_home_screen(_win, _session: ClientSession, _buttons):
    global home_sound_buttons_pos_pending

    _win.fill(BG_DARK)

    _bg = IMAGES.home_bg
    if _bg:
        o_asp = _bg.get_width() / _bg.get_height()
        d_asp = _win.get_width() / _win.get_height()
        if o_asp < d_asp:
            nw = _win.get_width()
            nh = int(nw / o_asp)
        else:
            nh = _win.get_height()
            nw = int(o_asp * nh)

        _bg = pygame.transform.scale(_bg, (nw, nh))
        _win.blit(_bg, ((_win.get_width() - nw) // 2, (_win.get_height() - nh) // 2))

    # Title
    title_part1 = FONT_TITLE.render(DISPLAY_TITLE_PART1 + ' ', True, COLOR_HOME_TITLE_PART1)
    title_part2 = FONT_TITLE.render(' ' + DISPLAY_TITLE_PART2, True, COLOR_HOME_TITLE_PART2)
    title_y = (_win.get_height() - title_part1.get_height()) // 3

    _win.blit(title_part1, (_win.get_width() // 2 - title_part1.get_width(), title_y))
    _win.blit(title_part2, (_win.get_width() // 2, title_y))

    summary = FONT_SUMMARY.render(DISPLAY_SUMMARY, True, COLOR_HOME_SUMMARY)
    _win.blit(summary, ((_win.get_width() - summary.get_width()) // 2, title_y + title_part1.get_height() + 10))

    _player = FONT_SUMMARY.render(format_player_name(_session.player_name if _session else player_name), True, FG_DARK)
    _win.blit(_player, (_win.get_width() - _player.get_width() - CLIENT_HOME_SCREEN_PADX, CLIENT_HOME_SCREEN_PADY))

    _sound_label = FONT_BUTTONS_SMALL.render(LABEL_TEXT_SOUND, True, FG_DARK)
    _sound_label_pos = (CLIENT_HOME_SCREEN_PADX_SOUND_LABEL, CLIENT_HOME_SCREEN_PADY_SOUND_LABEL)

    if home_sound_buttons_pos_pending:
        update_sound_buttons_pos(home_sound_buttons, _sound_label_pos, _sound_label.get_size())
        home_sound_buttons_pos_pending = False

    # pygame.draw.rect(_win, BG_LIGHT, (
    # 10, 10, home_sound_buttons[1].x2 + 10, _sound_label.get_height() + _sound_label_pos[1]),
    #                  border_radius=10)

    _win.blit(_sound_label, _sound_label_pos)

    # Controls Description
    _controls_title = FONT_BUTTONS_SMALL.render(TITLE_CONTROLS, True, COLOR_HIGHLIGHT)
    _controls_title_pos = (CLIENT_HOME_SCREEN_PADX, _sound_label_pos[1] * 2 + _sound_label.get_height())
    _win.blit(_controls_title, _controls_title_pos)
    blit_text(_win, DES_CONTROLS, (_controls_title_pos[0], _controls_title_pos[1] + _controls_title.get_height() + 12),
              FONT_BUTTONS_SMALL, color=FG_DARK)

    for _b in _buttons:
        _b.draw(_win)


def draw(_win, _session: ClientSession, _paused: bool, _home_buttons):
    if not _session or _session.is_idle:
        _draw_home_screen(_win, _session, _home_buttons)
    else:
        _win.fill(BG_DARK)

        # status
        _status_text = _session.game_mode.short_name + \
                       (
                           f"{STATUS_TEXT_DELIMITER}{_session.difficulty.display_name} ({STATUS_TEXT_WINNING_SCORE}: {_session.difficulty.winning_score})" if _session.difficulty else "") + \
                       (STATUS_TEXT_DELIMITER + (
                           STATUS_TEXT_SOUND_ON if _session.sounds_enabled else STATUS_TEXT_SOUND_OFF))

        _status = FONT_STATUS.render(_status_text, True, COLOR_STATUS_TEXT)
        _win.blit(_status, (_win.get_width() - _status.get_width() - 6, _win.get_height() - _status.get_height() - 4))

        if _session.is_connecting or _session.is_waiting or _session.has_enemy_left:
            if _session.is_connecting:
                msg_text = MSG_SESSION_CONNECTING
                cap_text = f"{format_server_addr(*_session.server_addr)} | {MSG_CONNECTING_CAPTION}"
            elif _session.is_waiting:
                msg_text = MSG_SESSION_WAITING
                cap_text = f"{format_server_addr(*_session.server_addr)} | {MSG_WAITING_CAPTION}"
            else:
                msg_text = get_msg_enemy_left(_session.other_player_name)
                cap_text = MSG_ENEMY_LEFT_CAPTION

            msg = FONT_CRITICAL_MSG.render(msg_text, True, FG_DARK)
            cap = FONT_MSG_CAPTION.render(cap_text, True, FG_MEDIUM)
            _win.blit(msg, ((_win.get_width() - msg.get_width()) // 2, (_win.get_height() - msg.get_height()) // 2))
            _win.blit(cap,
                      ((_win.get_width() - cap.get_width()) // 2, (_win.get_height() + msg.get_height()) // 2 + 10))

            right_player_name = FONT_SUMMARY.render(
                format_player_name(_session.player_name if _session else player_name), True, FG_DARK)
            _win.blit(right_player_name, (
                _win.get_width() - right_player_name.get_width() - CLIENT_HOME_SCREEN_PADX, CLIENT_HOME_SCREEN_PADY))
        elif _session.is_running:
            state = _session.game_state
            assert state is not None, "Running session has no GameState !!"

            self_left = _session.is_self_left

            if state.any_won():
                self_won = state.is_won(self_left)
                won_text, won_cap_text, won_col = _session.game_mode.get_won_display_info(self_won=self_won,
                                                                                          score_diff=state.score_difference,
                                                                                          enemy_name=_session.other_player_name)

                won_img = FONT_WON_MSG.render(won_text, True, won_col)
                won_cap = FONT_MSG_CAPTION.render(won_cap_text, True, FG_MEDIUM)

                _win.blit(won_img, (
                    (_win.get_width() - won_img.get_width()) // 2, (_win.get_height() - won_img.get_height()) // 2))
                _win.blit(won_cap, (
                    (_win.get_width() - won_cap.get_width()) // 2,
                    (_win.get_height() + won_img.get_height()) // 2 + 10))
            else:
                div_h = int(_win.get_height() * VERTICAL_DIVIDER_REL_HEIGHT)
                for i in range(_win.get_height() - 16 // div_h):
                    if i % 2 == 1:
                        continue

                    pygame.draw.rect(_win, COLOR_VERTICAL_DIVIDER, (
                        (_win.get_width() - VERTICAL_DIVIDER_WIDTH) // 2, i * div_h, VERTICAL_DIVIDER_WIDTH, div_h),
                                     border_radius=VERTICAL_DIVIDER_CORNERS)

                score_text_left = FONT_SCORE.render(str(state.score_left), True,
                                                    COLOR_SCORE_SELF if self_left else COLOR_SCORE_ENEMY)
                score_text_right = FONT_SCORE.render(str(state.score_right), True,
                                                     COLOR_SCORE_SELF if not self_left else COLOR_SCORE_ENEMY)

                _win.blit(score_text_left, (
                    _win.get_width() // 4 - score_text_left.get_width() // 2,
                    _win.get_height() - score_text_left.get_height() - 24))
                _win.blit(score_text_right, (
                    _win.get_width() * (3 / 4) - score_text_right.get_width() // 2,
                    _win.get_height() - score_text_right.get_height() - 24))

                if _session.game_mode == GAME_MODE_ONLINE_MULTI_PLAYER:
                    _self_name = get_self_name_status(_session.player_name)
                    _enemy_name = get_enemy_name_status(_session.other_player_name)
                elif _session.game_mode == GAME_MODE_OFFLINE_SINGLE_PLAYER:
                    _self_name = get_self_name_status(_session.player_name)
                    _enemy_name = get_ai_name_status(_session.difficulty.ai_efficiency_percent)
                else:
                    _self_name = OFFLINE_MULTI_PLAYER_PLAYER1_NAME
                    _enemy_name = OFFLINE_MULTI_PLAYER_PLAYER2_NAME

                if self_left:
                    left_name = _self_name
                    right_name = _enemy_name
                else:
                    left_name = _enemy_name
                    right_name = _self_name

                if left_name:
                    left_img = FONT_STATUS_PLAYER.render(left_name, True, COLOR_PLAYER_STATUS_TEXT)
                    _win.blit(left_img, (_win.get_width() // 4 - left_img.get_width() // 2, CLIENT_HOME_SCREEN_PADY))

                if right_name:
                    right_img = FONT_STATUS_PLAYER.render(right_name, True, COLOR_PLAYER_STATUS_TEXT)
                    _win.blit(right_img,
                              ((_win.get_width() * 3) // 4 - right_img.get_width() // 2, CLIENT_HOME_SCREEN_PADY))

                state.paddle_left.draw()
                state.paddle_right.draw()
                state.ball.draw()

                if _paused and not _session.game_mode.online:
                    overlay = pygame.Surface((_win.get_width(), _win.get_height()))
                    overlay.fill(COLOR_TRANSLUCENT)
                    overlay.set_alpha(COLOR_TRANSLUCENT.a)
                    _win.blit(overlay, (0, 0))
                    # pygame.draw.rect(_win, (0, 0, 0, 0), (0, 0, _win.get_width(), _win.get_height()))  # overlay

                    p_msg = FONT_CRITICAL_MSG.render(MSG_PAUSED, True, TINT_ENEMY_MEDIUM)
                    p_msg_pos = (
                        (_win.get_width() - p_msg.get_width()) // 2, (_win.get_height() - p_msg.get_height()) // 2)
                    p_cap = FONT_MSG_CAPTION.render(MSG_PAUSED_CAPTION, True, FG_DARK)
                    p_cap_pos = (
                        (_win.get_width() - p_cap.get_width()) // 2,
                        ((_win.get_height() + p_msg.get_height()) // 2) + 8)
                    _win.blit(p_msg, p_msg_pos)
                    _win.blit(p_cap, p_cap_pos)

                    # Controls Description
                    _controls_title = FONT_BUTTONS_SMALL.render(TITLE_CONTROLS, True, COLOR_HIGHLIGHT)
                    # _controls_title_pos = (p_msg_pos[0], p_cap_pos[1] + p_cap.get_height() + 20)
                    _controls_title_pos = (CLIENT_HOME_SCREEN_PADX, CLIENT_HOME_SCREEN_PADY)
                    _controls_des_pos = (
                        _controls_title_pos[0], _controls_title_pos[1] + _controls_title.get_height() + 12)

                    _win.blit(_controls_title, _controls_title_pos)
                    blit_text(_win, DES_CONTROLS, _controls_des_pos, FONT_BUTTONS_SMALL, color=FG_DARK)

        else:
            print("Invalid Session state")

    pygame.display.update()


# player_name
player_name = CONFIG.get_client_local_config_player_name()

# Server
server_ip = DEFAULT_SERVER_IP
server_port = DEFAULT_SERVER_PORT
__loaded_server_addr = load_server_addr(default_ip=DEFAULT_SERVER_IP, default_port=DEFAULT_SERVER_PORT)
__ip_from_argv = False
__port_from_argv = False

if len(sys.argv) > 1:
    _ip = sys.argv[1]
    if is_valid_ip(_ip):
        server_ip = _ip
        __ip_from_argv = True
    else:
        print(f"Invalid input IP Address: {_ip}")

if len(sys.argv) > 2:
    try:
        server_port = int(sys.argv[2])
        __port_from_argv = True
    except ValueError:
        print("Invalid input port: " + sys.argv[2])

if not __ip_from_argv:
    server_ip = __loaded_server_addr[0]

if not __port_from_argv:
    server_port = __loaded_server_addr[1]

server_addr = (server_ip, server_port)

# Main Loop
load_local_ai_efficiencies()
home_selected_difficulty: DifficultyLevel = DIFFICULTY_LEVEL_DEFAULT
home_selected_sound_enabled: bool = CLIENT_DEFAULT_SOUNDS_ENABLED
session: ClientSession = None

home_game_mode_buttons = create_game_mode_buttons(win.get_width(), win.get_height())
home_difficulty_buttons = create_difficulty_buttons(win.get_width(), win.get_height())
home_sound_buttons = create_sound_buttons()
home_exit_button = create_exit_button(win.get_width(), win.get_height())

run = True
paused = False
home_sound_buttons_pos_pending = True

_display_updated = False
_last_focused_button: Button = None
_last_win_size = None


def is_fullsreen() -> bool:
    return (win.get_flags() & pygame.FULLSCREEN) != 0


def __set_fullscreen(fullscreen: bool):
    global win
    global _last_win_size
    global _display_updated

    if fullscreen:
        if not is_fullsreen():
            _last_win_size = win.get_size()
        else:
            _last_win_size = None

        pygame.display.quit()
        pygame.display.init()
        win = create_fullscreen_display()
    else:
        _size = _last_win_size if _last_win_size else (DEFAULT_W_WIDTH, DEFAULT_W_HEIGHT)
        pygame.display.quit()
        pygame.display.init()
        win = create_non_fullscreen_display(_size)

    _display_updated = True


def set_fullsreen(fullscreen: bool):
    if is_fullsreen() == fullscreen:
        return
    __set_fullscreen(fullscreen)


def toggle_fullscreen() -> bool:
    fs = not is_fullsreen()
    __set_fullscreen(fs)
    return fs
    # pygame.display.toggle_fullscreen()
    # return True


def consider_play_button_sound(hover: bool):
    if home_selected_sound_enabled:
        AUDIO.play_button_sound(hover)


def get_all_home_buttons():
    return chain(home_game_mode_buttons, home_difficulty_buttons, home_sound_buttons, (home_exit_button,))


def sync_home_sound_buttons_state():
    for _bt in home_sound_buttons:
        _bt.active = _bt.tag == home_selected_sound_enabled


def sync_home_difficulty_buttons_state():
    for _bt in home_difficulty_buttons:
        _bt.active = _bt.id == home_selected_difficulty.id


def sync_all_home_buttons_state(_event=None):
    global _last_focused_button

    m_pos = _event.pos if _event else pygame.mouse.get_pos()
    focused_bt = None

    for _bt in get_all_home_buttons():
        _focus = _bt.is_over(*m_pos)
        _bt.active = _focus or (home_selected_difficulty and _bt.id == home_selected_difficulty.id) \
                     or _bt.id == (ID_SOUND_ON_BUTTON if home_selected_sound_enabled else ID_SOUND_OFF_BUTTON)

        if _focus:
            focused_bt = _bt

    if focused_bt:
        if not _last_focused_button or _last_focused_button != focused_bt:
            _last_focused_button = focused_bt
            consider_play_button_sound(hover=True)
    else:
        _last_focused_button = None


def go_back():
    global run
    global paused
    global session
    global _display_updated

    if not session or session.is_idle:
        run = False
    else:
        session.set_idle()
        consider_play_button_sound(False)
        paused = False
        _display_updated = True


def handle_keydown(_event):
    global run
    global paused
    global session
    global home_selected_sound_enabled
    global _display_updated

    if _event.key == pygame.K_ESCAPE:
        go_back()
    elif _event.key == pygame.K_RETURN:
        if session and (
                session.has_enemy_left or (session.is_running and session.game_state and session.game_state.any_won())):
            session.set_idle()
            consider_play_button_sound(False)
            paused = False
            _display_updated = True
    elif _event.key == pygame.K_a:
        if pygame.key.get_mods() & pygame.KMOD_CTRL:  # if ctrl pressed
            home_selected_sound_enabled = not home_selected_sound_enabled
            if session:
                session.sounds_enabled = home_selected_sound_enabled
            sync_home_sound_buttons_state()
    elif _event.key == pygame.K_SPACE:
        if session and session.is_running and not session.game_mode.online:
            paused = not paused
    elif _event.key == pygame.K_f:
        if pygame.key.get_mods() & pygame.KMOD_CTRL:  # if ctrl pressed
            toggle_fullscreen()


def handle_mouse_motion(_event=None):
    global session

    if not session or session.is_idle:
        sync_all_home_buttons_state(event)


# def on_double_left_click(_event) -> bool:
#     toggle_fullscreen()
#     return True     # handled


def handle_mouse_button_down(_event=None):
    global session
    global player_name
    global paused
    global home_selected_difficulty
    global home_selected_sound_enabled
    global home_exit_button

    # if _event and _event.button == pygame.BUTTON_LEFT:
    #     print("left click")
    #     if db_clock.tick() < DOUBLE_CLICK_MS:
    #         print("Double Left click")
    #         handled = on_double_left_click(_event)
    #         if handled:
    #             return

    if not session or session.is_idle:
        m_pos = _event.pos if _event else pygame.mouse.get_pos()

        if home_exit_button.is_over(*m_pos):
            go_back()
            return

        _got_diff = False
        _got_sound = False
        _got_game_mode = False
        for bt in home_difficulty_buttons:
            if bt.is_over(*m_pos):
                home_selected_difficulty = bt.tag
                _got_diff = True
                break

        if _got_diff:
            sync_home_difficulty_buttons_state()
        else:
            for bt in home_sound_buttons:
                if bt.is_over(*m_pos):
                    home_selected_sound_enabled = bt.tag
                    _got_sound = True
                    break

            if _got_sound:
                sync_home_sound_buttons_state()
            elif home_selected_difficulty:
                for bt in home_game_mode_buttons:
                    if bt.is_over(*m_pos):
                        if session:
                            session.log_out()
                        paused = False
                        session = ClientSession(win_getter=get_win, game_mode=bt.tag, server_addr=server_addr,
                                                player_name=player_name, sounds_enabled=home_selected_sound_enabled)
                        session.req_new_session(difficulty=home_selected_difficulty)
                        _got_game_mode = True
                        break

        if _got_diff or _got_sound or _got_game_mode:
            consider_play_button_sound(hover=False)


def handle_videoresize(_event=None):
    global session

    if not session or session.is_idle:
        size = _event.size if _event and hasattr(_event, 'size') else win.get_size()
        update_game_mode_buttons_pos(home_game_mode_buttons, size[0], size[1])
        update_difficulty_buttons_pos(home_difficulty_buttons, size[0], size[1])
        update_exit_button_pos(home_exit_button, size[0], size[1])


while run:
    clock.tick(FPS_CLIENT)
    draw(win, session, paused, get_all_home_buttons())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        elif event.type == pygame.KEYDOWN:
            handle_keydown(event)
        elif event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_button_down(event)
        elif event.type == pygame.VIDEORESIZE:
            handle_videoresize(event)

    if not run:
        break

    if _display_updated:
        handle_videoresize()
        _display_updated = False

    if not session or session.is_idle:  # Home Screen
        pass
    elif session.is_running and session.game_state and not session.game_state.any_won():
        if session.game_mode.online or not paused:
            keys = pygame.key.get_pressed()
            session.update_game(keys)

if session:
    session.log_out()
pygame.quit()
sys.exit(2)
