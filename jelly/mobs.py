#!/usr/bin/env python
# -*- coding: utf-8 -*-


import random
import collections
import pygame
from pygame import locals as pg

from jelly import sprites
from jelly import message
from jelly import items
from jelly import behavior
from jelly.util import DX, DY, dist, pos2dir, CancelMenu


KEY_DIRS = {
    pg.K_UP: 4,
    pg.K_LEFT: 2,
    pg.K_DOWN: 0,
    pg.K_RIGHT: 6,
    pg.K_SPACE: 8,
}


class Mob(object):
    Sprite = sprites.MobSprite
    has_light = False
    max_hp = 2
    hunted = False
    behaviors = [behavior.attack_behavior, behavior.wander_behavior]
    spawns = []

    def __init__(self, (x, y)):
        self.pos = x, y
        self.hp = self.max_hp
        self.status = {}

    def control(self, level):
        for behavior in self.behaviors:
            if behavior(self, level):
                return

    def hit(self, level, attacker):
        self.hp -= attacker.damage
        self.status['asleep'] = False
        if self.hp <= 0:
            level.kill(self)
        return True


class PinkJelly(Mob):
    name = 'pink jelly'
    color = 2
    max_hp = 3
    animation = [56, 56, 57, 57, 57, 57]
    behaviors = [behavior.attack_behavior, behavior.coward_behavior]


class PurpleJelly(Mob):
    name = 'purple jelly'
    color = 1
    max_hp = 2
    animation = [46, 46, 46, 47, 47, 47, 47]
    behaviors = [behavior.sleep_behavior, behavior.attack_behavior, behavior.wander_behavior]


class RedJelly(Mob):
    name = 'red jelly'
    color = 3
    max_hp = 1
    animation = [66, 66, 67, 67, 67]
    behaviors = [behavior.attack_behavior, behavior.aggressive_behavior]


class BlueJelly(Mob):
    name = 'blue jelly'
    color = 0
    max_hp = 5
    animation = [36, 36, 36, 37, 37, 37, 37, 37]
    behaviors = [behavior.slow_behavior, behavior.attack_behavior, behavior.wander_behavior]


class BlackJelly(Mob):
    name = 'black jelly'
    color = 4
    max_hp = 3
    animation = [76, 76, 76, 77, 77, 77]
    behaviors = [behavior.one_in(15)(behavior.spawn_behavior), behavior.wander_behavior]
    hunted = True


class Crate(Mob):
    name = 'crate'
    animation = [16]

    def __init__(self, *args, **kwargs):
        super(Crate, self).__init__(*args, **kwargs)
        self.item = random.choice(items.ITEMS)

    def control(self, level):
        pass

    def hit(self, level, attacker):
        level.open(self, self.item)

class Ladder(Mob):
    name = 'ladder'
    animation = [95, 96] * 7
    Sprite = sprites.LadderSprite

    def control(self, level):
        level.kill(self)

    def hit(self, level, attacker):
        pass

class Ladder2(Ladder):
    Sprite = sprites.Ladder2Sprite

class Player(object):
    name = 'player'
    has_light = True
    Sprite = sprites.PlayerSprite
    animation = None
    hunted = False
    color = 5

    def __init__(self):
        self.level = 0
        self.max_hp = 26
        self.hp = self.max_hp
        self.items = collections.Counter()
        self.damage = 1
        self.weapon = None


    def place(self, (x, y)):
        self.pos = x, y
        self.direction = 0

    def hit(self, level, attacker):
        self.direction = pos2dir(self.pos, attacker.pos)
        self.hp -= 1
        if self.hp <= 0:
            level.game_over()
        return True

    def pick(self, item):
        self.items[item] += 1

    def inventory_menu(self, display):
        item_list = [k for (k, v) in self.items.iteritems() if v]
        labels = []
        equipped = []
        for item, count in self.items.iteritems():
            if self.weapon == item:
                equipped.append(len(labels))
                labels.append('%s (equipped)' % item)
            elif count:
                labels.append('%s x%d' % (item, count))
        menu = message.Menu((480, 20), labels or ['Empty'], equipped)
        display.render_menu(menu)
        choice = None
        clock = pygame.time.Clock()
        try:
            while choice is None:
                clock.tick(15)
                display.update()
                display.draw()
                choice = menu.update()
        except CancelMenu:
            return None
        if not item_list:
            return None
        return item_list[choice]

    def control(self, level, display):
        direction = None
        keys = pygame.key.get_pressed()
        if keys[pg.K_x]:
            item = self.inventory_menu(display)
            if item:
                if items.use_item(item, self, level):
                    self.items[item] -= 1
                return True
            return False
        elif keys[pg.K_DOWN] and keys[pg.K_LEFT]:
            direction = 1
        elif keys[pg.K_UP] and keys[pg.K_LEFT]:
            direction = 3
        elif keys[pg.K_UP] and keys[pg.K_RIGHT]:
            direction = 5
        elif keys[pg.K_DOWN] and keys[pg.K_RIGHT]:
            direction = 7
        if keys[pg.K_z]:
            x, y = self.pos
            for other in level.mobs:
                if other.pos == (x + DX[self.direction],
                                 y + DY[self.direction]):
                    break
            else:
                other = None
            if other is None and not keys[pg.K_LCTRL]:
                for m in level.mobs:
                    if m == self:
                        continue
                    if dist(self.pos, m.pos) <= 1:
                        other = m
                        self.direction = pos2dir(self.pos, other.pos)
                        break
            level.attack(self, self.direction, other)
            return True
        if not keys[pg.K_LSHIFT] and not direction:
            for key, direction in KEY_DIRS.iteritems():
                if keys[key]:
                    break
            else:
                direction = None
        if direction == 8:
            level.wait(self, self.direction)
        elif direction is not None:
            self.direction = direction
            if keys[pg.K_LCTRL]:
                level.stand(self, direction)
                return False
            try:
                level.walk(self, direction)
            except level.Blocked:
                level.stand(self, self.direction, dust=True)
                return False
        else:
            level.stand(self, self.direction)
            return False
        return True
