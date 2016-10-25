#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pygame
from pygame import locals as pg
import random

from jelly.util import DX, DY


class LadderSprite(pygame.sprite.Sprite):
    def __init__(self, frames, (x, y), steps):
        super(LadderSprite, self).__init__()
        self.image = pygame.Surface((32, 480))
        self.image.set_colorkey((0, 0, 0))
        for step, frame in enumerate(steps):
            self.image.blit(frames[frame], (0, 32 * step + 16))
        self.rect = self.image.get_rect()
        self.rect.midbottom = (20 + 20 * x, 32 + 12 * y)
        self.depth = self.rect.bottom
        self.step = 0


    def update(self):
        self.step += 1
        if self.step % 4 == 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect.move_ip(0, -3)
        if self.step > 24:
            self.kill()

    def death_animation(self):
        pass

    def set_animation(self, animation):
        pass


class Ladder2Sprite(LadderSprite):

    def __init__(self, frames, (x, y), steps):
        super(Ladder2Sprite, self).__init__(frames, (x,y), steps)
        self.rect.midbottom = (20 + 20 * x, 32 + 12 * y - 48)
        self.depth -= 1

    def update(self):
        self.step += 1
        if self.step % 4 == 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.step = 0
        if self.rect.bottom < self.depth:
            self.rect.move_ip(0, 4)


class MobSprite(pygame.sprite.Sprite):
    def __init__(self, frames, (x, y), steps):
        super(MobSprite, self).__init__()
        self.steps = steps
        self.frames = frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.frame = random.randint(0, len(self.steps))
        self.rect.topleft = (4 + 20 * x, 12 * y)
        self.depth = self.rect.bottom
        self.animations = [self.spawn_animation()]

    def update(self):
        self.frame = (self.frame + 1) % len(self.steps)
        self.image = self.frames[self.steps[self.frame]]
        if self.animations:
            try:
                self.animations[0].next()
            except StopIteration:
                del self.animations[0]

    def walk_animation(self, direction):
        for frame in range(4):
            yield None
            self.rect.move_ip((DX[direction]*5, DY[direction]*3))
            self.depth = self.rect.bottom

    def death_animation(self):
        for step in range(3):
            yield None
        image = self.image.copy()
        for step in xrange(8):
            yield None
            self.image = pygame.transform.scale(image, (32+8*step, max(2, 32-8*step)))
            self.rect.move_ip(0, 1)
            rect = self.image.get_rect()
            rect.center = self.rect.center
            self.rect = rect
            self.image.set_alpha(192-step*32)
        self.kill()

    def spawn_animation(self):
        self.rect.move_ip(0, -12)
        for step in xrange(4):
            self.image = self.image.copy()
            self.image.set_alpha(0)
            yield None
        for step in xrange(4):
            self.image = self.image.copy()
            self.image.set_alpha(step * 48)
            yield None
        self.rect.move_ip(0, 2)
        yield None
        self.rect.move_ip(0, 4)
        yield None
        self.rect.move_ip(0, 6)


    def spawner_animation(self):
        yield None
        self.rect.move_ip(0, -5)
        yield None
        self.rect.move_ip(0, 3)
        yield None
        self.rect.move_ip(0, 3)
        yield None
        self.rect.move_ip(0, 3)
        yield None
        self.rect.move_ip(0, -4)
        yield None
        self.rect.move_ip(0, -5)
        yield None
        self.rect.move_ip(0, 3)
        yield None
        self.rect.move_ip(0, 3)
        yield None
        self.rect.move_ip(0, 3)
        yield None
        self.rect.move_ip(0, -4)

    def open_animation(self):
        self.depth -= 2
        for step in range(2):
            yield None
        self.rect.move_ip(0, -8)
        yield None
        self.rect.move_ip(0, 2)
        yield None
        self.rect.move_ip(0, 6)
        self.steps = [17]
        yield None
        self.steps = [18]
        yield None
        self.steps = [19]
        yield None
        yield None
        yield None
        yield None
        self.kill()

    def stand_animation(self, direction):
        yield None

    def attack_animation(self, direction):
        self.rect.move_ip((DX[direction]*4, DY[direction]*2-2))
        yield None
        self.rect.move_ip((DX[direction]*6, DY[direction]*4))
        yield None
        self.rect.move_ip((-DX[direction]*3, -DY[direction]*1+2))
        yield None
        self.rect.move_ip((-DX[direction]*7, -DY[direction]*5))
        self.depth = self.rect.bottom

    def set_animation(self, animation):
        self.animations.append(animation)
        self.update()


