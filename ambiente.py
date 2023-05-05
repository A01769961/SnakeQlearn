from typing import Tuple
import gym
from gym import spaces
import pandas
import numpy
import random
import pygame
from collections import deque

class SnakeEnv(gym.Env):
    metadata = {'render.modes': ['human']}
     # actions available 
    UP   = 0
    LEFT = 1
    DOWN = 2
    RIGHT= 3


    
    def __init__(self):
        self.ancho=1000 #Ancho de la Pantalla
        self.alto=1000  #Largo de la Pantalla
        self.fps= 8 #Fps a los que se mueve el juego
        self.vel = .2 #Velocidad de la serpiente recomendacion dejarlo en divisores de 1 
        self.celdas=5   #Celdas del tablero recomendado para ver 23*23 celdas
        self.thickness = 5 #Circunferencia del cuerpo

        self.tablero=[] #Matriz del tablero donde |-1 Casilla sin nada |-100 Casilla de borde |-50 Cuerpo de la serpiente |100 Comida de la serpiente
        self.sitio=[0,0] #Sitio actuual de Snake en forma x,y
        self.newSitio=[0,0] #Sitio a donde va a ir Snake en forma x,y
        self.comida=[0,0] #Sitio actual de la comida en forma x,y
        self.fila = deque() # Crear una cola vacía para saber donde esta el cuerpo de snake

        self.comidaExist = False # Booleano si la comida existe
        self.moviendome = False #Actualmente se esta moviendo?
        self.gameover= False
        self.start=True

        self.indexdireccion=3
        self.direccion=["der","izq","aba", "arr"] #Arreglo de las direcciones a 3letras para comodidad
        self.aDonde="" #Direccion actual de snake
        
        self.action_space = spaces.Discrete(4) # acciones del agente
        self.observation_space = spaces.Box(low=-1, high=100, shape=(self.celdas, self.celdas), dtype=np.int) # observaciones del agente
        
        self.step()

    def step(self, action):
        
          