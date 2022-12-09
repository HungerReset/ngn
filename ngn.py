import pygame
from time import sleep
import math
import random

scr       = [800,600]
cameraPos = [-250,-250]
eList     = []
bList     = []
movm      = [(0,1),(-1,0),(0,-1),(1,0)]
fric      = .15
cos45     = .707
lvlInd    = 0

defstats  = {"speed%":2, "bulletSpeed%":3.5, "bulletDmg%": 1, "bulletDmgRaw": 0}

# reading options file (d9.fig)

dataRaw = open("d9.fig", "r").read()
dataRaw = dataRaw.replace(" ", "").replace("	", "").replace("\n", "")
dataDunder = dataRaw.split("__")
dataDict = {}
for i in range(len(dataDunder) - 1):
    o = dataDunder[i + 1][1:len(dataDunder[i + 1])]
    o = o.split(";")
    for u in range(len(o)):
        o[u] = o[u].split(":")
    dataDict[dataDunder[i + 1][0]] = o
oL = dataDict["o"]; oo = {}
for o in range(len(oL)):
    oo[oL[o][0]] = int(oL[o][1])

if not oo["customLevels"]:
    lvlList = ["l1.d9", "l2.d9"]

def getLvlData(fName:str) -> dict:
    dataRaw = open(f"{fName}", "r").read()
    dataRaw = dataRaw.replace(" ", "").replace("	", "").replace("\n", "")
    dataDunder = dataRaw.split("__")
    dataDict = {}
    for i in range(len(dataDunder) - 1):
        o = dataDunder[i + 1][1:len(dataDunder[i + 1])]
        o = o.split(";")
        for u in range(len(o)):
            o[u] = o[u].split(",")
        dataDict[dataDunder[i + 1][0]] = o
    bL = dataDict["b"]
    for b in range(len(bL)):
        bL[b] = [(int(bL[b][0]),int(bL[b][1])),(int(bL[b][2]),int(bL[b][3]))]
    eL = dataDict["e"]
    for e in range(len(eL)):
        eL[e] = [eL[e][0], [int(eL[e][1]), int(eL[e][2])]]
    pL = dataDict["p"][0]; inv = {}; stats = {};
    if pL[2] == "#": inv   = "#"
    if pL[3] == "#": stats = "#"
    else:
        for s in pL[3].split("*"):
            s = s.split(":")
            stats[s[0]] = float(s[1])
    pL = [[int(pL[0]), int(pL[1])], inv, stats]
    return({"b":bL, "e":eL, "p":pL})

def toScreen(p:list) -> tuple:
    return((p[0] - cameraPos[0],scr[1] - (p[1] - cameraPos[1])))

def sign(x) -> int:
    if x<0:return -1
    if x>0:return  1
    else:  return  0

def collisionTest(p1:list, p2:list, b) -> float:
        
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

def listProd(list1:list, list2:list) -> list:
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

    def __init__(self, shtr, pos, vel, dmg, stats) -> None:
        self.vel    = vel
        self.pos    = pos
        self.dmg    = (dmg * stats["bulletDmg%"] + stats["bulletDmgRaw"])
        self.stats  = stats
        self.origin = shtr
        pass

    def render(self) -> None:
        pygame.draw.circle(screen, (255,0,0), toScreen(self.pos), 3, 3)

    def delete(self) -> None:
        eList.remove(self)

    def update(self) -> None:
        if self.vel == [0,0]:self.delete()
        s = self.pos
        self.pos = [self.pos[0] + self.vel[0] * self.stats["bulletSpeed%"], self.pos[1] + self.vel[1] * self.stats["bulletSpeed%"]]
        self.vel = [self.vel[0], self.vel[1]]
        for b in bList:
            if collisionTest(s, self.pos, b):
                self.pos = s; self.vel = [0,0]

        for e in eList:
            try: s = e.size
            except:break

            if e.pos[0] - s[0] / 2 < self.pos[0] < e.pos[0] + s[0] / 2 and e.pos[1] - s[1] / 2 < self.pos[1] < e.pos[1] + s[1] / 2:
                e.coll(self)

