#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from jelly import mobs
from jelly import level


class Level(level.BaseLevel):
    def __init__(self, pc):
        super(Level, self).__init__(pc)

        areas = [
            ((0, 0), (9, 11)), ((11, 0), (9, 11)), ((22, 0), (9, 11)),
            ((0, 13), (9, 11)), ((11, 13), (9, 11)), ((22, 13), (9, 11)),
            ((0, 26), (9, 11)), ((11, 26), (9, 11)), ((22, 26), (9, 11)),
        ]

        rooms = []
        r = random.randint
        for (x, y), (w, h) in areas:
            width = r(1, w/2) * 2
            height = r(1, h/2) * 2
            x_offset = r(0, (w - width)/2) * 2
            y_offset = r(0, (h - height)/2) * 2
            rooms.append(((x + x_offset, y + y_offset), (width, height)))

        random.shuffle(rooms)

        for room, next_room in zip(rooms, rooms[1:]):
            (x, y), (w, h) = room
            (nx, ny), (nw, nh) = next_room
            x1 = nx + r(0, nw/2) * 2
            y1 = ny + r(0, nh/2) * 2
            x2 = x + r(0, w/2) * 2
            y2 = y + r(0, h/2) * 2
            self._path((x1, y1), (x2, y2), 2)

        for room in rooms:
            (x, y), (w, h) = room
            self._fill((x, y), (w + 1, h + 1), 1)

        (x, y), (w, h) = random.choice(rooms)
        pc_pos = (r(x, x+w), r(y, y+h))

        self.spawn(mobs.Ladder(pc_pos))
        self.pc.place(pc_pos)
        self.spawn(self.pc)

        self.rooms = rooms

    def populate(self, bosses, items, monsters, kinds):
        r = random.randint
        for i in xrange(bosses):
            (x, y), (w, h) = random.choice(self.rooms)
            pos = (r(x, x + w), r(y, y + h))
            mob = mobs.BlackJelly(pos)
            mob.spawns = kinds
            self.spawn(mob)
        for i in xrange(items):
            (x, y), (w, h) = random.choice(self.rooms)
            pos = (r(x, x + w), r(y, y + h))
            mob = mobs.Crate(pos)
            self.spawn(mob)
        for i in xrange(monsters):
            (x, y), (w, h) = random.choice(self.rooms)
            pos = (r(x, x + w), r(y, y + h))
            mob = random.choice(kinds)(pos)
            self.spawn(mob)


    def _fill(self, (sx, sy), (width, height), fill):
        for y in xrange(sy, sy + height):
            for x in xrange(sx, sx + width):
                self[x, y] = fill

    def _path(self, (sx, sy), (ex, ey), fill):
        for x in xrange(sx, ex, 1 if sx < ex else -1):
            if self[x, sy]:
                return
            self[x, sy] = fill
        for y in xrange(sy, ey, 1 if sy < ey else -1):
            if self[ex, y]:
                return
            self[ex, y] = fill

    def find_room(self, (x, y)):
        for room in self.rooms:
            (rx, ry), (rw, rh) = room
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return room

    def walk(self, mob, direction):
        super(Level, self).walk(mob, direction)
        if mob.has_light:
            room = self.find_room(mob.pos)
            if room:
                self.events.append(('light_radius', mob, 80))
                if room not in self.lit_rooms:
                    self.lit_rooms.append(room)
                    self.events.append(('room_light', mob, room))
            else:
                self.events.append(('light_radius', mob, 48))
