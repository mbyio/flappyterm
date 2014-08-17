#!/usr/bin/env python3

import curses
from time import sleep
import sys
import logging

from states import GameState, GameStateManager
from config import *


logging.basicConfig(filename='flappyterm.log', level=10)
log = logging.getLogger(__name__)


class Game(object):

    def __init__(self, root):
        self.root_window = root

    def run(self):
        curses.curs_set(0)
        root = self.root_window
        root.nodelay(True)
        root.border('#', '#', '#', '#', '#', '#', '#', '#')
        root.refresh()
        height, width = root.getmaxyx()
        self.window = root.derwin(
                PLAY_HEIGHT + 2,
                PLAY_WIDTH + 2,
                (height - PLAY_HEIGHT - 2) // 2,
                (width - PLAY_WIDTH - 2) // 2)
        self.window.nodelay(True)
        self.exiting = False

        states = GameStateManager()
        self.states = states
        states.autoload(self)
        states.change_state('title')

        log.info('Starting game')

        while not self.exiting:
            states.current_state.update()
            states.current_state.draw()
            sleep(1 / 60)

    def exit(self):
        self.exiting = True


if __name__ == '__main__':
    def main(window):
        g = Game(window)
        g.run()
    curses.wrapper(main)
