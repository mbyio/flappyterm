from states import GameState
from config import *

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