class PlayerSprite(MobSprite):
    def __init__(self, frames, (x, y), steps):
        super(PlayerSprite, self).__init__(frames, (x, y), [])
        self.direction = 0
        self.frames = frames
        self.image = self.frames[0]
        self.animations = [self.stand_animation(self.direction)]
        self.rect = self.image.get_rect()
        self.rect.move_ip(4 + 20 * x, 12 * y)
        self.depth = self.rect.bottom
        self.frame = 0

    def update(self):
        if self.animations:
            try:
                self.animations[0].next()
            except StopIteration:
                del self.animations[0]

    def walk_animation(self, direction):
        frames = [
            [0, 0, 1, 1, 2, 2, 3, 3],
            [10, 10, 11, 11, 12, 12, 13, 13],
            [20, 20, 21, 21, 22, 22, 23, 23],
            [30, 30, 31, 31, 32, 32, 33, 33],
            [40, 40, 41, 41, 42, 42, 43, 43],
            [50, 50, 51, 51, 52, 52, 53, 53],
            [60, 60, 61, 61, 62, 62, 63, 63],
            [70, 70, 71, 71, 72, 72, 73, 73],
        ][direction]
        for step in xrange(4):
            yield None
            self.frame = (self.frame + 1) % len(frames)
            self.rect.move_ip((DX[direction]*5, DY[direction]*3))
            self.image = self.frames[frames[self.frame]]
            self.depth = self.rect.bottom

    def attack_animation(self, direction):
        yield None
        self.rect.move_ip((DX[direction]*4, DY[direction]*2-2))
        self.image = self.frames[[4, 14, 24, 34, 44, 54, 64, 74][direction]]
        yield None
        self.rect.move_ip((DX[direction]*6, DY[direction]*4))
        yield None
        self.rect.move_ip((-DX[direction]*3, -DY[direction]*1+2))
        self.image = self.frames[[5, 15, 25, 35, 45, 55, 65, 75][direction]]
        yield None
        self.rect.move_ip((-DX[direction]*7, -DY[direction]*5))
        self.depth = self.rect.bottom


    def stand_animation(self, direction):
        yield None
        frame = [0, 10, 20, 30, 40, 50, 60, 70][direction]
        self.image = self.frames[frame]

    def wait_animation(self, direction):
        for step in xrange(4):
            yield None
            frame = [0, 10, 20, 30, 40, 50 ,60, 70][direction]
            self.image = self.frames[frame]

    def finish_animation(self):
        for step in xrange(8):
            yield None
        frames = [40, 40, 41, 41, 42, 42, 43, 43]
        for ladder in xrange(8):
            for step in xrange(4):
                yield None
                self.frame = (self.frame + 1) % len(frames)
                self.rect.move_ip(0, -3)
                self.image = self.frames[frames[self.frame]]


class Shadow(pygame.sprite.Sprite):
    def __init__(self, frames, owner):
        super(Shadow, self).__init__()
        self.image = frames[9].copy()
        self.alpha = 112
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect()
        self.owner = owner

    def update(self):
        if not self.owner.alive():
            self.alpha -= 16
            if self.alpha <= 0:
                self.kill()
            self.image.set_alpha(self.alpha)
        self.rect.midbottom = (self.owner.rect.centerx, self.owner.depth)

class Vision(pygame.sprite.DirtySprite):
    def __init__(self, owner, radius):
        super(Vision, self).__init__()
        self.owner = owner
        self.blendmode = pg.BLEND_RGBA_MIN
        self.dirty = 2
        self.images = {}
        for r in xrange(48, 81):
            self.images[r] = self.get_image(r)
        self.radius = radius
        self.set_radius(radius)

    def set_radius(self, radius):
        self.current_radius = radius
        self.image = self.images[radius]
        self.rect = self.image.get_rect()
        self.rect.center = self.owner.rect.center

    def get_image(self, radius):
        image = pygame.Surface((radius*5/2, radius*2), pg.SRCALPHA)
        image.fill((255, 255, 255, 255))
        for r in xrange(radius, radius-25, -1):
            pygame.draw.ellipse(
                    image,
                    (255, 255, 255, max(0, min(255, (r-radius+25) * 10))),
                    (radius*5/4-r*5/4, radius-r, 2*r*5/4, 2*r), 0)
        return image

    def update(self):
        if self.current_radius > self.radius:
            self.set_radius(max(self.current_radius - 4, self.radius))
        elif self.current_radius < self.radius:
            self.set_radius(min(self.current_radius + 4, self.radius))
        self.rect.center = self.owner.rect.center

class Dust(pygame.sprite.Sprite):
    steps = [26, 27, 28, 29]
    speed = 3

    def __init__(self, frames, (x, y), delay=0):
        super(Dust, self).__init__()
        self.animation = self.dust_animation(frames, delay)
        self.image = frames[self.steps[0]].copy()
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.depth = self.rect.bottom + 2
        for step, frame in enumerate(self.steps):
            frames[frame].set_alpha(192 - 32 * step)

    def dust_animation(self, frames, delay):
        for step in xrange(delay):
            yield None
        for frame in self.steps:
            self.image = frames[frame]
            for step in xrange(random.randrange(
                                max(0, self.speed-2),
                                max(0, self.speed+3)
                            )):
                yield None

    def update(self):
        try:
            self.animation.next()
        except StopIteration:
            self.kill()

class Gib(pygame.sprite.Sprite):
    def __init__(self, frames, (x, y), delay=0, color=0):
        super(Gib, self).__init__()
        self.image = frames[38].copy()
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.depth = self.rect.bottom + 2
        self.animation = self.gib_animation(frames, delay, color)

    def gib_animation(self, frames, delay, color):
        dx = random.randint(-3, 3)
        dy = random.randint(-5, 1)
        steps = random.randint(4, 8)
        for step in xrange(delay):
            yield None
        self.image = frames[38+color*10 + random.randint(0, 1)].copy()
        for step in xrange(steps):
            self.image.set_alpha(192*(steps-step)/steps)
            self.rect.move_ip(dx, dy)
            dy += 1
            yield None

    def update(self):
        try:
            self.animation.next()
        except StopIteration:
            self.kill()
