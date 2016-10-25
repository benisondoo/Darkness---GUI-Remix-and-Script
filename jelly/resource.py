#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pkgutil
import os
import tempfile
import shutil
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import pygame


TILE_CACHE = {}
FONT_CACHE = {}


def load_tiles(filename, width, height):
    try:
        return TILE_CACHE[filename, width, height]
    except KeyError:
        image = load_image(filename)
        image.set_colorkey((0, 0, 0))
        image_width, image_height = image.get_size()
        tiles = []
        for x in range(image_width/width):
            for y in range(image_height/height):
                rect = (x * width, y * height, width, height)
                tiles.append(image.subsurface(rect))
        TILE_CACHE[filename, width, height] = tiles
    return tiles


def load_image(filename):
    f = StringIO.StringIO(pkgutil.get_data('jelly', filename))
    return pygame.image.load(f, filename).convert()


def load_font(filename, size=8):
    try:
        return FONT_CACHE[filename, size]
    except KeyError:
        # XXX the "right" way causes segmentation fault
        f = StringIO.StringIO(pkgutil.get_data('jelly', filename))
        tmpdir = tempfile.mkdtemp()
        fname = os.path.join(tmpdir, filename)
        try:
            with open(fname, 'wb') as f:
                data = pkgutil.get_data('jelly', filename)
                f.write(data)
            font = pygame.font.Font(fname, size)
        finally:
            try:
                os.remove(fname)
                os.rmdir(tmpdir)
            except:
                pass
        FONT_CACHE[filename, size] = font
    return font

