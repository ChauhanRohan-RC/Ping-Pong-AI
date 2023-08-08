import random
import pygame
import math

import U
from R import *
from U import lerp, line_line_intersection, get_ball_initial_rel_vel, to_rel, to_abs
from DifficultyLevel import DifficultyLevel


class BaseGameObject:

    def __init__(self, win_getter, relx: float, rely: float):
        self._win_getter = win_getter
        self._relx = self.original_relx = relx
        self._rely = self.original_rely = rely

    @property
    def win(self):
        return self._win_getter()

    @property
    def win_width(self) -> int:
        return self.win.get_width()

    @property
    def win_height(self) -> int:
        return self.win.get_height()

    def get_relx(self, x: int) -> float:
        return x / self.win_width

    def get_rely(self, y: int) -> float:
        return y / self.win_height

    def get_absx(self, relx: float) -> int:
        return int(relx * self.win_width)

    def get_absy(self, rely: float) -> int:
        return int(rely * self.win_height)

    @property
    def relx(self) -> float:
        return self._relx

    @relx.setter
    def relx(self, value: float):
        self._relx = value

    @property
    def x(self) -> int:
        return self.get_absx(self._relx)

    @x.setter
    def x(self, value: int):
        self._relx = self.get_relx(value)

    @property
    def rely(self) -> float:
        return self._rely

    @rely.setter
    def rely(self, value: float):
        self._rely = value

    @property
    def y(self) -> int:
        return self.get_absy(self._rely)

    @y.setter
    def y(self, value: int):
        self._rely = self.get_rely(value)

    def reset(self):
        self.relx = self.original_relx
        self.rely = self.original_rely


