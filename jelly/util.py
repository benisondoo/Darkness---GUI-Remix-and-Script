#!/usr/bin/env python
# -*- coding: utf-8 -*-

DX = [0, -1, -1, -1,  0,  1, 1, 1]
DY = [1,  1,  0, -1, -1, -1, 0, 1]


def dist((x1, y1), (x2, y2)):
    return max(abs(x2 - x1), abs(y2 - y1))

def sum_dist((x1, y1), (x2, y2)):
    return abs(x2 - x1) + abs(y2 - y1)

def dist2(pos1, pos2):
    return dist(pos1, pos2) + sum_dist(pos1, pos2)

def pos2dir(pos1, pos2):
    x, y = pos1
    return min(
            [0, 2, 4, 6, 1, 3, 5, 7],
            key=lambda d: dist(pos2, (x + DX[d], y + DY[d])))


class QuitLevel(Exception):
    pass


class QuitGame(Exception):
    pass


class CancelMenu(Exception):
    pass
