#!/usr/bin/env python
# -*- coding: utf-8 *-*

import pygame
from pygame.locals import K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN, K_RIGHT, K_SPACE, K_RETURN, K_ESCAPE, KEYUP, KEYDOWN, QUIT
from random import randint, randrange
import os.path as path
from glob import glob
import math

X = 800
Y = 600
FPS = 30

pygame.init()
pygame.mixer.init()

FONT = pygame.font.Font("pixel.ttf", 20)
BIGFONT = pygame.font.Font("pixel.ttf", 100)

KEYS = K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN, K_RIGHT, K_SPACE, K_RETURN, K_ESCAPE
SQUARE = 10
WATERSQR = SQUARE
SUGARSQR = SQUARE - 2
ANTSQR = SQUARE
SUGAR2COLLECT = 1
PLAYERSPEED = 4
TIMER = pygame.time.Clock()
tick = 0

BLACK = (0,0,0)
GREY = (128,128,128)
WHITE = (255,255,255)
RED = (200,0,0)
GRASSGREEN = (0,180,0)
WATERBLUE = (0,0,180)

pygame.display.set_caption('gANgsTer')
DISPLAY = pygame.display.set_mode((X, Y))

SPRITES = { path.basename(path.splitext(s)[0]) : pygame.image.load(s).convert_alpha()
            for s in glob("*.png") }
SOUNDS = { path.basename(path.splitext(s)[0]) : pygame.mixer.Sound(str(s))
            for s in glob("*.ogg") }

# helper functions
getsurface = lambda s: SPRITES[s]
getwav = lambda s: SOUNDS[s] if s in SOUNDS else pygame.mixer.Sound(str(s)+'.wav')
playsound = lambda s: getwav(s).play()
dist = lambda r1, (r2x,r2y): math.sqrt( (r1.x-r2x)**2 + (r1.y-r2y)**2 )
def draw_text(text, font, color, pos):
	label = font.render(text, 1, color)
	posi = label.get_rect(center = pos)
	DISPLAY.blit(label, posi)

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
		self.life = 5
	def update(self, player, sugar, water):
		pass
		# Ant AI ...
		# find nearest sugar... and walk to it... while avoiding water

class PlayerAnt(Ant):
	def __init__(self, x, y):
		super(PlayerAnt, self).__init__(x, y, RED)
		self.STEP = PLAYERSPEED
		self.sugar = 0
		self.LOSER = False
	def update(self, events):
		if not self.LOSER and self.life > 0:
			# movement
			newrect = self.rect.copy()
			if   K_UP    in events: newrect.move_ip((0,-self.STEP))
			elif K_DOWN  in events: newrect.move_ip((0,self.STEP))
			if   K_LEFT  in events: newrect.move_ip((-self.STEP,0))
			elif K_RIGHT in events: newrect.move_ip((self.STEP,0))
			if not newrect.colliderect(ROCKET.rect):
				self.rect = newrect
			# boundaries
			if self.rect.x < 10:
				self.rect.x = 10
			if self.rect.y < 10:
				self.rect.y = 10
			if self.rect.x > X-20:
				self.rect.x = X-20
			if self.rect.y > Y-20:
				self.rect.y = Y-20
			# rocket
			if self.rect.x < ROCKET.rect.right and self.rect.y < ROCKET.rect.top:
				pass
		if not self.LOSER and self.life <= 0:
			self.LOSER = True
			playsound("loser")

class Rocket(pygame.sprite.Sprite):
	def __init__(self):
		super(Rocket, self).__init__()
		self.image = getsurface('rocket-desperate')
		self.rect = self.image.get_rect()
		self.rect.center = (80, Y/4*3)
		self.fire = RocketFire(self.rect.centerx+1, self.rect.bottom-5)
		self.TAKEOFF = False
		self.FIRESPAWNED = False
	def update(self, player):
		if not self.TAKEOFF and player.sugar >= SUGAR2COLLECT:
			self.TAKEOFF = True
		elif not self.FIRESPAWNED and self.TAKEOFF:
			self.image = getsurface('rocket-happy')
			ROCKETGROUP.add(self.fire, layer=-1)
			playsound('rocketlaunch')
			self.TAKEOFF = False
			self.FIRESPAWNED = True
		elif self.FIRESPAWNED:
			self.rect.y -= 10
			self.fire.rect.y -= 10

