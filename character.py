import pygame
from pygame.locals import *
import os
from threading import Lock
import socket

JUMP = -15
WALK = 5
HEALTHHITBOX=40
WEAPONHITBOX=43


class Character:
    def __init__(self, char_class, direction=False, pos_x=50, pos_y=50, vel_x=0,
                 vel_y=0):
        self.classs = char_class
        self.positionLock = Lock()
        self.velocityLock = Lock()
        self.direction = direction

        self.frameCount = 0

        self.HP = 100

        imagePath = "/sprites/"
        self.spritePath = ""

        if char_class == "mage":
            self.spritePath = os.getcwd() + imagePath + "Mage/mage"
        elif char_class == "warrior":
            self.spritePath = os.getcwd() + imagePath + "Warrior/warrior"
        elif char_class == "rogue":
            self.spritePath = os.getcwd() + imagePath + "Rogue/rogue"

        self.normalImage = pygame.image.load(self.spritePath + ".png")
        self.hitImage = pygame.image.load(self.spritePath + "-attack.png")

        self.hitState = 0  # Not hitting

        self.jumpCount = 0

        self.position = list()
        self.position.append(pos_x)
        self.position.append(pos_y)

        self.velocity = list()
        self.velocity.append(vel_x)
        self.velocity.append(vel_y)

    def move(self):
        self.positionLock.acquire()
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.positionLock.release()

    def limitPosition(self, H, W):
        ret = False
        # Limit right
        self.positionLock.acquire()
        self.velocityLock.acquire()
        if self.position[0] + 62 > W:
            self.position[0] = W - 62
            self.velocity[0] = 0
            ret = True
        # Limit left
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0
            ret = True
        # Limit ground
        if self.position[1] + 62 + 15 > H:
            self.position[1] = H - 62 - 15
            self.velocity[1] = 0
            ret = True

        if self.position[1] == H - 62 - 15:
            self.jumpCount = 0

        self.velocityLock.release()
        self.positionLock.release()

        return ret

    def draw(self, surface):
        #pygame.draw.rect(surface, Color('red'), self.get_Rect_Health())
        #pygame.draw.rect(surface, Color('blue'), self.get_Rect_Weapon())
        if self.hitState > 0:
            surface.blit(pygame.transform.flip(self.hitImage, self.direction, False), self.position)
        else:
            surface.blit(pygame.transform.flip(self.normalImage, self.direction, False), self.position)

    def jump(self):
        if self.jumpCount < 2:
            self.push(0, JUMP)
            self.jumpCount += 1

    def stop(self):
        self.updateVelocity(0, self.velocity[1])

    def right(self):
        self.direction = False
        self.updateVelocity(WALK, self.velocity[1])

    def left(self):
        self.direction = True
        self.updateVelocity(-1 * WALK, self.velocity[1])

    def push(self, x, y):
        self.velocityLock.acquire()
        self.velocity[0] += x
        self.velocity[1] += y
        self.velocityLock.release()

    def update(self, px, py, vx, vy, hitSt):
        self.updatePosition(px, py)
        self.updateVelocity(vx, vy)
        self.hitState = hitSt

    def updatePosition(self, px, py):
        self.positionLock.acquire()
        self.position[0] = px
        self.position[1] = py
        self.positionLock.release()

    def updateVelocity(self, vx, vy):
        self.velocityLock.acquire()
        self.velocity[0] = vx
        if vx < 0:
            self.direction = True
        elif vx > 0:
            self.direction = False
        self.velocity[1] = vy
        self.velocityLock.release()

    def get_velocity(self):
        return (self.velocity[0], self.velocity[1])

    def get_position(self):
        return (self.position[0], self.position[1])

    def get_Rect_Health(self):
        if self.direction==False: # Looking right
            return Rect(self.position[0],self.position[1],HEALTHHITBOX,62)
        else:
            if self.hitState > 0:
                return Rect(self.position[0]+83-HEALTHHITBOX,self.position[1],HEALTHHITBOX,62)
            else:
                return Rect(self.position[0]+62-HEALTHHITBOX,self.position[1],HEALTHHITBOX,62)

    def get_Rect_Weapon(self):
        if self.hitState > 0:
            if self.direction==False:
                return Rect(self.position[0]+HEALTHHITBOX, self.position[1],WEAPONHITBOX,62)
            else:
                return Rect(self.position[0],self.position[1],WEAPONHITBOX,62)
        else:
            return Rect(0,0,0,0)
