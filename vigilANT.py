#!/usr/bin/env python
# -*- coding: utf-8 *-*

import pygame
from pygame.locals import K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN, K_RIGHT, K_SPACE, K_RETURN, K_ESCAPE, KEYUP, KEYDOWN, QUIT
from random import randint, randrange
import os.path as path
from glob import glob

X = 800
Y = 600
FPS = 30

pygame.init()
pygame.mixer.init()

FONT = pygame.font.Font("pixel.ttf", 20)

KEYS = K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN, K_RIGHT, K_SPACE, K_RETURN, K_ESCAPE
SQUARE = 10
TIMER = pygame.time.Clock()
tick = 0

BLACK = (0,0,0)
GREY = (128,128,128)
WHITE = (255,255,255)
RED = (200,0,0)
GRASSGREEN = (0,200,0)
WATERBLUE = (0,0,200)

pygame.display.set_caption('gANgsTer')
DISPLAY = pygame.display.set_mode((X, Y))

#SPRITES = { path.basename(path.splitext(s)[0]) : pygame.image.load(s).convert_alpha()
#            for s in glob("*.png") }
#SOUNDS = { path.basename(path.splitext(s)[0]) : pygame.mixer.Sound(str(s))
#            for s in glob("*.wav") }

class Dot(pygame.sprite.Sprite):
	def __init__(self, x, y, col=GREY, sqr=SQUARE):
		super(Dot, self).__init__()
		self.sqr = sqr
		self.color = col

		self.image = pygame.Surface((self.sqr, self.sqr))
		self.image.fill(self.color)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
	def update(self):
		pass

class Ant(Dot):
	def __init__(self, x, y, colo=BLACK):
		super(Ant, self).__init__(x, y, colo)
		self.life = 10
	def update(self, player, sugar, water):
		pass
		# Ant AI ...
		# find nearest sugar... and walk to it... while avoiding water

class PlayerAnt(Ant):
	def __init__(self, x, y):
		super(PlayerAnt, self).__init__(x, y, RED)
		self.STEP = 5
	def update(self, events):
		pass
		# handle player input...
		if K_UP in events: self.rect.y -= self.STEP
		if K_LEFT in events: self.rect.x -= self.STEP
		if K_DOWN in events: self.rect.y += self.STEP
		if K_RIGHT in events: self.rect.x += self.STEP
		if self.rect.x <   10: self.rect.x = 10
		if self.rect.y <   10: self.rect.y = 10
		if self.rect.x > X-20: self.rect.x = X-20
		if self.rect.y > Y-20: self.rect.y = Y-20

class Water(Dot):
	def __init__(self, x, y):
		super(Water, self).__init__(x, y, col=WATERBLUE)
		self.fade = 0
	def update(self):
		self.fade += 5
		if self.fade >= 200:
			self.kill()
			SUGAR.add(Sugar(self.rect.x, self.rect.y))
		else:
			self.image.fill((self.fade,self.fade,200)) # turns from blue to white

class Sugar(Dot):
	def __init__(self, x, y):
		super(Sugar, self).__init__(x, y, WHITE)

def rain(player, water):
	if randint(1,1000) < 25:
		xx = PLAYER.rect.x
		while abs(PLAYER.rect.x-xx) < 30:
			xx = randint(10,X-10)
		yy = PLAYER.rect.y
		while abs(PLAYER.rect.y-yy) < 30:
			yy = randint(10,Y-10)
		water.add(Water(xx,yy))


PLAYER = PlayerAnt(X/2, Y/2)
PLAYERGROUP = pygame.sprite.Group(PLAYER)
ANTS = pygame.sprite.Group()
WATER = pygame.sprite.Group()
SUGAR = pygame.sprite.Group()


# helper functions
#getsurface = lambda s: SPRITES[s]
#getwav = lambda s: SOUNDS[s] if s in SOUNDS else pygame.mixer.Sound(str(s)+'.wav')
#playsound = lambda s: getwav(s).play()

run = True
events = []

# main game loop
while run:

	DISPLAY.fill(GRASSGREEN)

	for e in pygame.event.get():
		if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
			run = False
			continue

		if e.type not in [KEYDOWN, KEYUP] or e.key not in KEYS:
			continue

		if e.type == KEYDOWN:
			events.append(e.key)
		elif e.key in events:
			events.remove(e.key)

	#label = FONT.render(str(slapcnt), 1, (255, 0, 0))
	#pos = label.get_rect(left=16, top=0)
	#DISPLAY.blit(label, pos)

	PLAYERGROUP.update(events)
	ANTS.update(PLAYER, SUGAR, WATER)
	WATER.update()
	SUGAR.update()

	rain(PLAYER, WATER)
	#ants(ANTS)

	ANTS.draw(DISPLAY)
	SUGAR.draw(DISPLAY)
	WATER.draw(DISPLAY)
	PLAYERGROUP.draw(DISPLAY)

	print WATER

	TIMER.tick(FPS)
	pygame.display.update()
	tick = (tick % (FPS*100)) + 1 # avoid overflow

pygame.quit()

