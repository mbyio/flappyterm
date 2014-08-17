import glob
from importlib import import_module
import logging


log = logging.getLogger(__name__)


class GameState(object):

    name = ''

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

    def autoload(self, game):
        # Locate and add states
        for f in glob.glob('game_states/*.py'):
            # format the name like a module import statement
            f = f[:-3]
            f = f.replace('/', '.')
            log.info('Importing %s' % f)
            mod = import_module(f)
            for name in dir(mod):
                prop = getattr(mod, name)
                try:
                    if issubclass(prop, GameState):
                        inst = prop(game)
                        self.add_state(inst)
                except TypeError:
                    pass

    def add_state(self, state):
        log.info('Adding state %s' % state.name)
        self.states[state.name] = state

    def change_state(self, name):
        if self.current_state is not None:
            self.current_state.on_exit()
        self.current_state = self.states[name]
        self.current_state.on_enter()

