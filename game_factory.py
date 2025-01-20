import os
from guess_the_phrase.guess_the_phrase import GuessThePhraseGame
from text_adventure.text_adventure_game import TextAdventureGame
from word_scramble.word_scramble_game import WordScrambleGame

#store the various games, an index and the game name and the game class, display the game name and the index
#then ask the user to select a game by index, then create an instance of the game class and call the play method
#also, store the game parameters in the game itme tuple, and pass them to the game class constructor
class GameFactory:
    def __init__(self):
        self.games = []
        self.games.append(("Word Scramble", WordScrambleGame))
        self.games.append(("Guess the Phrase", GuessThePhraseGame, f"guess_the_phrase{os.sep}phrase_inventory.csv"))
        self.games.append(("Text Adventure", TextAdventureGame, f"text_adventure{os.sep}game_layouts.json")) 
    def select_game(self):
        for i, game in enumerate(self.games):
            print(f"{i+1}. {game[0]}")
        choice = int(input("Choose a game, -1 to quit: "))
        if choice == -1:
            return None
        chosen = self.games[choice-1]
        if len(chosen) == 2:
            game = chosen[1]()
        else:
            game = chosen[1](chosen[2])
        return game
    def get_game(self):
        game = self.select_game()
        if game:
            return game
        else:
            return None