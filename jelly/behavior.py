#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from jelly.util import DX, DY, dist, pos2dir, dist2


def one_in(prob):
    def decorator(func):
        def wrapped(*args, **kwargs):
            if random.randint(0, prob) != 0:
                return False
            return func(*args, **kwargs)
        return wrapped
    return decorator


def sleep_behavior(mob, level):
    if mob.status.get('asleep', True):
        return True
    return False


def attack_behavior(mob, level):
    if dist(level.pc.pos, mob.pos) <= 1:
        level.attack(mob, pos2dir(mob.pos, level.pc.pos), level.pc)
        mob.status['asleep'] = False
        return True
    return False


def fitness_behavior(mob, level, fitness):
    x, y = mob.pos
    possible = [d for d in [0, 2, 4, 6, 1, 3, 5, 7]
                if not level.is_blocked((x + DX[d], y + DY[d]))]
    if not possible:
        return False
    direction = fitness(possible)
    try:
        level.walk(mob, direction)
    except level.Blocked:
        return False
    return True


def wander_behavior(mob, level):
    return fitness_behavior(mob, level, random.choice)


def passive_behavior(mob, level):
    return True


def slow_behavior(mob, level):
    mob.status['wait'] = not mob.status.get('wait', False)
    if mob.status['wait']:
        return True
    return False


def spawn_behavior(mob, level):
    x, y = mob.pos
    possible = [d for d in [0, 2, 4, 6, 1, 3, 5, 7]
                if not level.is_blocked((x + DX[d], y + DY[d]))]
    if not possible:
        return False
    direction = random.choice(possible)
    MobClass = random.choice(mob.spawns)
    pos = (x + DX[direction], y + DY[direction])
    spawnee = MobClass(pos)
    level.spawn(spawnee, mob)
    return True


def coward_behavior(mob, level):
    x, y = mob.pos
    def coward_fitness(choices):
        return max(
            choices,
            key=lambda d: dist2((x + DX[d], y + DY[d]), level.pc.pos))
    return fitness_behavior(mob, level, coward_fitness)


def aggressive_behavior(mob, level):
    x, y = mob.pos
    return fitness_behavior(mob, level, lambda choices: min(choices,
        key=lambda d: dist((x+DX[d], y+DY[d]), level.pc.pos)))