class Player:

    def __init__(self, pos:list, inv:dict, stats:dict) -> None:
        self.pos    = pos
        self.vel    = [0,0]
        self.inv    = inv
        self.stats  = stats
        self.size   = [20,20]
        self.spr    = pygame.image.load("Player.png")
        self.bCldwn = 0.5 * fRate
        self.bC     = 0
        self.coin   = 0
        pass

    def update(self) -> None:
        s = self.pos
        if self.bC:self.bC -= 1
        if self.bC <0:self.bC = 0
        self.pos = [self.pos[0] + self.vel[0] * (self.stats["speed%"]), self.pos[1] + self.vel[1] * (self.stats["speed%"])]
        self.vel = [self.vel[0] * (1 - fric), self.vel[1] * (1 - fric)]
        for b in bList:
            if collisionTest(s, self.pos, b):
                self.pos = s; self.vel = [0,0]

    def render(self) -> None:
        screen.blit(self.spr, toScreen((self.pos[0] - self.size[0]/2,self.pos[1] + self.size[1]/2)))
        #pygame.draw.rect(screen, (255,255,127), (toScreen(self.pos)[0] - self.size[0] / 2,toScreen(self.pos)[1] - self.size[1] / 2, self.size[0], self.size[1]), 1)
    
    def move(self, inputMap:list) -> None:
        movL = listProd(inputMap, movm)
        for i in movL:
            self.vel = listAdd(self.vel, i)
    
    def shoot(self, inputMap:list) -> None:
        if not self.bC:
            bulletVel = [0,0]
            movL = listProd(inputMap, movm)
            for i in movL:
                bulletVel = listAdd(bulletVel, i)
            if abs(bulletVel[0]) + abs(bulletVel[1]) == 2:
                bulletVel = [bulletVel[0] * cos45, bulletVel[1] * cos45]
            eList.append(Projectile(self, self.pos, [bulletVel[0] * self.stats["bulletSpeed%"], bulletVel[1] * self.stats["bulletSpeed%"]], 1, self.stats))
            self.bC = self.bCldwn

    def coll(self, bull) -> None:
        if bull.origin == self:0
        else:print(bull.origin)

class Chaser:

    def __init__(self, pos:list) -> None:
        self.pos    = pos
        self.vel    = [0,0]
        self.size   = [25,25]
        self.lTable = {"Coin": [0.75, (1,2)]}
        pass

    def update(self) -> None:
        s = self.pos
        self.ai()
        self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]
        self.vel = [self.vel[0] * (1 - fric), self.vel[1] * (1 - fric)]
        for b in bList:
            if collisionTest(s, self.pos, b):
                self.pos = s; self.vel = [0,0]

    def render(self) -> None:
        pygame.draw.rect(screen, (255,127,127), (toScreen(self.pos)[0] - self.size[0] / 2,toScreen(self.pos)[1] - self.size[1] / 2, self.size[0], self.size[1]), 1)
    
    def ai(self) -> None:
        sight = True
        for b in bList:
            if collisionTest(self.pos, player.pos, b):sight = False
        if sight:
            dx = player.pos[0] - self.pos[0];dy = player.pos[1] - self.pos[1]
            if dx:a = math.atan(dy/dx)
            else: a = 10**100
            self.vel = [sign(dx)*0.05*(abs(dx)+5)*abs(math.cos(a)),sign(dy)*0.05*(abs(dy)+5)*abs(math.sin(a))]

    def die(self, killer:object) -> None:

        eList.remove(self)

        if killer == player:
            for d in self.lTable:
                r = random.randrange(0,100) / 100
                if self.lTable[d][0] >= r:
                    if type(self.lTable[d][1]) == tuple:
                        c = random.randrange(self.lTable[d][1][0], self.lTable[d][1][1] + 1) 
                    else:c=self.lTable[d][1]
                    for _ in range(c):
                        exec('eList.append('+ d + '(self.pos, [random.randrange(-5,5), random.randrange(-5,5)]))')

    def coll(self, bull) -> None:
        self.die(bull.origin)

class Coin:

    def __init__(self, pos:list, vel=[0,0]) -> None:
        self.pos = pos
        self.vel = vel
        pass

    def update(self) -> None:
        s = self.pos
        self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]
        self.vel = [self.vel[0] * (1 - fric), self.vel[1] * (1 - fric)]
        for b in bList:
            if collisionTest(s, self.pos, b):
                self.pos = s; self.vel = [-self.vel[0],-self.vel[1]]

        for e in eList:
            try: s = e.size
            except:break

            if e.pos[0] - s[0] / 2 < self.pos[0] < e.pos[0] + s[0] / 2 and e.pos[1] - s[1] / 2 < self.pos[1] < e.pos[1] + s[1] / 2:
                if e == player:
                    player.coin += 1
                    eList.remove(self)


    def render(self) -> None:
        pygame.draw.circle(screen, (255,255,0), toScreen(self.pos), 3, 3)
  
