#!/usr/bin/env python3

import curses
from time import sleep
import sys
import logging


PLAY_WIDTH = 35
PLAY_HEIGHT = 30
PLAYER_JUMP_VELOCITY_Y = -1

logging.basicConfig(filename='flappyterm.log', level=10)
log = logging.getLogger(__name__)


class GameState(object):

    def __init__(self, game):
        self.game = game

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class GameStateManager(object):

    def __init__(self):
        self.states = {}
        self.current_state = None

    def add_state(self, name, state):
        self.states[name] = state

    def change_state(self, name):
        if self.current_state is not None:
            self.current_state.on_exit()
        self.current_state = self.states[name]
        self.current_state.on_enter()


class TitleState(GameState):

    def on_enter(self):
        window = self.game.root_window
        window.erase()
        window.border()
        window.addstr(10, 3, 'Welcome to Flappy Term!')
        window.addstr(11, 2, 'Press any key to continue!')
        window.refresh()

    def update(self):
        if self.game.window.getch() != curses.ERR:
            self.game.states.change_state('play')


class Player(object):

    def __init__(self, window, on_dead): 
        self.win_height, self.win_width = window.getmaxyx()
        self.y = self.win_height / 2
        self.x = self.win_width / 4
        self.velocityX = 0
        self.velocityY = PLAYER_JUMP_VELOCITY_Y
        self.accelY = 0.05
        self.on_dead = on_dead

    def jump(self):
        self.velocityY = PLAYER_JUMP_VELOCITY_Y

    def update(self):
        self.y += self.velocityY
        self.velocityY += self.accelY
        if self.y > self.win_height - 1 or self.y < 0:
            self.on_dead()

    def draw(self, window):
        window.addstr(int(self.y), int(self.x), 'P')


class PlayState(GameState):

    def __init__(self, game):
        super(PlayState, self).__init__(game)
        window = self.game.window
        height, width = window.getmaxyx()
        self.play_win = window.derwin(
                PLAY_HEIGHT,
                PLAY_WIDTH,
                1,
                1)

    def on_enter(self):
        self.game.root_window.clear()
        self.game.root_window.refresh()
        window = self.game.window
        window.clear()
        window.border()
        window.refresh()
        self.player = Player(self.play_win, self.on_dead)

    def on_dead(self):
        self.game.states.change_state('end')

    def update(self):
        try:
            key = self.game.window.getkey()
        except:
            # There was no input available
            key = ''
        if key == 'q':
            self.game.exit()
        elif key == ' ':
            self.player.jump()
        self.player.update()

    def draw(self):
        self.play_win.clear()
        self.player.draw(self.play_win)
        self.play_win.refresh()
        self.game.window.refresh()


class GameOverState(GameState):

    def on_enter(self):
        window = self.game.root_window
        window.clear()
        window.border()
        window.addstr(10, 10, 'Game over...')
        window.addstr(11, 10, 
                'Press "q" to quit or any other key to '
                'continue...')
        window.refresh()
    
    def update(self):
        try:
            key = self.game.window.getkey()
            if key == 'q':
                self.game.exit()
            else:
                self.game.states.change_state('play')
        except:
            pass


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
        self.states = GameStateManager()
        self.exiting = False

        states = self.states
        states.add_state('title', TitleState(self))
        states.add_state('play', PlayState(self))
        states.add_state('end', GameOverState(self))
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
