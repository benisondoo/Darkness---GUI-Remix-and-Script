#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame import locals as pg

from jelly import display
from jelly import mobs
from jelly import rooms_level
from jelly import message
from jelly import util


LEVELS = [
    (1, 4, 8, [mobs.PurpleJelly]),
    (1, 5, 8, [mobs.PurpleJelly, mobs.PinkJelly]),
    (2, 6, 12, [mobs.PurpleJelly, mobs.PinkJelly]),
    (2, 7, 8, [mobs.PurpleJelly, mobs.RedJelly]),
    (3, 8, 12, [mobs.PurpleJelly, mobs.RedJelly]),
    (3, 8, 12, [mobs.PurpleJelly, mobs.PinkJelly, mobs.RedJelly]),
    (2, 6, 8, [mobs.RedJelly]),
    (4, 8, 12, [mobs.PurpleJelly, mobs.RedJelly, mobs.BlueJelly]),
    (2, 12, 16, [mobs.BlueJelly]),
    (5, 8, 20, [mobs.PurpleJelly, mobs.RedJelly, mobs.BlueJelly, mobs.PinkJelly]),
]


class Game(object):
    def __init__(self):
        self.display = display.Display()
        self.clock = pygame.time.Clock()

    def run(self):
        try:
            while True:
                try:
                    self.start()
                    while True:
                        if not self.main():
                            self.game_over()
                        else:
                            self.victory()
                except util.QuitLevel:
                    pass
        except util.QuitGame:
            pygame.quit()
            return

    def game_menu(self):
        menu = message.Menu((80, 380), ['WAKE UP IN THE DARKNESS', 'CONTINUE TO SLEEP'], [0])
        self.display.render_menu(menu)
        choice = None
        try:
            while choice is None:
                self.display.update()
                self.display.draw()
                self.clock.tick(15)
                choice = menu.update()
        except (util.QuitLevel, util.CancelMenu):
            raise util.QuitGame()
        if choice == 1:
            raise util.QuitGame()

    def start(self):
        self.display.render_image('title.png')
        self.game_menu()

    def game_over(self):
        self.display.render_image('dead.png')
        self.game_menu()

    def victory(self):
        self.display.render_image('finish.png')
        self.game_menu()

    def next_level(self):
        params = LEVELS[self.pc.level]
        self.pc.level += 1
        if self.pc.level >= len(LEVELS):
            return True
        self.level = rooms_level.Level(self.pc)
        self.level.populate(*params)
        self.display.render_level(self.level)
        self.display.hud.add(message.Health(self.pc))

    def quit_menu(self):
        menu = message.Menu(
            (290, 200),
            ['CONTINUE', 'TITLE', 'QUIT'],
            [0],
        )
        self.display.render_menu(menu)
        choice = None
        try:
            while choice is None:
                self.clock.tick(15)
                self.display.update()
                self.display.draw()
                choice = menu.update()
        except (util.QuitLevel, util.CancelMenu):
            return
        if choice == 1:
            raise util.QuitLevel()
        if choice == 2:
            raise util.QuitGame()

    def main(self):
        self.pc = mobs.Player()
        self.next_level()
        while not self.level.is_game_over:
            self.clock.tick(15)
            self.display.update()
            self.display.draw()
            for event in pygame.event.get():
                if event.type == pg.ACTIVEEVENT and event.gain:
                    self.display.refresh()
                if event.type == pg.QUIT:
                    raise util.QuitGame()
                elif event.type == pg.KEYDOWN and event.key == pg.K_n:
                    self.level.hunted = 0
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.quit_menu()
                    self.display.refresh()
            try:
                pc_animation = self.display.mob_sprites[id(self.pc)].animations
            except KeyError:
                pc_animation = None
                self.display.events(self.level.events)
                self.level.events = []
            if not pc_animation:
                if self.level.is_level_over and self.next_level():
                    return True
                if self.pc.control(self.level, self.display):
                    for mob in list(self.level.mobs):
                        if mob == self.pc:
                            continue
                        mob.control(self.level)
                self.display.events(self.level.events)
                self.level.events = []

