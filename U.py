import math
import random
import re
import pygame

REL_VALUE_MULTIPLIER = 10_000
IP_ADDRESS_REGEX = r"^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
IP_ADDRESS_PATTERN = re.compile(IP_ADDRESS_REGEX)


def to_rel(abs_value: int) -> float:
    return abs_value / REL_VALUE_MULTIPLIER


def to_abs(rel_value: float) -> int:
    return int(rel_value * REL_VALUE_MULTIPLIER)


def is_valid_ip(ip: str):
    return ip and re.search(IP_ADDRESS_PATTERN, ip)


def get_user_name(default_user_name):
    try:
        import getpass
        user_name = getpass.getuser()
    except Exception:
        user_name = default_user_name

    return user_name


def signum(num) -> int:
    if num > 0:
        return 1
    if num < 0:
        return -1
    return 0


def remove_all_whitespaces(_str: str) -> str:
    return ''.join(_str.split())


def outside01(t) -> bool:
    return t < 0 or t > 1


def lerp(start, stop, amt):
    return start + ((stop - start) * amt)


def line_line_intersection(x1, y1, x2, y2, x3, y3, x4, y4, bound_line1: bool, bound_line2: bool) -> tuple:
    den = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))
    if den == 0:
        return None  # parallel

    t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / den
    if bound_line1 and outside01(t):
        return None  # intersection not within first line

    u = (((x1 - x3) * (y1 - y2)) - ((y1 - y3) * (x1 - x2))) / den
    if bound_line2 and outside01(u):
        return None  # intersection not within second line

    return t, u


def get_vel_max_total(vel_max_component: float) -> float:
    return 1.4143 * vel_max_component


# def get_ball_initial_rel_vel(rel_vel_max_component: float, _random: bool,
#                              component_vel_min_factor: float = 0.35, total_vel_min_factor: float = 0.9) -> tuple:
#     if _random:
#         _maxi = to_abs(rel_vel_max_component)
#         x_vel = to_rel(random.randint(-_maxi, _maxi))
#         y_vel = to_rel(random.randint(-_maxi, _maxi))
#
#         min_comp_vel = rel_vel_max_component * component_vel_min_factor
#         if x_vel >= min_comp_vel and y_vel >= min_comp_vel:
#             total_sq = (x_vel * x_vel) + (y_vel * y_vel)
#             min_total = rel_vel_max_component * total_vel_min_factor
#             if total_sq >= min_total * min_total:
#                 return x_vel, y_vel
#
#     return random.choice((1, -1)) * rel_vel_max_component, 0  # Right or left


def get_ball_initial_rel_vel(rel_vel_max_component: float, _random: bool,
                             x_vel_min_factor: float = 0.62,
                             total_vel_max_variance: float = 0.1) -> tuple:

    if not _random:
        return random.choice((1, -1)) * rel_vel_max_component, 0  # Right or left

    max_vel_sq = 2 * (rel_vel_max_component ** 2)
    vel_sq = max_vel_sq * random.uniform(1 - total_vel_max_variance, 1 + total_vel_max_variance)

    # decompose total_vel velocity into components
    vel_x_sq = vel_sq * random.uniform(x_vel_min_factor ** 2, 0.9)
    vel_y_sq = vel_sq - vel_x_sq

    return random.choice((1, -1)) * math.sqrt(vel_x_sq), random.choice((1, -1)) * math.sqrt(vel_y_sq)


def blit_text(surface: pygame.Surface, text: str, pos: tuple, font: pygame.font.Font, color=pygame.Color('black')) -> tuple:
    """
    Renders a multiple line text on the surface, wrapping it when necessary

    :return: (width, height) of whole rendered text on the given surface
    """

    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.

    space_width = font.size(' ')[0]  # The width of a space.
    font_height = font.get_height()
    font_linesize = font.get_linesize()

    max_width, max_height = surface.get_size()
    x, y = pos

    word_height = 0
    max_x2 = 0

    for line in words:
        for word in line:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height + font_linesize  # Start on new row.
                max_x2 = max(x, max_x2)
            else:
                max_x2 = max(x + word_width, max_x2)
            surface.blit(word_surface, (x, y))
            x += word_width + space_width
        x = pos[0]  # Reset the x.
        y += max(word_height, font_height) + font_linesize  # Start on new row.

    return max_x2 - pos[0], y - pos[1]