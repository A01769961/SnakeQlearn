import random
import time
import pygame
import gym
from gym import spaces
import numpy as np


#variables escenario
ancho = 630
altura = 480
filas = 30
columnas = 40
fps = 30

def genSnake(s_body, s_dir): #Crea Snake
    if len(s_body) == 0:
        #head
        x = random.randrange(3, columnas - 1)
        y = random.randrange(3, filas - 1)
        s_body.append([x, y])
        # body
        s_body.append(random.choice([[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]))

        # tail
        x = s_body[-1][0]
        y = s_body[-1][1]
        temp = [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]
        temp.remove([s_body[0][0], s_body[0][1]])
        s_body.append(random.choice(temp))

    if len(s_dir) == 0:
        #direccion inicial
        dir_list = ['right', 'left', 'up', 'down']
        if s_body[0][0] > s_body[1][0]:
            dir_list.remove('left')
        if s_body[0][1] > s_body[1][1]:
            dir_list.remove('up')
        if s_body[0][0] < s_body[1][0]:
            dir_list.remove('right')
        if s_body[0][1] < s_body[1][1]:
            dir_list.remove('down')
        s_dir = random.choice(dir_list)

    return s_body, s_dir


def genComida(s_body,comida_pos):#Crea comida
    if len(comida_pos) == 0:
        x = random.randrange(1, columnas + 1)
        y = random.randrange(1, filas + 1)
        while [x, y] in s_body:
            x = random.randrange(1, columnas + 1)
            y = random.randrange(1, filas + 1)
        comida_pos = [x, y]

    return comida_pos


def updateSnake(s_dir, s_body, comida_exs, gameOver):#Acutaliza Snake mientras se mueve
    if not gameOver:

        if not comida_exs:
            s_body.pop(-1)
        else:
            comida_exs = False

        if s_dir == 'up':
            s_body.insert(0, [s_body[0][0], s_body[0][1] - 1])
        if s_dir == 'down':
            s_body.insert(0, [s_body[0][0], s_body[0][1] + 1])
        if s_dir == 'right':
            s_body.insert(0, [s_body[0][0] + 1, s_body[0][1]])
        if s_dir == 'left':
            s_body.insert(0, [s_body[0][0] - 1, s_body[0][1]])
    return s_body, comida_exs


def collisionDetector(s_body, comida_pos, s_dir, comida_exs, gameOver, Score):#Detector Colisiones
    #Con comida
    if s_body[0] == comida_pos:
        comida_exs = True
        Score += 1
        comida_pos = []

    # Con bordes
    if s_body[0][1] == 1 and s_dir == 'up':
        gameOver = True
    if s_body[0][1] == 30 and s_dir == 'down':
        gameOver = True
    if s_body[0][0] == 1 and s_dir == 'left':
        gameOver = True
    if s_body[0][0] == 40 and s_dir == 'right':
        gameOver = True

    #Con cuerpo
    if s_body[0] in s_body[1:]:
        gameOver = True

    return comida_exs, gameOver, Score, comida_pos

class snakeEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    def __init__(self):
        self.render_mode = None
        # Define action and observation space
        # # They must be gym.spaces objects
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=40, shape=(5,), dtype=np.int32)

    def step(self, action):
        self.comida_exs, self.gameOver, self.score, self.comida_pos = collisionDetector(self.s_body, self.comida_pos, self.s_dir, self.comida_exs, self.gameOver, self.score)
        self.s_body, self.comida_exs = updateSnake(self.s_dir, self.s_body, self.comida_exs, self.gameOver)
        self.comida_pos = genComida(self.s_body, self.comida_pos)

        # snake dir
        if action == 0:
            self.s_dir = 'up'
        elif action == 1:
            self.s_dir = 'down'
        elif action == 2:
            self.s_dir = 'right'
        elif action == 3:
            self.s_dir = 'left'
        
        #observation
        self.observation = [self.s_body[0][0], self.s_body[0][1], self.comida_pos[0], self.comida_pos[1], action]
        self.observation = np.array(self.observation)

        if self.gameOver:
            self.done = True

        #rewards/punishments
        # gameover punishment
        if self.done:
            reward_a = -100
        else:
            reward_a = 0
        # comida reward
        if self.prev_score < self.score:
            reward_b = 10
            self.prev_score = self.score
            self.timestep_passed_eating = 0
            self.valid_timestep_to_eat += 1
        else:
            reward_b = 0
            self.timestep_passed_eating += 1
        
        # distancia rewards/punishments
        self.dist = abs(self.s_body[0][0] - self.comida_pos[0]) + abs(self.s_body[0][1] - self.comida_pos[1])
        if self.dist > self.prev_dist:
            reward_c = -1
        elif self.dist < self.prev_dist:
            reward_c = 1
        else:
            reward_c = 0
        self.prev_dist = self.dist

         # castigo perder tiempo
        reward_d = -self.timestep_passed_eating // self.valid_timestep_to_eat
        self.reward = reward_a + reward_b + reward_c + reward_d

        self.info = {}

        if self.render_mode=='human':
            self.render()




        return self.observation, self.reward, self.done, self.info
    
    
    def reset(self):
        self.done = False
        self.s_dir = ''
        self.s_body = []
        self.comida_pos = []
        self.comida_exs = False
        self.gameOver = False

        #crea snake y comida
        self.s_body, self.s_dir = genSnake(self.s_body, self.s_dir)
        self.comida_pos = genComida(self.s_body, self.comida_pos)

        #observation
        if self.s_dir == 'up':
            self.numerical_dir = 0
        elif self.s_dir == 'down':
            self.numerical_dir = 1
        elif self.s_dir == 'right':
            self.numerical_dir = 2
        elif self.s_dir == 'left':
            self.numerical_dir = 3

        self.observation = [self.s_body[0][0], self.s_body[0][1], self.comida_pos[0], self.comida_pos[1], self.numerical_dir]
        self.observation = np.array(self.observation)

        # reward
        self.reward = 0
        self.score = 0
        self.prev_score = 0
        self.dist = abs(self.s_body[0][0] - self.comida_pos[0]) + abs(self.s_body[0][1] - self.comida_pos[1])
        self.prev_dist = self.dist
        self.valid_timestep_to_eat = 30 + 40 + 3
        self.timestep_passed_eating = 0

        if self.render_mode == 'human':
            pygame.init()
            pygame.display.set_caption('Snake RL')
            self.display = pygame.display.set_mode((ancho, altura))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont('Arial_bold', 20)

            self.render()

        return self.observation  # reward, done, info can't be included
    
    def render(self, render_mode='human'):
        #draw
        self.display.fill((255, 253, 208))
        #borders
        pygame.draw.rect(self.display, 'BLACK', (15, 15, 40*15, 1))
        pygame.draw.rect(self.display, 'BLACK', (15, 31*15, 40*15, 1))
        pygame.draw.rect(self.display, 'BLACK', (41*15, 15, 1, 30*15))
        pygame.draw.rect(self.display, 'BLACK', (15, 15, 1, 30*15))

        # score
        if self.gameOver:
            img = self.font.render(str(self.score), True, (255, 255, 255))
        else:
            img = self.font.render(str(self.score), True, (57, 60, 65))
        score_rect = img.get_rect()
        self.display.blit(img, score_rect)

        # comida
        if len(self.comida_pos) > 0:
            pygame.draw.rect(self.display, 'RED', (self.comida_pos[0] * 15 + 1, self.comida_pos[1] * 15 + 1, 13, 13))

        # snake body
        for part in self.s_body[1:]:
            pygame.draw.rect(self.display, "green", (part[0] * 15 + 1, part[1] * 15 + 1, 13, 13))
        
        # snake head
        pygame.draw.rect(self.display, 'black', (self.s_body[0][0] * 15 + 1, self.s_body[0][1] * 15 + 1, 13, 13))

        pygame.display.update()
        self.clock.tick(fps)

        #delay para verlo mejor
        if self.done:
            time.sleep(0.5)


    def close (self):
        pygame.quit()