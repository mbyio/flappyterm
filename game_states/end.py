from states import GameState

class GameOverState(GameState):

    name = 'end'

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
