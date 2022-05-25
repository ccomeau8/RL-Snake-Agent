import gym
from snake_gym_env.snake_env import SnakeEnv
from gym.utils.env_checker import check_env
import pygame, sys
import time

env = SnakeEnv(headless=False,fast_mode=False,cell_size=120)


env.reset()


env.reset()
change_to = 0
while env.step(change_to):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Whenever a key is pressed down
        elif event.type == pygame.KEYDOWN:
            # W -> Up; S -> Down; A -> Left; D -> Right
            if event.key == pygame.K_UP or event.key == ord('w'):
                change_to = 0
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                change_to = 1
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                change_to = 2
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                change_to = 3
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))


