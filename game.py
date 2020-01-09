import pygame
import datetime
import os
import time
from character import *
from pygame.locals import *

H = 480
W = 640
DAMAGE = 6
MSCOUNT = 60
PORT = 12345


class Game:
    def __init__(self, player1, char1,ip1, player2, char2, ip2,position):
        pygame.init()
        self.ownName = player1
        self.enemyName = player2
        self.willPrint = False

        self.damageLock = Lock()
        self.damagePackCount = 0
        self.sentDamagePacks = []
        self.ackedDamagePacks = []

        self.ms = -1
        self.msPacketTime = datetime.datetime.now()
        self.msFrameCount = MSCOUNT
        self.msPacketId = 0
        self.msWaitLock = Lock()
        self.waitingmsAck = False

        self.hostIP = ip1
        self.enemyIP = ip2
        self.atomicDamage = 1

        imagePath = "/"
        self.bg = pygame.image.load(os.getcwd() + imagePath + "bg.jpg")

        self.texts = []
        self.characters = list()
        if position:
            self.characters.append(Character(char1, False, 50, 50))
            self.characters.append(Character(char2, True, 430, 50))
        else:
            self.characters.append(Character(char1, True, 430, 50))
            self.characters.append(Character(char2, False, 50, 50))

    def physics(self):
        wP = list()
        for c in self.characters:
            # Gravity
            if c.position[1] < H - 62 - 15:
                c.velocityLock.acquire()
                c.velocity[1] += 1
                c.velocityLock.release()
            c.move()
            b = c.limitPosition(H, W)
            willPrintThisCharacter = c.velocity[0] != 0 or c.velocity[1] != 0 or b or c.hitState > 0
            wP.append(willPrintThisCharacter)
            if willPrintThisCharacter:
                c.frameCount += 1
            if c.hitState > 0:
                c.hitState -= 1
        self.willPrint = (wP[0] or wP[1])

    def simulateForTime(self, px, py, vx, vy, t, hitState):
        i = 0
        hitState -= t
        if hitState < 0:
            hitState = 0
        while i < t:
            if py < H - 62:
                vy += 1
            px += vx
            py += vy
            i += 1
        return px, py, vx, vy, hitState

    def update(self, px, py, vx, vy, hitState):
        # This will be called by UDP listener thread
        self.characters[1].update(px, py, vx, vy, hitState)

    def sendDamagePacket(self, id):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        myMessage = "[" + self.ownName + "," + self.hostIP + "," + "damage" + "," + str(id) + "]"
        s.sendto(bytes(myMessage, 'utf-8'), (self.enemyIP, PORT))
        self.msPacketTime = datetime.datetime.now()

        s.close()

    def sendPacket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        FC = self.characters[0].frameCount
        myMessage = "[" + self.ownName + "," + self.hostIP + "," + "update" + "," + str(
            self.characters[0].hitState) + "," + str(
            self.characters[0].position[0]) + "," + str(self.characters[0].position[1]) + "," + str(
            self.characters[0].velocity[0]) + "," + str(self.characters[0].velocity[1]) + "," + str(
            FC) + "]"
        s.sendto(bytes(myMessage, 'utf-8'), (self.enemyIP, PORT))
        s.close()

    def sendmsPacket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.msPacketId += 1
        myMessage = "[" + self.ownName + "," + self.hostIP + "," + "ms" + "," + str(self.msPacketId) + "]"
        s.sendto(bytes(myMessage, 'utf-8'), (self.enemyIP, PORT))
        self.msPacketTime = datetime.datetime.now()
        s.close()
        self.msWaitLock.acquire()
        self.waitingmsAck = True
        self.msWaitLock.release()

    def printScreen(self):
        # Background
        self.screen.blit(self.bg, (0, 0))
        font = pygame.font.SysFont(None, 24)
        msFont = pygame.font.SysFont(None, 18)

        MS = msFont.render(str(int(self.ms)) + " ms", True, Color('black'))
        PName1 = font.render(str(self.ownName), True, Color('black'))
        PName2 = font.render(str(self.enemyName), True, Color('black'))
        HPRect1 = Rect(20, 20, 2 * self.characters[0].HP, 20)
        HPRect2 = Rect(420, 20, 2 * self.characters[1].HP, 20)

        self.screen.blit(PName1, (25,45))
        self.screen.blit(PName2, (425,45))
        self.screen.blit(MS, (25,60))
        if self.characters[0].HP > 60:
            pygame.draw.rect(self.screen, Color('green'), HPRect1)
        elif self.characters[0].HP > 20:
            pygame.draw.rect(self.screen, Color('yellow'), HPRect1)
        else:
            pygame.draw.rect(self.screen, Color('red'), HPRect1)

        if self.characters[1].HP > 60:
            pygame.draw.rect(self.screen, Color('green'), HPRect2)
        elif self.characters[1].HP > 20:
            pygame.draw.rect(self.screen, Color('yellow'), HPRect2)
        else:
            pygame.draw.rect(self.screen, Color('red'), HPRect2)

        # Characters
        for char in self.characters:
            char.draw(self.screen)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
        pygame.display.set_caption("SHOW ME WHAT YOU GOT")
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_w:
                        self.characters[0].jump()
                        self.sendPacket()
                    elif event.key == K_d:
                        self.characters[0].right()
                        self.sendPacket()
                    elif event.key == K_a:
                        self.characters[0].left()
                        self.sendPacket()
                    elif event.key == K_y:
                        running = False
                    elif event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_k:
                        self.characters[0].hitState = DAMAGE
                        self.sendPacket()
                elif event.type == KEYUP:
                    if (event.key == K_d and self.characters[0].direction == False) or (
                            event.key == K_a and self.characters[0].direction == True):
                        self.characters[0].stop()
                        self.sendPacket()
            self.physics()
            for d in self.sentDamagePacks:
                self.sendDamagePacket(d)
            if self.willPrint:
                self.calculateDamage()
                self.printScreen()
                self.willPrint = False
            if self.characters[0].HP==0 or self.characters[1].HP==0:
                time.sleep(3)
                running=False
            self.msFrameCount -= 1
            if self.msFrameCount == 0:
                self.sendmsPacket()
                self.msFrameCount = MSCOUNT
            pygame.display.update()
            clock.tick(60)
        pygame.quit()

    def calculateDamage(self):
        if self.characters[1].hitState > 0:
            r1 = self.characters[1].get_Rect_Weapon()
            r2 = self.characters[0].get_Rect_Health()
            if r1.colliderect(r2):
                self.characters[0].HP -= self.atomicDamage
                self.damagePackCount += 1
                self.sendDamagePacket(self.damagePackCount)
                self.damageLock.acquire()
                self.sentDamagePacks.append(self.damagePackCount)
                self.damageLock.release()