class Paddle(BaseGameObject):
    # _s_left = None
    # _s_right = None

    @classmethod
    def create_left(cls, win_getter, difficulty: DifficultyLevel, is_self: bool):
        return cls(win_getter=win_getter, relx=PADDLE_REL_PAD_X, rely=(1 - difficulty.paddle_rel_height) / 2,
                   rel_width=difficulty.paddle_rel_width, rel_height=difficulty.paddle_rel_height,
                   rel_vel=difficulty.paddle_rel_vel, color=COLOR_PADDLE_SELF if is_self else COLOR_PADDLE_ENEMY)

    @classmethod
    def create_right(cls, win_getter, difficulty: DifficultyLevel, is_self: bool):
        return cls(win_getter=win_getter, relx=1 - difficulty.paddle_rel_width - PADDLE_REL_PAD_X,
                   rely=(1 - difficulty.paddle_rel_height) / 2,
                   rel_width=difficulty.paddle_rel_width, rel_height=difficulty.paddle_rel_height,
                   rel_vel=difficulty.paddle_rel_vel, color=COLOR_PADDLE_SELF if is_self else COLOR_PADDLE_ENEMY)

    # @classmethod
    # def left_singleton(cls):
    #     ins = cls._s_left
    #     if not ins:
    #         ins = cls.create_left(False)
    #         cls._s_left = ins
    #     return ins
    #
    # @classmethod
    # def right_singleton(cls):
    #     ins = cls._s_right
    #     if not ins:
    #         ins = cls.create_right(True)
    #         cls._s_right = ins
    #     return ins

    def __init__(self, win_getter,
                 relx: float, rely: float,
                 rel_width: float, rel_height: float,
                 rel_vel: float, color: pygame.Color = FG_DARK
                 # , rel_padx: int = PADDLE_REL_PAD_X, rel_pady: int = PADDLE_REL_PAD_Y
                 ):

        super(Paddle, self).__init__(win_getter, relx, rely)
        self._rel_width = rel_width
        self._rel_height = rel_height
        self._rel_vel = rel_vel
        self.color = color

        # self.abs_padx = abs_padx
        # self.abs_pady = abs_pady

    @property
    def rel_vel(self):
        return self._rel_vel

    @property
    def rel_width(self) -> float:
        return self._rel_width

    @rel_width.setter
    def rel_width(self, value: float):
        self._rel_width = value

    @property
    def width(self) -> int:
        return self.get_absx(self._rel_width)

    @width.setter
    def width(self, value: int):
        self._rel_width = self.get_relx(value)

    @property
    def relx2(self) -> float:
        return self.relx + self._rel_width

    @relx2.setter
    def relx2(self, value: float):
        self.relx = value - self._rel_width

    @property
    def x2(self) -> int:
        return self.get_absx(self.relx2)

    @x2.setter
    def x2(self, value: int):
        self.relx2 = self.get_relx(value)

    @property
    def rel_height(self) -> float:
        return self._rel_height

    @rel_height.setter
    def rel_height(self, value: float):
        self._rel_height = value

    @property
    def height(self) -> int:
        return self.get_absy(self._rel_height)

    @height.setter
    def height(self, value: int):
        self._rel_height = self.get_rely(value)

    @property
    def rely2(self) -> float:
        return self.rely + self._rel_height

    @rely2.setter
    def rely2(self, value: float):
        self.rely = value - self._rel_height

    @property
    def y2(self) -> int:
        return self.get_absy(self.rely2)

    @y2.setter
    def y2(self, value: int):
        self.rely2 = self.get_rely(value)

    def check_rel_collision(self, relx: float, rely: float) -> bool:
        return self.relx <= relx <= self.relx2 and self.rely <= rely <= self.rely2

    def check_rel_collisions(self, *rel_points) -> bool:
        for pt in rel_points:
            if self.check_rel_collision(*pt):
                return True

        return False

    def draw(self):
        pygame.draw.rect(self.win, self.color, (self.x, self.y, self.width, self.height), border_radius=PADDLE_CORNERS)

    def rely_max(self, rel_pady=PADDLE_REL_PAD_Y) -> float:
        return 1 - self.rel_height - rel_pady

    @staticmethod
    def rely_min(rel_pady=PADDLE_REL_PAD_Y) -> float:
        return rel_pady

    @property
    def center_relx(self) -> float:
        return self.relx + (self.rel_width / 2)

    @property
    def center_rely(self) -> float:
        return self.rely + (self.rel_height / 2)

    @property
    def center_absx(self) -> float:
        return self.get_absx(self.center_relx)

    @property
    def center_absy(self) -> float:
        return self.get_absy(self.center_rely)

    def set_raw_rel_pos(self, relx, rely):
        self.relx, self.rely = relx, rely

    def move_to_rel(self, rely, rel_pady=PADDLE_REL_PAD_Y):
        self.rely = max(self.rely_min(rel_pady), min(self.rely_max(rel_pady), rely))

    def move_by_rel(self, rel_dy, rel_pady=PADDLE_REL_PAD_Y):
        self.move_by_rel(self.rely + rel_dy, rel_pady=rel_pady)

    def move(self, up=True, rel_pady=PADDLE_REL_PAD_Y):
        if up:
            _final = self.rely - self._rel_vel
            _min = self.rely_min(rel_pady=rel_pady)
            self.rely = max(_min, _final)
        else:
            _final = self.rely + self._rel_vel
            _max = self.rely_max(rel_pady=rel_pady)
            self.rely = min(_max, _final)

        # self.move_by((-1 if up else 1) * self.vel)

    def reset(self):
        super(Paddle, self).reset()


