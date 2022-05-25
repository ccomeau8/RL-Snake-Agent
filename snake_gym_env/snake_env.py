
from gym import Env, spaces

import pygame, sys, time, random, os
from typing import Tuple
import numpy as np
from enum import Enum

class SnakeEnv(Env):
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)
    RED = pygame.Color(255, 0, 0)
    GREEN = pygame.Color(0, 255, 0)
    BLUE = pygame.Color(0, 0, 255)

    class Direction(Enum):
        UP = 0
        DOWN = 1
        LEFT = 2
        RIGHT = 3

    class GridEntity(Enum):
        BLANK = 0
        SNAKE = 1
        FOOD = 2

    """A snake game environment for OpenAI gym"""
    def __init__(self, headless: bool=True, fast_mode: bool=True, frame_size: Tuple[int,int]=(720,480), cell_size: int=10):
        super(SnakeEnv, self).__init__()
        self.headless = headless
        self.fast_mode = fast_mode
        if cell_size <=0 or cell_size > min(frame_size):
            raise ValueError(f"Cell size provided ({cell_size}) must be positive and within the frame's bounds (frame: {frame_size})")
        if (frame_size[0] % cell_size != 0 or frame_size[1] % cell_size != 0):
            raise ValueError(f"Grid dimensions must {frame_size} be an integer multiple of grid size {cell_size}")
        self.frame_size = frame_size
        self.cell_size = cell_size
        self.grid_size = np.array([s // cell_size for s in self.frame_size])

        if (headless):
            os.environ["SDL_VIDEODRIVER"] = "dummy"
    
        # self.observation_space = spaces.Box(low=SnakeEnv.GridEntity.BLANK.value,high=255, shape=(self.grid_size[0],self.grid_size[1],1), dtype=np.uint8)
        self.observation_space = spaces.Box(low=SnakeEnv.GridEntity.BLANK.value,high=SnakeEnv.GridEntity.FOOD.value, shape=(self.grid_size[0],self.grid_size[1],1), dtype=np.uint8)

        print(self.observation_space.shape)
        self.action_space = spaces.Discrete(len(SnakeEnv.Direction.__members__.values()))

        # TODO Reward range

    def reset(self):
        print("Reset")
        # Checks for errors encountered
        check_errors = pygame.init()


        # pygame.init() example output -> (6, 0)
        # second number in tuple gives number of errors
        if check_errors[1] > 0:
            print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
            sys.exit(-1)
        else:
            print('[+] Game successfully initialised')

        pygame.display.set_caption('Snake Eater')
        self.game_window = pygame.display.set_mode(self.frame_size)
        self.clock = pygame.time.Clock()

        self.grid = np.zeros(shape=self.grid_size, dtype=np.uint8)
        self.snake_body = np.array([self.grid_size // 2, self.grid_size // 2, self.grid_size // 2]).T
        self.snake_body[0,1] -= 1
        self.snake_body[0,2] -= 2

        self.grid[self.snake_body[0],self.snake_body[1]] = SnakeEnv.GridEntity.SNAKE.value
        
        self.respawn_food()

        self.move_direction = SnakeEnv.Direction.RIGHT
        print(self.move_direction)
        self.score = 0
        ret = np.expand_dims(self.grid,axis=2)
        return ret


    def step(self, action):
        action = SnakeEnv.Direction(action)
        game_over = True

        print("ACT",action)
        
        # Making sure the snake cannot move in the opposite direction instantaneously
        if action == SnakeEnv.Direction.UP and self.move_direction != SnakeEnv.Direction.DOWN:
            self.move_direction = SnakeEnv.Direction.UP
        if action == SnakeEnv.Direction.DOWN and self.move_direction != SnakeEnv.Direction.UP:
            self.move_direction = SnakeEnv.Direction.DOWN
        if action == SnakeEnv.Direction.LEFT and self.move_direction != SnakeEnv.Direction.RIGHT:
            self.move_direction = SnakeEnv.Direction.LEFT
        if action == SnakeEnv.Direction.RIGHT and self.move_direction != SnakeEnv.Direction.LEFT:
            self.move_direction = SnakeEnv.Direction.RIGHT

        print(self.grid)
        print(self.snake_body)
        head = self.snake_body[:,0].T.copy()
        print(head)
        print(self.move_direction)
        # Moving the snake
        if self.move_direction == SnakeEnv.Direction.UP:
            head[1] -= 1
        if self.move_direction == SnakeEnv.Direction.DOWN:
            head[1] += 1
        if self.move_direction == SnakeEnv.Direction.LEFT:
            head[0] -= 1
        if self.move_direction == SnakeEnv.Direction.RIGHT:
            head[0] += 1

        # Game Over conditions
        # Getting out of bounds
        if head[0] < 0 or head[0] >= self.grid_size[0] or head[1] < 0 or head[1] >= self.grid_size[1]:
            game_over = True
            self.game_over()

        # Touching the snake body
        if self.grid[head[0],head[1]] == SnakeEnv.GridEntity.SNAKE:
            game_over = True
            self.game_over()

        print("Before",self.snake_body)
        # Snake body growing mechanism
        self.snake_body = np.insert(self.snake_body,0, head, axis=1)
        if head[0] == self.food_pos[0] and head[1] == self.food_pos[1]:
            self.score += 1
            self.respawn_food()
        else:
            self.snake_body = self.snake_body[:,:-1]
        print("After",self.snake_body)

        # GFX
        self.game_window.fill(SnakeEnv.BLACK)
        for pos in self.snake_body.T:
            # Snake body
            # .draw.rect(play_surface, color, xy-coordinate)
            # xy-coordinate -> .Rect(x, y, size_x, size_y)
            print(pygame.Rect(pos[0], pos[1], 10, 10))
            pygame.draw.rect(self.game_window, SnakeEnv.GREEN, pygame.Rect(pos[0]*self.cell_size, pos[1]*self.cell_size, self.cell_size, self.cell_size))

        # Snake food
        pygame.draw.rect(self.game_window, SnakeEnv.WHITE, pygame.Rect(self.food_pos[0]*self.cell_size, self.food_pos[1]*self.cell_size, self.cell_size, self.cell_size))


        self.show_score(1, SnakeEnv.WHITE, 'consolas', 20)

        pygame.display.update()
        if (not self.fast_mode):
            self.clock.tick(min(self.grid_size)/3)
        return game_over

    
    def respawn_food(self):
        opens = np.where(self.grid == SnakeEnv.GridEntity.BLANK.value)
        opens = list(zip(opens[0], opens[1]))
        self.food_pos = opens[np.random.choice(len(opens), 1)[0]]
        self.grid[self.food_pos[0],self.food_pos[1]] = SnakeEnv.GridEntity.FOOD.value

    # Game Over
    def game_over(self):
        my_font = pygame.font.SysFont('times new roman', 90)
        game_over_surface = my_font.render('YOU DIED', True, SnakeEnv.RED)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (self.frame_size[0]/2, self.frame_size[1]/4)
        self.game_window.fill(SnakeEnv.BLACK)
        self.game_window.blit(game_over_surface, game_over_rect)
        self.show_score(0, SnakeEnv.RED, 'times', 20)
        pygame.display.flip()
        pygame.quit()


    # Score
    def show_score(self,choice, color, font, size):
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render('Score : ' + str(self.score), True, color)
        score_rect = score_surface.get_rect()
        if choice == 1:
            score_rect.midtop = (self.frame_size[0]/10, 15)
        else:
            score_rect.midtop = (self.frame_size[0]/2, self.frame_size[1]/1.25)
        self.game_window.blit(score_surface, score_rect)