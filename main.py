from game_factory import GameFactory
from guess_the_phrase.guess_the_phrase import GuessThePhraseGame
import os
if __name__ == "__main__":
    factory = GameFactory()
    while True:
        game = factory.get_game()
        if game:
            game.play()
        else:
            break