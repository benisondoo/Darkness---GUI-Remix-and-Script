#!/usr/bin/env python
# -*- coding: utf-8 -*-


from jelly.util import DX, DY
from jelly import mobs


class Error(Exception):
    pass

class Blocked(Error):
    pass

class BlockedWall(Blocked):
    pass

class BlockedMob(Blocked):
    def __init__(self, mob):
        self.mob = mob


class BaseLevel(object):
    def __init__(self, pc):
        self.pc = pc
        self.mobs = []
        self.width = 31
        self.height = 38

        self.lit_rooms = []
        self.map = [[0] * self.width for y in xrange(self.height)]

        self.Blocked = Blocked
        self.BlockedWall = BlockedWall
        self.BlockedMob = BlockedMob

        self.events = []
        self.is_game_over = False
        self.is_level_over = False
        self.hunted = 0

    def __getitem__(self, (x, y)):
        if self.width > x >= 0 and self.height > y >= 0:
            return self.map[y][x]

    def __setitem__(self, (x, y), value):
        if self.width > x >= 0 and self.height > y >= 0:
            self.map[y][x] = value

    def is_blocked(self, pos):
        for m in self.mobs:
            if m.pos == pos:
                return True
        return not self[pos]


    def walk(self, mob, direction):
        if direction is None:
            return
        x, y = mob.pos
        target = x + DX[direction], y + DY[direction]
        for m in self.mobs:
            if m.pos == target:
                raise self.BlockedMob(m)
        if not self[target]:
            raise self.BlockedWall()
        mob.pos = target
        self.events.append(('mob_walk', mob, direction))
        self.events.append(('mob_dust', mob, 1, -4))

    def spawn(self, mob, spawner=None):
        self.mobs.append(mob)
        self.events.append(('mob_spawn', mob, spawner))
        if mob.hunted:
            self.hunted += 1

    def kill(self, mob):
        self.mobs.remove(mob)
        self.events.append(('mob_death', mob))
        if mob.hunted:
            self.hunted -= 1
            if self.hunted <= 0:
                ladder = mobs.Ladder2(self.pc.pos)
                self.is_level_over = True
                self.spawn(ladder)
                self.events.append(('mob_finish', self.pc))
            else:
                self.message(mob, '%d left' % self.hunted)

    def hit(self, mob, attacker):
        if mob.hit(self, attacker):
            self.events.append(('mob_gibs', mob, mob.color, 8, 2))

    def open(self, mob, item):
        self.mobs.remove(mob)
        self.events.append(('mob_open', mob))
        self.events.append(('mob_dust', mob, 10, 4))
        self.message(mob, item)
        if item != 'Empty':
            self.pc.pick(item)


    def stand(self, mob, direction, dust=False):
        if direction is None:
            return
        self.events.append(('mob_stand', mob, direction))
        if dust:
            self.events.append(('mob_dust', mob, 4))

    def wait(self, mob, direction):
        self.events.append(('mob_wait', mob, direction))

    def attack(self, mob, direction, other):
        self.events.append(('mob_attack', mob, direction, other))
        self.events.append(('mob_dust', mob, 4, -2))
        if other is not None:
            self.hit(other, mob)

    def game_over(self):
        self.events.append(('mob_death', self.pc))
        self.is_game_over = True

    def message(self, mob, text):
        self.events.append(('mob_message', mob, text))
