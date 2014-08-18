import random

from states import GameState
from config import *


class PipeManager():

    MAX_HEIGHT = PLAY_HEIGHT - PIPE_MARGIN * 2 - PIPE_GAP_SIZE

    def __init__(self):
        self.pipe_counter = INITIAL_PIPE_SPACE
        self.pipes = []

    def update(self):
        for pipe in self.pipes:
            pipe['x'] -= 1
        try:
            first = self.pipes[0]
            if first['x'] + PIPE_WIDTH < 0:
                self.pipes.pop(0)
        except IndexError:
            pass

        self.pipe_counter -= 1
        if self.pipe_counter == 0:
            self.pipe_counter = SPACE_BETWEEN_PIPES + PIPE_WIDTH
            self.add_pipe()

    def add_pipe(self):
        self.pipes.append({
            'height': random.randint(0, self.MAX_HEIGHT - 1),
            'x': PLAY_WIDTH
            })

    def draw(self, window):
        for pipe in self.pipes:
            x = pipe['x']
            for x in range(x, x + PIPE_WIDTH):
                if x >= PLAY_WIDTH or x < 0:
                    continue
                self.draw_pipe_col(x, pipe['height'], window)

    def draw_pipe_col(self, x, pipe_height, window):
        for y in range(0, PIPE_MARGIN + pipe_height):
            window.addstr(y, x, PIPE_SYMBOL)
        y += PIPE_GAP_SIZE
        for y in range(y, PLAY_HEIGHT - 1):
            window.addstr(y, x, PIPE_SYMBOL)


class Player():

    def __init__(self, window, on_dead): 
        self.win_height, self.win_width = window.getmaxyx()
        self.y = self.win_height / 2
        self.x = self.win_width / 4
        self.velocityX = 0
        self.velocityY = PLAYER_JUMP_VELOCITY_Y
        self.accelY = 0.05
        self.on_dead = on_dead

    def jump(self):
        if self.y >= 0:
            self.velocityY = PLAYER_JUMP_VELOCITY_Y

    def update(self):
        self.y += self.velocityY
        self.velocityY += self.accelY
        if self.y > self.win_height - 1:
            self.on_dead()

    def draw(self, window):
        if self.y < 0:
            return
        window.addstr(int(self.y), int(self.x), 'P')


class PlayState(GameState):

    name = 'play'

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
        self.pipes = PipeManager()

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

        self.pipes.update()

    def draw(self):
        self.play_win.clear()
        self.player.draw(self.play_win)
        self.pipes.draw(self.play_win)
        self.play_win.refresh()
        self.game.window.refresh()
