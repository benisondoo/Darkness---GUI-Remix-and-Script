#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import weakref

import pygame
from pygame import locals as pg

from jelly import sprites
from jelly import resource
from jelly import message


class SortedUpdates(pygame.sprite.RenderUpdates):
    """Sprite group with a depth for controlling drawing order."""

    def sprites(self):
        return sorted(self.spritedict.keys(),
                      key=lambda sprite: getattr(sprite, "depth", 0))


class Display(object):
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption('DARKNESS')
        self.real_screen = pygame.display.set_mode((640, 480))
        self.screen = pygame.Surface(self.real_screen.get_size())
        self.first_draw = True
        self.tiles = resource.load_tiles('jelly.png', 32, 32)
        pygame.display.set_icon(self.tiles[-1])
        for tile in self.tiles[36:40]:
            tile.set_alpha(192)
        for tile in self.tiles[46:50]:
            tile.set_alpha(192)
        for tile in self.tiles[56:60]:
            tile.set_alpha(192)
        for tile in self.tiles[66:70]:
            tile.set_alpha(192)
        for tile in self.tiles[76:80]:
            tile.set_alpha(128)
        for step, tile in enumerate(self.tiles[16:20]):
            tile.set_alpha(255-step*32)

    def render_image(self, image_file):
        self.first_draw = True
        self.fog = None
        self.background = resource.load_image(image_file)
        self.sprites = SortedUpdates()
        self.hud = SortedUpdates()
        self.shadows = pygame.sprite.RenderUpdates()
        self.lights = pygame.sprite.LayeredDirty()

    def render_menu(self, menu):
        for sprite in menu.sprites:
            self.hud.add(sprite)

    def render_level(self, level):
        self.first_draw = True
        self.fog = pygame.Surface(self.screen.get_size(), pg.SRCALPHA)
        self.fog.fill((64, 128, 255, 255))
        self._grad(self.fog, self.fog.get_rect(),
                (64, 128, 255), (16, 64, 224))
        self.memory = self.fog.copy()
        self.sprites = SortedUpdates()
        self.hud = SortedUpdates()
        self.shadows = pygame.sprite.RenderUpdates()
        self.dirty = []
        self.mob_sprites = weakref.WeakValueDictionary()
        self.mob_lights = weakref.WeakValueDictionary()
        self.lights = pygame.sprite.LayeredDirty()

        self.background = render_background(level, self.tiles)

    def light_room(self, mob, room):
        (rx, ry), (rw, rh) = room
        mx = rx * 20 + 10
        my = ry * 12 + 17
        mw = (rw+1) * 20
        mh = (rh+1) * 12
        darkroom = self.background.subsurface((mx, my, mw, mh))
        darkroom.set_alpha(32)
        rect = self.memory.blit(darkroom, (mx, my))
        self.fog.blit(self.memory, (mx, my), rect)
        self.dirty.append(rect)

    def _grad(self, surface, rect, startcolor, endcolor):
        (sx, sy, w, h) = rect
        steps = h / 8
        sr, sg, sb = startcolor
        er, eg, eb = endcolor
        dr, dg, db = (er-sr)/steps, (eg-sg)/steps, (eb-sb)/steps
        for step, y in enumerate(xrange(sy, sy+h, 8)):
            surface.fill((max(0, sr), max(0, sg), max(0, sb)), (sx, y, w, 8))
            sr += dr
            sg += dg
            sb += db

    def refresh(self):
        self.screen.blit(self.background, (0, 0))
        self.shadows.draw(self.screen)
        self.sprites.draw(self.screen)
        if self.fog:
            self.lights.draw(self.fog)
            self.screen.blit(self.fog, (0, 0))
        self.hud.draw(self.screen)
        self.real_screen.blit(self.screen, (0, 0))
        pygame.display.update()
        self.dirty = []

    def draw(self):
        if self.first_draw:
            self.refresh()
            self.first_draw = False
        else:
            if self.fog:
                self.hud.clear(self.fog, self.memory)
                self.lights.clear(self.fog, self.memory)
                visible = self.lights.draw(self.fog)
                self.dirty.extend(visible)
                for rect in self.dirty:
                    self.screen.blit(self.background, rect.topleft, rect)
                self.shadows.draw(self.screen)
                self.sprites.draw(self.screen)
                self.dirty.extend(self.hud.draw(self.screen))
                for rect in self.dirty:
                    self.screen.blit(self.fog, rect.topleft, rect)
                self.hud.draw(self.screen)
            else:
                self.hud.clear(self.screen, self.background)
                self.sprites.clear(self.screen, self.background)
                self.shadows.draw(self.screen)
                self.dirty.extend(self.sprites.draw(self.screen))
            self.dirty.extend(self.hud.draw(self.screen))
            for rect in self.dirty:
                self.real_screen.blit(self.screen, rect.topleft, rect)
            pygame.display.update(self.dirty)
            self.dirty = []

    def update(self):
        self.sprites.update()
        self.shadows.update()
        self.lights.update()
        self.hud.update()

    def events(self, events):
        for event in events:
            getattr(self, 'on_%s' % event[0])(*event[1:])

    def on_mob_dust(self, mob, amount=4, delay=0):
        sprite = self.mob_sprites[id(mob)]
        for i in xrange(amount):
            x = sprite.rect.centerx + random.randint(-8, 8)
            y = sprite.rect.centery + random.randint(-3, 3)
            self.sprites.add(sprites.Dust(
                self.tiles, (x, y), min(0, delay + random.randint(0, 4))))

    def on_mob_gibs(self, mob, color=0, amount=8, delay=0):
        sprite = self.mob_sprites[id(mob)]
        for i in xrange(amount):
            x = sprite.rect.centerx + random.randint(-10, 10)
            y = sprite.rect.centery + random.randint(-3, 5)
            self.sprites.add(sprites.Gib(
                    self.tiles,
                    (x, y),
                    min(0, delay + random.randint(0, 6)),
                    color=color,
                ))

    def on_room_light(self, mob, room):
        self.light_room(mob, room)

    def on_light_radius(self, mob, radius):
        light = self.mob_lights[id(mob)]
        light.radius = radius

    def on_mob_walk(self, mob, direction):
        sprite = self.mob_sprites[id(mob)]
        sprite.set_animation(sprite.walk_animation(direction))

    def on_mob_stand(self, mob, direction):
        sprite = self.mob_sprites[id(mob)]
        sprite.set_animation(sprite.stand_animation(direction))

    def on_mob_wait(self, mob, direction):
        sprite = self.mob_sprites[id(mob)]
        sprite.set_animation(sprite.wait_animation(direction))

    def on_mob_attack(self, mob, direction, other):
        sprite = self.mob_sprites[id(mob)]
        sprite.set_animation(sprite.attack_animation(direction))

    def on_mob_death(self, mob):
        try:
            sprite = self.mob_sprites[id(mob)]
        except KeyError:
            return
        sprite.set_animation(sprite.death_animation())

    def on_mob_open(self, mob):
        sprite = self.mob_sprites[id(mob)]
        sprite.set_animation(sprite.open_animation())

    def on_mob_spawn(self, mob, spawner):
        sprite = mob.Sprite(self.tiles, mob.pos, mob.animation)
        self.sprites.add(sprite)
        self.mob_sprites[id(mob)] = sprite
        shadow = sprites.Shadow(self.tiles, sprite)
        self.shadows.add(shadow)
        if mob.has_light:
            light = sprites.Vision(sprite, 64)
            self.lights.add(light)
            self.mob_lights[id(mob)] = light
        if spawner is not None:
            sprite = self.mob_sprites[id(spawner)]
            sprite.set_animation(sprite.spawner_animation())

    def on_mob_message(self, mob, text):
        try:
            sprite = self.mob_sprites[id(mob)]
        except KeyError:
            return
        msg = message.Message(text, sprite.rect.center)
        msg.depth = sprite.depth
        self.sprites.add(msg)

    def on_mob_finish(self, mob):
        sprite = self.mob_sprites[id(mob)]
        sprite.set_animation(sprite.finish_animation())

def render_background(level, tiles):
    background = pygame.Surface((level.width * 20 + 20, level.height * 12 + 20))
    background.fill((8, 32, 112))
    for y, row in enumerate(level.map):
        for x, square in enumerate(row):
            pos = x * 20 + 4, y * 12
            if square == 1:
                background.blit(tiles[6], pos)
            elif square == 2:
                background.blit(tiles[7], pos)

    return background

