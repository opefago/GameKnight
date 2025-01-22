class CommandDispatcher:
    def __init__(self, game, parser):
        self.game = game
        self.parser = parser
        self.commands = {
            'go': self.game.go,
            'look': self.game.look,
            'inventory': self.game.inventory,
            'take': self.game.take,
            'drop': self.game.drop,
            'quit': self.game.quit,
        }

    def dispatch(self, command):
        command = self.parser.parse_command(command)
        if command['action'] in self.commands:
            self.commands[command['action']](command)
        else:
            print('I do not understand that command.') 