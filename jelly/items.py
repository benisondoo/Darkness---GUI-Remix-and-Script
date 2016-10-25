#!/usr/bin/env python
# -*- coding: utf-8 -*-


ITEMS = [
    'Empty',
    'Heavy wrench',
    'Wooden mallet',
    'First aid kit',
    'Bandaid',
    'Fire axe',
]

def use_item(item, mob, level):
    if item == 'Bandaid':
        mob.hp = min(mob.max_hp, mob.hp + 10)
        return True
    elif item == 'First aid kit':
        mob.hp = mob.max_hp
        return True
    elif item == 'Heavy wrench':
        mob.weapon = item
        mob.damage = 2
    elif item == 'Wooden mallet':
        mob.weapon = item
        mob.damage = 3
    elif item == 'Fire axe':
        mob.weapon = item
        mob.damage = 8
    return False