class Rook:

    def __init__(self, pos:list) -> None:
        self.pos      = pos
        self.vel      = [0,0]
        self.size     = [35,35]
        self.cC       = 0
        self.cCounter = 2 * fRate
        self.lTable   = [[.85, (3,5), "Coin"]]
        self.health   = 20
        pass

    def update(self) -> None:
        s = self.pos
        self.ai()
        self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]
        self.vel = [self.vel[0] * (1 - fric), self.vel[1] * (1 - fric)]
        for b in bList:
            if collisionTest(s, self.pos, b):
                self.pos = s; self.vel = [0,0]
        self.cC -= 1

    def render(self) -> None:
        pygame.draw.rect(screen, (127,127,127), (toScreen(self.pos)[0] - self.size[0] / 2,toScreen(self.pos)[1] - self.size[1] / 2, self.size[0], self.size[1]), 1)
    
    def ai(self):
        sight = True
        for b in bList:
            if collisionTest(self.pos, player.pos, b):sight = False
        if sight:
            dx = player.pos[0] - self.pos[0];dy = player.pos[1] - self.pos[1]
            slope = dy/dx
            if abs(slope) < 1 and self.cC <= 0:
                self.vel = [50 * sign(dx),0];self.cC = self.cCounter
            elif self.cC <= 0:
                self.vel = [0, 50 * sign(dy)];self.cC = self.cCounter

    def die(self, killer:object) -> None:

        eList.remove(self)

        if killer == player:
            for d in range(len(self.lTable)):
                r = random.randrange(0,100) / 100
                if self.lTable[d][0] >= r:
                    if type(self.lTable[d][1]) == tuple:
                        c = random.randrange(self.lTable[d][1][0], self.lTable[d][1][1] + 1) 
                    else:c=self.lTable[d][1]
                    for _ in range(c):
                        exec('eList.append('+ self.lTable[d][2] + '(self.pos, [random.randrange(-2,2) * 10, random.randrange(-2,2) * 10]))')

    def coll(self, bull) -> None:
        
        self.health -= bull.dmg

        if self.health <= 0:
            self.die(bull.origin)

pygame.display.set_caption("[D-9]")
screen = pygame.display.set_mode(scr)
fRate = 30

player = Player([0,0], {}, defstats)

print(getLvlData("l1.d9"))

while 1: # main loop

    #reset

    bList = []; eList = []

    #load level

    lvlD8a = getLvlData(lvlList[lvlInd])

    bList = lvlD8a["b"]

    if lvlD8a["p"][1] != "#":
        player.inv = lvlD8a["p"][1]
    if lvlD8a["p"][2] != "#":
        player.stats = lvlD8a["p"][2]

    player.pos = lvlD8a["p"][0]

    eList.append(player)

    for e in lvlD8a["e"]:
        exec(f"eList.append({e[0]}({e[1]}))")

    inLevel = True

    while inLevel: # inside level loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    pygame.quit() # pause at some point
                if k == pygame.K_r:
                    inLevel = False
                if k == pygame.K_p:
                    if lvlInd:
                        lvlInd -= 1
                    inLevel = False
                if k == pygame.K_n:
                    if lvlInd != len(lvlList) - 1:
                        lvlInd += 1
                    inLevel = False

        k = pygame.key.get_pressed()

        if k[pygame.K_c]:
            for e in eList:
                if e.__class__ == Chaser:
                    e.die(player)

        arrows = [int(k[pygame.K_UP]),int(k[pygame.K_LEFT]),int(k[pygame.K_DOWN]),int(k[pygame.K_RIGHT])]
        wasd = [int(k[pygame.K_w]),int(k[pygame.K_a]),int(k[pygame.K_s]),int(k[pygame.K_d])]

        cameraPos = [player.pos[0] - int(scr[0] / 2), player.pos[1] - int(scr[1] / 2)]

        for e in eList:
            e.update()
            if e == player:
                if 1 not in arrows:
                    player.bC = 0

        player.move(wasd)
        if arrows != [0,0,0,0]:player.shoot(arrows)

        screen.fill((0,0,0))

        for e in eList:
            e.render()

        for b in bList:
            pygame.draw.line(screen, (255,255,255), toScreen(b[0]), toScreen(b[1]))

        pygame.display.update()
        sleep(1/fRate)