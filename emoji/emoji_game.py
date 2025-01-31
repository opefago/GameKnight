import random
import time

from game import Game

class EmojiGame(Game):
    def __init__(self):
        self.categories = {
            "Movies": {
                "🦁👑": "The Lion King",
                "👻🏃‍♂️": "Ghost",
                "🌊👨‍👦🐠": "Finding Nemo",
                "🧙‍♂️💍": "Lord of the Rings",
                "🚢❄️💔": "Titanic"
            },
            "Books": {
                "🐷🕷": "Charlotte's Web",
                "🧙‍♂️⚡👓": "Harry Potter",
                "🌳🏃‍♂️": "The Giving Tree",
                "🦈🚣‍♂️": "Old Man and the Sea",
                "🐛🍎": "The Very Hungry Caterpillar"
            },
            "Songs": {
                "⭐🌙": "Starlight",
                "💃🌙": "Dancing in the Moonlight",
                "👶🎵": "Baby Shark",
                "🎄🎵": "Jingle Bells",
                "💜🌧": "Purple Rain"
            }
        }
        self.score = 0
        self.total_questions = 0
    
    def name(self):
        return "Emoji Guessing Game"

    def play(self):
        print("Welcome to the Emoji Guessing Game!")
        print("\nCategories:", ", ".join(self.categories.keys()))
        
        while True:
            category = random.choice(list(self.categories.keys()))
            emoji_set = random.choice(list(self.categories[category].keys()))
            answer = self.categories[category][emoji_set]
            
            print(f"\nCategory: {category}")
            print(f"Emoji: {emoji_set}")
            
            guess = input("Your guess (or 'quit' to exit): ").strip().lower()
            
            if guess == 'quit':
                break
            
            self.total_questions += 1
            if guess == answer.lower():
                print("Correct! 🎉")
                self.score += 1
            else:
                print(f"Wrong! The answer was: {answer}")
            
            print(f"Score: {self.score}/{self.total_questions}")
            time.sleep(1)
        
        if self.total_questions > 0:
            percentage = (self.score / self.total_questions) * 100
            print(f"\nFinal Score: {self.score}/{self.total_questions} ({percentage:.1f}%)")