class MultiSprite(pygame.sprite.Sprite):
	def __init__(self, path, rx, ry):
		super(MultiSprite, self).__init__()
		self.sprite = getsurface(path)
		self.rx, self.ry = rx, ry

	def draw2surface(self, target, x, y, pX=0, pY=0):
		subsprite_rect = (self.rx*x, self.ry*y, self.rx, self.ry)
		topleft = (pX, pY)
		target.blit(self.sprite, topleft, subsprite_rect)

class RocketFire(MultiSprite):
	def __init__(self, offX, offY):
		super(RocketFire, self).__init__("rocketflame", 88, 132)
		self.frame = 0
		self.image = pygame.Surface((self.rx, self.ry)).convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.center = (offX,offY)
		self.update(None)

	def update(self, _player):
		self.frame = (self.frame + 1) % 8
		self.image.fill((0,0,0,0))
		self.draw2surface(self.image, self.frame, 0)

class Water(Dot):
	def __init__(self, x, y):
		super(Water, self).__init__(x, y, col=WATERBLUE, sqr=10)
		self.fade = 0
	def update(self):
		self.fade += 5
		if self.fade >= 255:
			self.kill()
			if randint(1,100) <= 10: # only add sugar with chance of 10 %
				off = (WATERSQR - SUGARSQR) / 2
				SUGAR.add(Sugar(self.rect.x+off, self.rect.y+off))
		else:
			#if self.fade >= 200:
			#	self.image.fill((self.fade,self.fade,self.fade))
			#else:
			self.image.fill((self.fade,self.fade,200)) # turns from blue to white

class Sugar(Dot):
	def __init__(self, x, y):
		super(Sugar, self).__init__(x, y, col=WHITE, sqr=8)

def rain(player, water):
	if randint(1,100) < 20:
		xx = PLAYER.rect.x
		yy = PLAYER.rect.y
		while dist(PLAYER.rect, ((xx,yy))) < 50 or dist(ROCKET.rect, ((xx,yy))) < 10:
			xx = randint(10,X-20)
			yy = randint(10,Y-20)
		water.add(Water(xx,yy))


PLAYER = PlayerAnt(X/2, Y/2)
PLAYERGROUP = pygame.sprite.Group(PLAYER)
ANTS = pygame.sprite.Group()
WATER = pygame.sprite.Group()
SUGAR = pygame.sprite.Group()
ROCKET = Rocket()
ROCKETGROUP = pygame.sprite.LayeredUpdates(ROCKET)


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

	### UPDATE
	PLAYERGROUP.update(events)
	ANTS.update(PLAYER, SUGAR, WATER)
	WATER.update()
	SUGAR.update()
	ROCKETGROUP.update(PLAYER)

	### TICK
	if not PLAYER.LOSER:
		for _ in range(randint(1,5)):
			rain(PLAYER, WATER)
	#ants(ANTS) # maybe spawn some ants
	PLAYER.life -= len(pygame.sprite.groupcollide(WATER, PLAYERGROUP, True, False))
	PLAYER.sugar += len(pygame.sprite.groupcollide(SUGAR, PLAYERGROUP, True, False))

	### DRAW
	ANTS.draw(DISPLAY)
	SUGAR.draw(DISPLAY)
	WATER.draw(DISPLAY)
	PLAYERGROUP.draw(DISPLAY)
	ROCKETGROUP.draw(DISPLAY)
	draw_text("Lives: "+str(PLAYER.life), FONT, (255,0,0), (60, 15))
	draw_text("Sugar: "+str(PLAYER.sugar), FONT, (255,0,0), (60, 30))
	if PLAYER.LOSER:
		draw_text("LOSER", BIGFONT, (255,0,0), (X/2, Y/2))

	TIMER.tick(FPS)
	pygame.display.update()
	tick = (tick % (FPS*100)) + 1 # avoid overflow

pygame.quit()

