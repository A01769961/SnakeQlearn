from stable_baselines3.common.env_checker import check_env
from snakeEnv import *


env = snakeEnv()
# It will check your custom environment and output additional warnings if needed
check_env(env, warn=True)