class Ball(BaseGameObject):

    # _s_ins = None

    # @classmethod
    # def singleton(cls):
    #     ins = cls._s_ins
    #     if not ins:
    #         ins = Ball()
    #         cls._s_ins = ins
    #     return ins

    @classmethod
    def create(cls, win_getter, difficulty: DifficultyLevel):
        return cls(win_getter=win_getter, relx=0.5, rely=0.5,
                   rel_radius=difficulty.ball_rel_radius,
                   rel_vel_max_component=difficulty.ball_rel_vel_max_component,
                   x_vel_min_factor=difficulty.ball_x_vel_min_factor,
                   random_initial_vel_enabled=difficulty.ball_random_initial_vel_enabled)

    def __init__(self, win_getter, relx: float = 0.5, rely: float = 0.5,
                 rel_radius: float = BALL_DEFAULT_REL_RADIUS,
                 rel_vel_max_component: float = BALL_DEFAULT_REL_VEl_MAX_COMPONENT,
                 x_vel_min_factor: float = BALL_DEFAULT_REL_VEl_MIN_COMPONENT_FACTOR,
                 random_initial_vel_enabled: bool = BALL_DEFAULT_RANDOM_INITIAL_VEL_ENABLED,
                 color: pygame.Color = COLOR_BALL):
        super(Ball, self).__init__(win_getter, relx, rely)
        self.rel_radius = rel_radius
        self.color = color

        self.rel_vel_max_component = rel_vel_max_component
        self.x_vel_min_factor = x_vel_min_factor
        self.random_initial_vel_enabled = random_initial_vel_enabled
        self.rel_velx, self.rel_vely = 0, 0
        self.reset_vel()

    @property
    def radius(self):
        return min(self.win_width, self.win_height) * self.rel_radius

    @property
    def abs_velx(self) -> int:
        return self.get_absx(self.rel_velx)

    @property
    def abs_vely(self) -> int:
        return self.get_absy(self.rel_vely)

    def draw(self):
        pygame.draw.circle(self.win, self.color, (self.x, self.y), self.radius)

    def move_to_rel(self, relx, rely):
        self.relx, self.rely = relx, rely

    def move_by_rel(self, rel_dx, rel_dy):
        self.relx += rel_dx
        self.rely += rel_dy

    def move(self):
        self.move_by_rel(self.rel_velx, self.rel_vely)

    def reset_vel(self):
        self.rel_velx, self.rel_vely = get_ball_initial_rel_vel(rel_vel_max_component=self.rel_vel_max_component,
                                                                _random=self.random_initial_vel_enabled,
                                                                x_vel_min_factor=self.x_vel_min_factor)

    def reset(self):
        super(Ball, self).reset()
        self.reset_vel()

    @property
    def center_left_rel(self) -> tuple:
        return self.relx - self.rel_radius, self.rely

    @property
    def center_right_rel(self) -> tuple:
        return self.relx + self.rel_radius, self.rely

    @property
    def center_top_rel(self) -> tuple:
        return self.relx, self.rely - self.rel_radius

    @property
    def center_bottom_rel(self) -> tuple:
        return self.relx, self.rely + self.rel_radius

    #     # todo: acceleration
    #
    # def accelerate(self):
    #     self.x_vel += (signum(self.x_vel)) * 1          # acceleration
    #     self.y_vel += (signum(self.y_vel)) * 1          # acceleration

    def collide(self, left_paddle: Paddle, right_paddle: Paddle, rel_pady=0) -> int:
        result = GAME_UPDATE_RESULT_NORMAL

        if self.rely + self.rel_radius >= 1 - rel_pady:  # Hit Bottom Wall
            self.rel_vely *= -1
            result = GAME_UPDATE_RESULT_BALL_HIT_BOTTOM_WALL
        elif self.rely - self.rel_radius <= rel_pady:  # Hit Top Wall
            self.rel_vely *= -1
            result = GAME_UPDATE_RESULT_BALL_HIT_TOP_WALL

        paddle = None
        if self.rel_velx < 0:  # Hit LEFT Paddle
            if left_paddle.check_rel_collisions(self.center_left_rel, self.center_top_rel, self.center_bottom_rel):
                paddle = left_paddle
                result = GAME_UPDATE_RESULT_BALL_HIT_PADDLE_LEFT
        elif self.rel_velx > 0:  # Hit Right Paddle
            if right_paddle.check_rel_collisions(self.center_right_rel, self.center_top_rel, self.center_bottom_rel):
                paddle = right_paddle
                result = GAME_UPDATE_RESULT_BALL_HIT_PADDLE_RIGHT

        if paddle:
            self.rel_velx *= -1

            # parenthesis expression is in range [-1, 1]
            rel_y_vel = (((paddle.center_rely - self.rely) * 2) / paddle.rel_height) * self.rel_vel_max_component
            self.rel_vely = -rel_y_vel

        return result

    @property
    def heading_rad(self) -> float:
        return math.atan2(self.rel_vely, self.rel_velx)

    @property
    def heading_deg(self):
        return math.degrees(self.heading_rad)


