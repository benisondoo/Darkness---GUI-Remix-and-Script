#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame import locals as pg

from jelly import resource
from jelly import util


class Text(pygame.sprite.Sprite):
    font = None

    def __init__(self, text, color=(250, 250, 250)):
        super(Text, self).__init__()
        if self.font is None:
            self.font = resource.load_font('pf_ronda_seven_bold.ttf')
        self.image = self.outlined_text(text, color, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.depth = 1001

    def outlined_text(self, text, color, border_color):
        font = self.font
        notcolor = [c^0xFF for c in border_color]
        base = font.render(text, 0, border_color, notcolor)
        size = base.get_width() + 2, base.get_height() + 2
        image = pygame.Surface(size, 16)
        image.fill(notcolor)
        base.set_colorkey(0)
        image.blit(base, (0, 0))
        image.blit(base, (2, 0))
        image.blit(base, (0, 2))
        image.blit(base, (2, 2))
        base.set_colorkey(0)
        base.set_palette_at(1, color)
        image.blit(base, (1, 1))
        image.set_colorkey(notcolor)
        return image


class Message(Text):
    def __init__(self, text, pos):
        super(Message, self).__init__(text)
        self.rect.center = pos
        self.step = 0
        self.alpha = 255

    def update(self):
        self.rect.move_ip(0, -2)
        self.alpha -= 16
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)


class Window(pygame.sprite.Sprite):
    tiles = None

    def __init__(self, pos, (width, height)):
        super(Window, self).__init__()
        if self.tiles is None:
            self.tiles = resource.load_tiles('jelly.png', 32, 32)
        tile = self.tiles[80]
        self.image = pygame.surface.Surface((width, height))
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((0x16, 0x52, 0xcd), (4, 4, width - 8, height - 8))
        for y in xrange(8, height - 8, 4):
            self.image.blit(tile, (0, y), (0, 8, 8, 4))
            self.image.blit(tile, (width - 8, y), (24, 8, 8, 4))
        for x in xrange(8, width - 8, 4):
            self.image.blit(tile, (x, 0), (8, 0, 4, 8))
            self.image.blit(tile, (x, height - 8), (8, 24, 4, 8))
        self.image.blit(tile, (0, 0), (0, 0, 8, 8))
        self.image.blit(tile, (width - 8, height - 8), (24, 24, 8, 8))
        self.image.blit(tile, (width - 8, 0), (24, 0, 8, 8))
        self.image.blit(tile, (0, height - 8), (0, 24, 8, 8))
        self.image.set_alpha(92)

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.depth = 1000


class Cursor(pygame.sprite.Sprite):
    tiles = None

    def __init__(self, pos):
        super(Cursor, self).__init__()
        if self.tiles is None:
            self.tiles = resource.load_tiles('jelly.png', 32, 32)
        self.image = self.tiles[81]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = pos
        self.item = 0
        self.depth = 1002
        self.x = 0
        self.dx = 1

    def update(self):
        self.x += self.dx
        if self.x > 4:
            self.dx -= 2
        elif self.x < -4:
            self.dx += 1
        self.rect.center = (self.pos[0]+self.x, self.pos[1] + 14 * self.item)


class Menu(object):
    def __init__(self, pos, items, highlights=[]):
        self.pos = pos
        self.sprites = []
        self.items = items
        width = 0
        for i, item in enumerate(items):
            if i in highlights:
                color = (255, 255, 0)
            else:
                color = (250, 250, 250)
            text = Text(item, color)
            self.sprites.append(text)
            text.rect.topleft = (pos[0] + 12, pos[1] + 14 * i + 6)
            if width < text.rect.width:
                width = text.rect.width
        self.cursor = Cursor((pos[0] + 10, pos[1] + 14))
        self.sprites.append(self.cursor)
        self.window = Window(pos, (21 + width, 16 + 14 * len(items)))
        self.sprites.append(self.window)

    def move(self, di):
        self.cursor.item = max(0, min(len(self.items)-1, self.cursor.item + di))

    def cleanup(self, wait=True):
        for sprite in self.sprites:
            sprite.kill()
        while wait:
            if pygame.event.wait().type == pg.KEYUP:
                return

    def update(self):
        item = None
        for event in pygame.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.move(-1)
                elif event.key == pg.K_DOWN:
                    self.move(1)
                elif event.key == pg.K_z:
                    item = self.cursor.item
                    self.cleanup()
                elif event.key == pg.K_x:
                    self.cleanup()
                    raise util.CancelMenu()
                elif event.key == pg.K_ESCAPE:
                    self.cleanup()
                    raise util.QuitLevel()
            elif event.type == pg.QUIT:
                self.cleanup(False)
                raise util.QuitGame()
        return item

class Health(pygame.sprite.Sprite):
    tiles = None

    def __init__(self, owner):
        super(Health, self).__init__()
        if self.tiles is None:
            self.tiles = resource.load_tiles('jelly.png', 32, 32)
        self.owner = owner
        self.image = self.tiles[90].copy()
        self.rect = self.image.get_rect()
        self.rect.center = 32, 32

    def update(self):
        gauge = int(max(0, min(26, 26 * self.owner.hp / self.owner.max_hp)))
        self.image = self.tiles[90].copy()
        self.image.blit(self.tiles[91], (3, 0), (3, 0, gauge, 32))
