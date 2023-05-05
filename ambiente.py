from typing import Tuple
import gym
from gym import spaces
import pandas as pd
import numpy as np
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
        self.reward_range = (-float('inf'), float('inf'))
        self.viewer = None
        
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
        pygame.init()
        self.screen = pygame.display.set_mode((self.ancho, self.alto))
        creaTablero()
        creaComida()
        self.step()

        def crearSnake():
            self.sitio[0] = random.randint(1, self.celdas) # X del sitio donde va a estar la cabeza de snake
            self.sitio[1] = random.randint(1, self.celdas) # Y del sitio donde va a estar la cabeza de snake
            self.tablero[self.sitio[1]][self.sitio[0]]=-50 
    
        
        def creaTablero():
            for i in range( self.celdas + 2): #Hacemos una matriz de -1 con borde -100 O(n²)
                temp = []
                if i == 0 or i == self.celdas + 1:
                    for j in range(self.celdas + 2):
                        temp.append( -100 ) 
                else:
                    for j in range(self.celdas + 2):
                        if j==0 or j==self.celdas+1:
                            temp.append( -100 )
                        else:
                            temp.append( -1 )
                self.tablero.append( temp )
                
            crearSnake() #Llamamos a la funcion para crear a snake
            
            self.fila.append([self.sitio[0],self.sitio[1]]) # Ponemos la posicion de snake en la fila para saber donde esta la cabeza
            return
        
        
        def creaComida():
            while True: #Repetimos el loop hasta que se pueda crear la comida
                numero_aleatoriox = random.randint(1, self.celdas) #X
                numero_aleatorioy = random.randint(1, self.celdas) #Y
                if self.tablero[numero_aleatorioy][numero_aleatoriox]==-1 : #Verificamos q no exista snake en la possicion generada
                    self.tablero[numero_aleatorioy][numero_aleatoriox]=100 #Creamos la comida en la matrizw
                    self.comida[0]=numero_aleatoriox #Guardamos la posicion de X en la comida
                    self.comida[1]=numero_aleatorioy #Guardamos la posicion de Y en la comida
                    self.comidaExist = True
                    break

        def dibujaCeldas(screen): # Dibujamos las celdas
            color = "black"
            for i in range(self.celdas):
                temporal=i*self.alto/self.celdas
                start_pos = (0, temporal)
                end_pos = (self.ancho, temporal)
                pygame.draw.line(screen, color, start_pos, end_pos, self.thickness)

                temporal=i*self.ancho/self.celdas
                start_pos = (temporal, 0)
                end_pos = (temporal, self.alto)
                pygame.draw.line(screen, color, start_pos, end_pos, self.thickness)
            
        def dibujaSnakeyComida(screen): 
            mat=[]
            for i in range(self.celdas+2):
                temp=[]
                if i==0 or i==self.celdas+1:
                    for j in range(self.celdas+2):
                        temp.append(-100) 
                else:
                    for j in range(self.celdas+2):
                        if j==0 or j==self.celdas+1:
                            temp.append(-100)
                        else:
                            temp.append(-1)
                mat.append(temp) #LLenamos la matriz
        
            cabeza=self.fila[-1] #Guardamos las cordenadas de la cabeza
            for i in self.fila: # Pintamos a toda snake de verde
                mat[i[1]][i[0]]=-50
                pygame.draw.circle(screen, "green",( self.ancho/self.celdas*(i[0]-1) + self.ancho/self.celdas/2 , self.alto/self.celdas*(i[1]-1) + self.alto/self.celdas/2), 20)
                    
            mat[cabeza[1]][cabeza[0]]=0 # Pintamos la cabeza de snake de negro
            pygame.draw.circle(screen, "black",( self.ancho/self.celdas*(cabeza[0]-1) + self.ancho/self.celdas/2 , self.alto/self.celdas*(cabeza[1]-1) + self.alto/self.celdas/2), 20)
                    
            mat[self.comida[1]][self.comida[0]]=100 # Pintamos la comida
            pygame.draw.circle(screen, "red",( self.ancho/self.celdas*(self.comida[0]-1) + self.ancho/self.celdas/2 , self.alto/self.celdas*(self.comida[1]-1) + self.alto/self.celdas/2), 20)
            self.tablero=mat

        def dibuja(screen):
            dibujaSnakeyComida(screen) # Dibujamos a snake y Comidaw
            if not (self.comidaExist): #Verificamos la existencia de la comida si no existe:
                creaComida() #Creamos la comida
            dibujaCeldas(screen) # Dibujamos celdas
            dibujaSnakeyComida(screen) # Dibujamos a snake y Comida
            
        def move(): 
            x = self.sitio[0] #renombramos para mayor comodidad
            y = self.sitio[1]
            nx =self.newSitio[0]
            ny =self.newSitio[1]


            if not moviendome: # Si no hay movimiento asignamos una direccion
                if self.direccion[self.indexdireccion] == "der" and (aDonde!="izq" or len(self.fila)<2) : # Hcemos que no se salga ni choque en si misma de momento
                    aDonde="der"
                    moviendome= True
                    nx= x+1

                elif self.direccion[self.indexdireccion] == "izq" and (aDonde!="der" or len(self.fila)<2) : # Hcemos que no se salga ni choque en si misma de momento
                    aDonde="izq"
                    moviendome= True
                    nx= x-1

                elif self.direccion[self.indexdireccion] == "aba" and (aDonde!="arr" or len(self.fila)<2)  : # Hcemos que no se salga ni choque en si misma de momento
                    aDonde="aba"
                    moviendome= True
                    ny= y+1

                elif self.direccion[self.indexdireccion] =="arr" and (aDonde!="aba" or len(self.fila)<2)  : # Hcemos que no se salga ni choque en si misma de momento
                    aDonde="arr"
                    moviendome= True
                    ny= y-1 
                else:
                    moviendome= True
                    if  aDonde=="izq":
                        nx= x-1
                    if  aDonde=="der":
                        nx= x+1
                    if  aDonde=="arr":
                        ny= y-1 
                    if  aDonde=="aba":
                        ny= y+1 
                        
            else: # Nos movemos de acuerdo a la direccion
                if aDonde == "der":
                    x=x+self.vel

                if aDonde == "izq":
                    x=x-self.vel
                
                if aDonde == "aba":
                    y=y+self.vel
                
                if aDonde == "arr":
                    y=y-self.vel
                    
                    
            if aDonde == "der": 
                if (x>nx): # Cuando llegamos  decimos que ya no nos movemos 
                    moviendome=False
                    x=nx

                    

                    if self.tablero[y][x]==100:
                        self.comidaExist=False
                        self.fila.append([x,y])
                    elif self.tablero[y][x]==-100: # si es comida agregamos a snake una bolita mas
                            self.gameover=True
                    elif self.tablero[y][x]==-50: # si es comida agregamos a snake una bolita mas
                            self.gameover=True
                    else: # Sino agregamos la bolita de posicion y quitamos la cola
                        self.fila.append([x,y])
                        self.fila.popleft()
                    
                    
                    

                    

            if aDonde == "izq": 
                if (x<nx): # Cuando llegamos  decimos que ya no nos movemos 
                    moviendome=False
                    x=nx
                    if self.tablero[y][x]==100:
                        self.comidaExist=False
                        self.fila.append([x,y])
                    elif self.tablero[y][x]==-100: # si es comida agregamos a snake una bolita mas
                            self.gameover=True
                    elif self.tablero[y][x]==-50: # si es comida agregamos a snake una bolita mas
                            self.gameover=True
                    else: # Sino agregamos la bolita de posicion y quitamos la cola
                        self.fila.append([x,y])
                        self.fila.popleft()

            
            if aDonde == "aba": 
                if (y>ny): # Cuando llegamos  decimos que ya no nos movemos 
                    moviendome=False
                    y=ny
                    if self.tablero[y][x]==100: # si es comida agregamos a snake una bolita mas
                        self.comidaExist=False
                        self.fila.append([x,y])
                    elif self.tablero[y][x]==-100: # si es comida agregamos a snake una bolita mas
                            self.gameover=True
                    elif self.tablero[y][x]==-50: # si es comida agregamos a snake una bolita mas
                            self.gameover=True
                    else: # Sino agregamos la bolita de posicion y quitamos la cola
                        self.fila.append([x,y])
                        self.fila.popleft()
        

            if aDonde == "arr":
                if (y<ny):
                    moviendome=False
                    y=ny
                    if self.tablero[y][x]==100: # si es comida agregamos a snake una bolita mas
                        self.comidaExist=False
                        self.fila.append([x,y])
                    elif self.tablero[y][x]==-100: # si es comida agregamos a snake una bolita mas
                            self.gameover=True
                    elif self.tablero[y][x]==-50: # si es comida agregamos a snake una bolita mas
                            self.gameover=True
                    else: # Sino agregamos la bolita de posicion y quitamos la cola
                        self.fila.append([x,y])
                        self.fila.popleft()

            self.sitio[0] = x 
            self.sitio[1] = y
            self.newSitio[0] = nx 
            self.newSitio[1] = ny

        
        def reset(self):
            # 1. Reiniciar las variables de estado del ambiente
            self.tablero = creaTablero() # creaTablero() es una función que inicializa el tablero
            self.sitio = [random.randint(1, self.celdas), random.randint(1, self.celdas)]
            self.fila = deque([[self.sitio[0],self.sitio[1]]])
            self.newSitio = [0, 0]
            self.comidaExist = False
            self.gameover = False
            self.moviendome = False
            self.aDonde = ""
            self.indexdireccion = 3
            
            # 2. Devolver el estado inicial del ambiente (observaciones)
            return np.array(self.tablero)

        def step(self, action):
            # 1. Actualizar la dirección de la serpiente en función de la acción recibida
            if action == 0 and self.indexdireccion != 1:
                self.aDonde = "der"
                self.indexdireccion = 0
            elif action == 1 and self.indexdireccion != 0:
                self.aDonde = "izq"
                self.indexdireccion = 1
            elif action == 2 and self.indexdireccion != 3:
                self.aDonde = "aba"
                self.indexdireccion = 2
            elif action == 3 and self.indexdireccion != 2:
                self.aDonde = "arr"
                self.indexdireccion = 3
            
            # 2. Mover la serpiente en la dirección actual
            if self.moviendome == True:
                self.fila.appendleft(list(self.newSitio))
                self.fila.pop()
                for i in range(len(self.fila)):
                    if i == 0:
                        self.tablero[self.fila[i][0]][self.fila[i][1]] = -50
                    else:
                        self.tablero[self.fila[i][0]][self.fila[i][1]] = -50
            else:
                self.moviendome = True
            
            if self.aDonde == "der":
                self.newSitio[1] += 1
            elif self.aDonde == "izq":
                self.newSitio[1] -= 1
            elif self.aDonde == "aba":
                self.newSitio[0] += 1
            elif self.aDonde == "arr":
                self.newSitio[0] -= 1
            
            # 3. Verificar si la serpiente se ha comido la comida
            if self.newSitio == self.comida:
                self.comidaExist = False
                self.fila.appendleft(list(self.newSitio))
                self.tablero[self.newSitio[0]][self.newSitio[1]] = -50
                self.nuevaComida()
            else:
                self.tablero[self.newSitio[0]][self.newSitio[1]] = -50
            
            # 4. Verificar si la serpiente se ha chocado con el borde o consigo misma
            if self.newSitio[0] == 0 or self.newSitio[0] == self.celdas-1 or self.newSitio[1] == 0 or self.newSitio[1] == self.celdas-1:
                self.gameover = True
                reward = -10
                return np.array(self.tablero), reward, self.gameover, {}
            
            for i in range(1, len(self.fila)):
                if self.newSitio == self.fila[i]:
                    self.gameover = True
                    reward = -10
                    return np.array(self.tablero), reward, self.gameover, {}
            
            # 5. Actualizar la puntuación y devolver el estado actualizado del ambiente (observaciones) y la recompensa obtenida
            reward = 1
            return np.array(self.tablero), reward, self.gameover, {}
        
        def render(self, mode='human'):
            self.screen.fill((255, 255, 255))
            dibujaCeldas(self.screen)
            dibujaSnakeyComida(self.screen)
            pygame.display.flip()
