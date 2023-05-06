import pygame
import random
#variables escenario
ancho = 630
altura = 480
filas = 30
columnas = 40
fps = 10

#Variables comida y serpiente
s_dir = ''
s_body = []
comida_pos = []
comida_exs = False
gameOver = False
score = 0

def genSnake(s_body, s_dir):
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
        # initail direction
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

def genComida(s_body,comida_pos):
    if len(comida_pos) == 0:
        # apple generating
        x = random.randrange(1, columnas + 1)
        y = random.randrange(1, filas + 1)
        while [x, y] in s_body:
            x = random.randrange(1, columnas + 1)
            y = random.randrange(1, filas + 1)
        comida_pos = [x, y]

    return comida_pos

def updateSnake(s_dir, s_body, comida_exs, gameOver):
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

def collisionDetector(s_body, comida_pos, s_dir, comida_exs, gameOver, Score):
    # apple and snake head
    if s_body[0] == comida_pos:
        comida_exs = True
        Score += 1
        comida_pos = []

    # snake head and wall
    if s_body[0][1] == 1 and s_dir == 'up':
        gameOver = True
    if s_body[0][1] == 30 and s_dir == 'down':
        gameOver = True
    if s_body[0][0] == 1 and s_dir == 'left':
        gameOver = True
    if s_body[0][0] == 40 and s_dir == 'right':
        gameOver = True

    # snake head and snake body
    if s_body[0] in s_body[1:]:
        gameOver = True

    return comida_exs, gameOver, Score, comida_pos

pygame.init()
pygame.display.set_caption('SnakeQLearn')
display = pygame.display.set_mode((ancho,altura))
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial_bold', 20)
running = True

while running == True:
    s_body, s_dir = genSnake(s_body, s_dir)
    s_body, comida_exs = updateSnake(s_dir, s_body, comida_exs, gameOver)
    comida_exs, gameOver, score, comida_pos = collisionDetector(s_body, comida_pos, s_dir, comida_exs, gameOver, score)
    comida_pos = genComida(s_body, comida_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False
                break
            if event.key == pygame.K_RIGHT and not s_body[0][0] < s_body[1][0]:
                s_dir = 'right'
            if event.key == pygame.K_LEFT and not s_body[0][0] > s_body[1][0]:
                s_dir = 'left'
            if event.key == pygame.K_DOWN and not s_body[0][1] < s_body[1][1]:
                s_dir = 'down'
            if event.key == pygame.K_UP and not s_body[0][1] > s_body[1][1]:
                s_dir = 'up'
    #draw
    display.fill((255, 253, 208))
    #borders
    pygame.draw.rect(display, 'BLACK', (15, 15, 40*15, 1))
    pygame.draw.rect(display, 'BLACK', (15, 31*15, 40*15, 1))
    pygame.draw.rect(display, 'BLACK', (41*15, 15, 1, 30*15))
    pygame.draw.rect(display, 'BLACK', (15, 15, 1, 30*15))

    # score
    if gameOver:
        img = font.render(str(score), True, (255, 255, 255))
    else:
        img = font.render(str(score), True, (57, 60, 65))
    score_rect = img.get_rect()
    display.blit(img, score_rect)

    # comida
    if len(comida_pos) > 0:
        pygame.draw.rect(display, 'RED', (comida_pos[0] * 15 + 1, comida_pos[1] * 15 + 1, 13, 13))

    # snake body
    for part in s_body[1:]:
        pygame.draw.rect(display, "green", (part[0] * 15 + 1, part[1] * 15 + 1, 13, 13))
    
    # snake head
    pygame.draw.rect(display, 'black', (s_body[0][0] * 15 + 1, s_body[0][1] * 15 + 1, 13, 13))

    pygame.display.update()
    clock.tick(fps)
pygame.quit