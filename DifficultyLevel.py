import R
from U import to_abs, to_rel, get_vel_max_total
from C import LOCAL_CONFIG_KEY_AI_EFFICIENCY
from R import CONFIG


class DifficultyLevel:

    def __init__(self, _id: int, key: str, display_name: str,
                 paddle_rel_width: float, paddle_rel_height: float, paddle_rel_vel: float,
                 ball_rel_radius: float, ball_rel_vel_max_component: float, ball_reset_delay_secs: float,
                 ball_random_initial_vel_enabled: bool,
                 ball_x_vel_min_factor: float,
                 winning_socre: int, default_ai_efficiency_percent: int):
        self.id: int = _id
        self.key = key
        self.display_name = display_name

        vel_factor = 60 / R.FPS         # velocities are designed to work with 60 fps

        self.ball_rel_radius: float = ball_rel_radius
        self.ball_rel_vel_max_component: float = ball_rel_vel_max_component * vel_factor
        self.ball_reset_delay_secs: float = ball_reset_delay_secs
        self.ball_random_initial_vel_enabled = ball_random_initial_vel_enabled
        self.ball_x_vel_min_factor = ball_x_vel_min_factor
        self.ai_efficiency_percent = self.default_ai_efficiency_percent = default_ai_efficiency_percent
        self.winning_score = winning_socre

        # otherwise ball will just pass through paddle
        self.paddle_rel_width: float = to_rel(
            max(to_abs(paddle_rel_width), to_abs(get_vel_max_total(self.ball_rel_vel_max_component)) + 4))
        self.paddle_rel_height: float = paddle_rel_height
        self.paddle_rel_vel: float = paddle_rel_vel * vel_factor

    @property
    def local_config_key_ai_efficiency(self):
        return LOCAL_CONFIG_KEY_AI_EFFICIENCY + "_" + self.key

    def reset_ai_efficiency(self):
        self.ai_efficiency_percent = self.default_ai_efficiency_percent

    def __eq__(self, other):
        return isinstance(other, DifficultyLevel) and self.id == other.id

    def __repr__(self):
        return f"DifficultyLevel(id: {self.id}, key: {self.key}, display_name: {self.display_name})"

    def __str__(self):
        return self.display_name


# Difficulty Levels
DIFFICULTY_LEVEL_EASY = DifficultyLevel(_id=0xAAA0, key="EASY", display_name="Easy",
                                        paddle_rel_width=0.0087, paddle_rel_height=0.138, paddle_rel_vel=0.0095,
                                        ball_rel_radius=0.01, ball_rel_vel_max_component=0.00725,
                                        ball_reset_delay_secs=2.5, ball_random_initial_vel_enabled=True,
                                        ball_x_vel_min_factor=0.89,
                                        winning_socre=3, default_ai_efficiency_percent=20)

DIFFICULTY_LEVEL_NORMAL = DifficultyLevel(_id=0xAAA1, key="NORMAL", display_name="Normal",
                                          paddle_rel_width=0.00875, paddle_rel_height=0.11875, paddle_rel_vel=0.0098,
                                          ball_rel_radius=0.008, ball_rel_vel_max_component=0.00755,
                                          ball_reset_delay_secs=2, ball_random_initial_vel_enabled=True,
                                          ball_x_vel_min_factor=0.86,
                                          winning_socre=5, default_ai_efficiency_percent=40)

DIFFICULTY_LEVEL_HARD = DifficultyLevel(_id=0xAAA2, key="HARD", display_name="Hard",
                                        paddle_rel_width=0.009, paddle_rel_height=0.1, paddle_rel_vel=0.011,
                                        ball_rel_radius=0.008, ball_rel_vel_max_component=0.0088,
                                        ball_reset_delay_secs=1.5, ball_random_initial_vel_enabled=True,
                                        ball_x_vel_min_factor=0.82,
                                        winning_socre=10, default_ai_efficiency_percent=60)

DIFFICULTY_LEVEL_EXPERT = DifficultyLevel(_id=0xAAA3, key="EXPERT", display_name="Expert",
                                          paddle_rel_width=0.01125, paddle_rel_height=0.0925, paddle_rel_vel=0.014,
                                          ball_rel_radius=0.0072, ball_rel_vel_max_component=0.0098,
                                          ball_reset_delay_secs=1, ball_random_initial_vel_enabled=True,
                                          ball_x_vel_min_factor=0.8,
                                          winning_socre=10, default_ai_efficiency_percent=85)

DIFFICULTY_LEVEL_DEFAULT = DIFFICULTY_LEVEL_NORMAL

DIFFICULTY_LEVELS: list = [
    DIFFICULTY_LEVEL_EASY,
    DIFFICULTY_LEVEL_NORMAL,
    DIFFICULTY_LEVEL_HARD,
    DIFFICULTY_LEVEL_EXPERT
]


def load_difficulty(_id: int, default: DifficultyLevel = DIFFICULTY_LEVEL_DEFAULT) -> DifficultyLevel:
    for d in DIFFICULTY_LEVELS:
        if d.id == _id:
            return d
    return default


def load_local_ai_efficiencies():
    data = CONFIG.client_local_config

    for d in DIFFICULTY_LEVELS:
        key = d.local_config_key_ai_efficiency
        val = data.get(key, '')
        if val:
            try:
                i_val = int(val)
                if 0 <= i_val <= 100:
                    d.ai_efficiency_percent = i_val
            except ValueError:
                pass