class GameState:

    @classmethod
    def create_server(cls, win_getter, difficulty: DifficultyLevel):
        return cls(difficulty,
                   Paddle.create_left(win_getter=win_getter, difficulty=difficulty, is_self=False),
                   Paddle.create_right(win_getter=win_getter, difficulty=difficulty, is_self=True),
                   Ball.create(win_getter=win_getter, difficulty=difficulty))  # colors don't matter in server

    @classmethod
    def create_client(cls, win_getter, difficulty: DifficultyLevel, self_left: bool):
        return cls(difficulty,
                   Paddle.create_left(win_getter=win_getter, difficulty=difficulty, is_self=self_left),
                   Paddle.create_right(win_getter=win_getter, difficulty=difficulty, is_self=not self_left),
                   Ball.create(win_getter=win_getter, difficulty=difficulty))

    def __init__(self, difficulty: DifficultyLevel, paddle_left: Paddle, paddle_right: Paddle, ball: Ball,
                 score_left: int = 0, score_right: int = 0):
        self.difficulty = difficulty
        self.paddle_left = paddle_left
        self.paddle_right = paddle_right
        self.ball = ball
        self.score_left = score_left
        self.score_right = score_right

    @property
    def winning_score(self):
        return self.difficulty.winning_score

    def get_paddle(self, left: bool):
        return self.paddle_left if left else self.paddle_right

    def dump_paddle_coords(self, left: bool) -> str:
        paddle = self.get_paddle(left)
        return f"{to_abs(paddle.relx)}{GAME_STATE_DELIMITER1}{to_abs(paddle.rely)}"

    def load_paddle_coords(self, s: str, left: bool):
        d = s.split(GAME_STATE_DELIMITER1)
        p = self.get_paddle(left)
        p.set_raw_rel_pos(to_rel(int(d[0])), to_rel(int(d[1])))

    def dump_ball_coords(self):
        return f"{to_abs(self.ball.relx)}{GAME_STATE_DELIMITER1}{to_abs(self.ball.rely)}{GAME_STATE_DELIMITER1}" \
               f"{to_abs(self.ball.rel_radius)}"

    def load_ball_coords(self, s: str):
        d = s.split(GAME_STATE_DELIMITER1)
        self.ball.move_to_rel(to_rel(int(d[0])), to_rel(int(d[1])))
        self.ball.rel_radius = to_rel(int(d[2]))

    def server_dump_all_coords(self) -> str:
        return self.dump_paddle_coords(left=True) + GAME_STATE_DELIMITER2 + \
            self.dump_paddle_coords(left=False) + GAME_STATE_DELIMITER2 + \
            self.dump_ball_coords()

    def client_load_all_coords(self, s: str, self_left: bool):
        d = s.split(GAME_STATE_DELIMITER2)
        self.load_paddle_coords(d[1 if self_left else 0], not self_left)
        self.load_ball_coords(d[2])

    def dump_score(self) -> str:
        return f"{self.score_left}{GAME_STATE_DELIMITER1}{self.score_right}"

    def load_score(self, s: str):
        d = s.split(GAME_STATE_DELIMITER1)
        self.score_left = int(d[0])
        self.score_right = int(d[1])

    def is_left_won(self) -> bool:
        return self.score_left >= self.winning_score

    def is_right_won(self) -> bool:
        return self.score_right >= self.winning_score

    def is_won(self, left: bool) -> bool:
        return self.is_left_won() if left else self.is_right_won()

    def any_won(self) -> bool:
        return self.is_left_won() or self.is_right_won()

    @property
    def score_difference(self) -> int:
        return abs(self.score_right - self.score_left)

    def reset(self):
        self.paddle_left.reset()
        self.paddle_right.reset()
        self.ball.reset()
        self.score_left = self.score_right = 0

    def handle_keys_both_player(self, keys):
        if keys[pygame.K_w]:
            self.paddle_left.move(up=True)
        if keys[pygame.K_s]:
            self.paddle_left.move(up=False)

        if keys[pygame.K_UP]:
            self.paddle_right.move(up=True)
        if keys[pygame.K_DOWN]:
            self.paddle_right.move(up=False)

    def handle_keys_single_player(self, keys, self_left: bool):
        paddle = self.get_paddle(self_left)

        if keys[pygame.K_UP]:
            paddle.move(up=True)
        if keys[pygame.K_DOWN]:
            paddle.move(up=False)

    _s_rand_err_choices = None
    _s_rand_err_choice_index = 0

    @classmethod
    def should_ai_make_mistake(cls, ai_efficiency_percent: int) -> bool:
        if not cls._s_rand_err_choices:
            cls._s_rand_err_choices = random.choices(list(range(1, 101)), k=100)

        choice = cls._s_rand_err_choices[cls._s_rand_err_choice_index]
        cls._s_rand_err_choice_index += 1
        if cls._s_rand_err_choice_index == len(cls._s_rand_err_choices):
            cls._s_rand_err_choice_index = 0  # reset
        return choice > ai_efficiency_percent

    def ai_handle_player(self, left: bool):
        paddle = self.get_paddle(left)
        # enemy = self.get_paddle(not left)

        # Intersect the entire Paddle Y-axis with the trajectory of the ball
        tu = line_line_intersection(to_abs(paddle.relx), to_abs(0), to_abs(paddle.relx2), to_abs(1),
                                    to_abs(self.ball.relx), to_abs(self.ball.rely),
                                    to_abs(self.ball.relx + self.ball.rel_velx),
                                    to_abs(self.ball.rely + self.ball.rel_vely), False, False)

        if not tu or tu[1] < 0:  # ball moving || to Y-axis or going away from the paddle
            return

        move_dir = -1  # -1: do not move, 0: down, 1: up

        t = tu[0]
        if U.outside01(t):
            # ball will collide with top/bottom wall, so just flip the collision point about the x-axis
            if t < 0:  # t < 0: Top wall
                t = abs(t)
            else:  # t > 1: Bottom wall
                t = 2 - t
        else:
            # ball will directly hit the paddle
            pass

        collision_point_y = int(lerp(to_abs(0), to_abs(1), t))
        center_y = to_abs(paddle.center_rely)
        dy = collision_point_y - center_y

        if abs(dy) > to_abs((paddle.rel_height / 2) - paddle.rel_vel):
            move_dir = 1 if dy < 0 else 0
        else:
            move_dir = -1  # do not move at all

        if move_dir < 0:
            return

        # stochastic application of difficulty level
        make_mistake = self.should_ai_make_mistake(self.difficulty.ai_efficiency_percent)
        if not make_mistake:
            paddle.move(up=move_dir == 1)

    def update(self) -> int:
        """
        Updates the game by moving the ball and checking for collisions

        :return whether score is changed with this update
        """
        self.ball.move()
        result = self.ball.collide(left_paddle=self.paddle_left, right_paddle=self.paddle_right)

        if self.ball.relx < 0:
            self.score_right += 1
            self.ball.reset()  # todo: seed next level
            # self.ball.accelerate()
            result = GAME_UPDATE_RESULT_WON_RIGHT if self.is_right_won() else GAME_UPDATE_RESULT_SCORE_UP_RIGHT
        elif self.ball.relx > 1:
            self.score_left += 1
            self.ball.reset()  # todo: seed next level
            # self.ball.accelerate()
            result = GAME_UPDATE_RESULT_WON_LEFT if self.is_left_won() else GAME_UPDATE_RESULT_SCORE_UP_LEFT

        return result
