class CommandDispatcher:
    def __init__(self, game):
        self.game = game
        self.commands = {
            'go': self.game.go,
            'look': self.game.look,
            'inventory': self.game.inventory,
            'take': self.game.take,
            'drop': self.game.drop,
            'quit': self.game.quit,
            'help': self.game.help,
            'read': self.game.read,
            'combine': self.game.combine,
            'put': self.game.put,
            'open': self.game.open,
            'close': self.game.close,
            'talk': self.game.talk,
            'objective': self.game.objective,
        }

    def dispatch(self, command):
        # command = self.parser.parse_command(command)
        if command['action'] in self.commands:
            self.commands[command['action']](command)
        else:
            print('I do not understand that command.') 