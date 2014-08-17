import curses

from states import GameState

class TitleState(GameState):

    name = 'title'

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

