import pygame
from time import sleep
import math

scr = [500,500]

cameraPos = [-250,-250]

eList = []

bList = [[(-300,-300),(300,-300)],[(-300,-300),(-300,300)],[(300,-300),(300,300)],[(-300,300),(300,300)], [(50,-100),(200,100)], [(200,100),(50,100)], [(50,-100),(50,100)],[(200,200),(200,100)]]

movm = [(0,1),(-1,0),(0,-1),(1,0)]

fric = .15

def toScreen(p) -> tuple:
    return((p[0] - cameraPos[0],scr[1] - (p[1] - cameraPos[1])))

def collisionTest(p1, p2, b) -> float:
        
    x1 = b[0][0] ; y1 = b[0][1]
    x2 = b[1][0] ; y2 = b[1][1]
    x3 = p1[0]   ; y3 = p1[1]
    x4 = p2[0]   ; y4 = p2[1]
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        den = 10**-20
    t =   ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4))
    u = - ((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3))
    if 1 >= t/den >= 0 and 1 >= u/den >= 0:
        P = (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    else:
        P = False
    print(bList.index(b),P)
    return P

def listAdd(list1:list, list2:list) -> list:
    j = len(list1) - len(list2)
    if j >  0:l1 = list1; l2 = list2
    if j <= 0:l1 = list2; l2 = list1
    o = []
    for i in range(len(l1)):o.append(0)
    for i in range(len(l2)):
        o[i] = l1[i] + l2[i]
    
    if j:
        for i in range(abs(j)):
            o[-(i + 1)] = l1[-(i + 1)]
    
    return o

def listProd(list1:list, list2:list):
    j = len(list1) - len(list2)
    if j >  0:l1 = list1; l2 = list2
    if j <= 0:l1 = list2; l2 = list1
    o = []
    for i in range(len(l1)):o.append(0)
    for i in range(len(l2)):
        o[i] = l1[i] * l2[i]
    
    if j:
        for i in range(abs(j)):
            o[-(i + 1)] = 0
    
    return o

class Projectile:

    def __init__(self, pos, vel, dmg, stats) -> None:
        self.vel = vel
        self.pos = pos
        self.dmg = (dmg * stats["bulletDmg%"] + stats["bulletDmgRaw"])
        self.stats = stats
        pass

    def render(self) -> None:
        pygame.draw.circle(screen, (255,0,0), toScreen(self.pos), 3, 3)

    def delete(self) -> None:
        eList.remove(self)

    def update(self) -> None:
        if cameraPos[0] < self.pos[0] < cameraPos[0] + scr[0] and cameraPos[1] < self.pos[1] < cameraPos[1] + scr[1]:0
        else:self.delete()
        if self.vel == [0,0]:self.delete()
        s = self.pos
        self.pos = [self.pos[0] + self.vel[0] * self.stats["bulletSpeed%"], self.pos[1] + self.vel[1] * self.stats["bulletSpeed%"]]
        self.vel = [self.vel[0], self.vel[1]]
        for b in bList:
            if collisionTest(s, self.pos, b):
                self.pos = s; self.vel = [0,0]


class Player:

    def __init__(self, inv:dict, stats:dict) -> None:
        self.pos   = [0,0]
        self.vel   = [0,0]
        self.inv   = inv
        self.stats = stats
        self.size = [25,25]
        pass

    def update(self) -> None:
        s = self.pos
        self.pos = [self.pos[0] + self.vel[0] * (self.stats["speed%"]), self.pos[1] + self.vel[1] * (self.stats["speed%"])]
        self.vel = [self.vel[0] * (1 - fric), self.vel[1] * (1 - fric)]
        for b in bList:
            if collisionTest(s, self.pos, b):
                self.pos = s; self.vel = [0,0]

    def render(self) -> None:
        pygame.draw.rect(screen, (255,255,127), (toScreen(self.pos)[0] - self.size[0] / 2,toScreen(self.pos)[1] - self.size[1] / 2, self.size[0], self.size[1]), 1)
    
    def move(self, inputMap:list) -> None:
        movL = listProd(inputMap, movm)
        for i in movL:
            self.vel = listAdd(self.vel, i)
    
    def shoot(self, inputMap:list) -> None:
        bulletVel = [0,0]
        movL = listProd(inputMap, movm)
        for i in movL:
            bulletVel = listAdd(bulletVel, i)
        eList.append(Projectile(self.pos, [bulletVel[0] * self.stats["bulletSpeed%"] + self.vel[0] / 10, bulletVel[1] * self.stats["bulletSpeed%"] + self.vel[1] / 10], 1, self.stats))



pygame.display.set_caption('im on the rainbow bridge')
screen = pygame.display.set_mode(scr)
fRate = 1/30

eList.append(Player({},{"speed%":2, "bulletSpeed%":5, "bulletDmg%": 1, "bulletDmgRaw": 0}))

player = eList[0]

while 1:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_ESCAPE:
                pygame.quit()
            if k == pygame.K_r:
                eList[0] = Player({},{"speed%":2, "bulletSpeed%":5, "bulletDmg%": 1, "bulletDmgRaw": 0})
                player = eList[0]

    k = pygame.key.get_pressed()

    arrows = [int(k[pygame.K_UP]),int(k[pygame.K_LEFT]),int(k[pygame.K_DOWN]),int(k[pygame.K_RIGHT])]
    wasd = [int(k[pygame.K_w]),int(k[pygame.K_a]),int(k[pygame.K_s]),int(k[pygame.K_d])]

    cameraPos = [player.pos[0] - int(scr[0] / 2), player.pos[1] - int(scr[1] / 2)]

    for e in eList:
        e.update()

    player.move(wasd)
    if arrows != [0,0,0,0]:player.shoot(arrows)

    screen.fill((0,0,0))

    for e in eList:
        e.render()

    for b in bList:
        pygame.draw.line(screen, (255,255,255), toScreen(b[0]), toScreen(b[1]))

    pygame.display.update()
    sleep(fRate)