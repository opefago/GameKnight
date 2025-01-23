import random
import csv
from game import Game


class GuessThePhraseGame(Game):
    def __init__(self, inventory_file='phrase_inventory.csv'):
        self.__load_inventory(inventory_file)
        self.__used_phrases = set()
        self.__difficulty_thresholds = {
            "easy": 0.5,
            "medium": 0.7,
            "hard": 0.85
        }
        self.__cost_per_guess = 50
        self.__cost_per_failed_attempt = 150
        self.__MAX_ATTEMPTS = 3
        self.__currency = "₦"
        self.__separator = "         "
    
    def name(self):
        return "Guess The Phrase"
    
    def __load_inventory(self, inventory_file):
        """Load phrases and categories from CSV file."""
        try:
            with open(inventory_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.inventory = [(row['phrase'], row['category']) for row in reader]
                
            if not self.inventory:
                raise ValueError("Inventory file is empty")
                
        except FileNotFoundError:
            print(f"Error: Could not find inventory file '{inventory_file}'")
            print("Creating a new inventory file with sample data...")
            self.__create_sample_inventory(inventory_file)
            
        except Exception as e:
            print(f"Error loading inventory: {str(e)}")
            print("Using default inventory...")
            self.inventory = [
                ("A Piece of Cake", "Common Phrases"),
                ("The Great Gatsby", "Book Titles"),
                ("To Be or Not To Be", "Famous Quotes")
            ]

    def __create_sample_inventory(self, filename):
        """Create a sample inventory CSV file."""
        sample_data = [
            ['phrase', 'category'],
            ['A Piece of Cake', 'Common Phrases'],
            ['The Great Gatsby', 'Book Titles'],
            ['To Be or Not To Be', 'Famous Quotes']
        ]
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(sample_data)
            self.inventory = [(row[0], row[1]) for row in sample_data[1:]]
            print(f"Created sample inventory file: {filename}")
        except Exception as e:
            print(f"Error creating sample inventory file: {str(e)}")
            self.inventory = [(row[0], row[1]) for row in sample_data[1:]]

    def __derive_phrase_data(self, phrase):
        letters_in_phrase = set(filter(str.isalpha, phrase.lower()))
        letter_positions = {
            letter: [pos for pos, char in enumerate(phrase) if char.lower() == letter] 
            for letter in set(phrase.lower())
        }
        return letters_in_phrase, letter_positions

    def __hide_letters(self, phrase, difficulty, letters_in_phrase):
        hide_threshold = int(len(letters_in_phrase) * difficulty)
        hidden_letters = set(random.sample(letters_in_phrase, k=hide_threshold))
        words = phrase.split()
        hidden_words = []
        for word in words:
            hidden_word = " ".join(
                letter if letter.lower() not in hidden_letters else "⬜"
                for letter in word
            )
            hidden_words.append(hidden_word)
        phrase_with_hidden_letters = self.__separator.join(hidden_words)
        return hidden_letters, phrase_with_hidden_letters

    def __format_for_display(self, phrase):
        return f"📝         {phrase}         📝"

    def __pick_phrase(self):
        phrase, category = random.choice(self.inventory)
        while f"{category}-{phrase}" in self.__used_phrases:
            phrase, category = random.choice(self.inventory)
        self.__used_phrases.add(f"{category}-{phrase}")
        return phrase, category
    
    def __normalize_string(self, text):
        """Normalize string by preserving only alphanumeric characters and converting to lowercase"""
        return ''.join(char.lower() for char in text if char.isalnum())

    def __game_round(self, phrase, category, difficulty):
        cash_prize = 1000
        guesses = set()
        letters_in_phrase, letter_positions = self.__derive_phrase_data(phrase)
        hidden_letters, phrase_with_hidden_letters = self.__hide_letters(
            phrase, difficulty, letters_in_phrase
        )

        print(f"\n📚 Category: {category}")
        print(f"🎯 Phrase: {self.__format_for_display(phrase_with_hidden_letters.upper())}")

        attempts = self.__MAX_ATTEMPTS

        while attempts > 0:
            print(f"\n💰 Cash prize: {self.__currency}{cash_prize}")
            guess = input("\nGuess a letter or the whole phrase: ").strip()

            if len(guess) == 1:
                 # deduct cost per guess for buying a vowel
                if guess.lower() in 'aeiou' and guess.lower() not in guesses:
                    cash_prize -= self.__cost_per_guess
                if guess.lower() in guesses:
                    print("❗ You already guessed that letter!")
                elif guess.lower() in hidden_letters:
                    count = len(letter_positions[guess.lower()])
                    print(f"✅ Correct! The letter '{guess}' appears {count} times in the phrase.")
                    guesses.add(guess.lower())
                    hidden_letters.remove(guess.lower())
                    
                    words = phrase.split()
                    revealed_words = []
                    for word in words:
                        revealed_word = " ".join(
                            letter if letter.lower() not in hidden_letters else "⬜"
                            for letter in word
                        )
                        revealed_words.append(revealed_word)
                    phrase_with_hidden_letters = self.__separator.join(revealed_words)
                    print(f"🎯 Phrase: {self.__format_for_display(phrase_with_hidden_letters.upper())}")
                elif guess.lower() in phrase_with_hidden_letters.lower():
                    print(f"❗ The letter '{guess}' is already revealed.")
                else:
                    print(f"❌ Wrong! The letter '{guess}' is not in the phrase.")
                    attempts -= 1
                    cash_prize -= self.__cost_per_failed_attempt
            else:
                if  self.__normalize_string(guess.strip()) == self.__normalize_string(phrase.strip()):
                    print(f"🎉 Congratulations! You guessed the phrase correctly. You just won {self.__currency}{cash_prize}.")
                    return True
                else:
                    print("❌ Wrong guess!")
                    attempts -= 1
                    cash_prize -= self.__cost_per_failed_attempt

            print(f"🎲 Remaining attempts: {attempts}")

            if phrase_with_hidden_letters.replace(" ", "").replace("⋮", "").lower() == phrase.lower().replace(" ", ""):
                print(f"🎉 Congratulations! You completed the phrase: {phrase}. You just won {self.__currency}{cash_prize}.")
                return True
            if cash_prize <= 0:
                print(f"😢 Game over! You ran out of cash. The phrase was: {phrase}")
                return False

        if attempts == 0:
            print(f"😢 Game over! The phrase was: {phrase}")
            return False

    def play(self):
        """Start and play the Word Guess Game."""
        print("🎮 Welcome to Phrase Guess Game! 🎮")
        while True:
            phrase, category = self.__pick_phrase()
            difficulty_choice = input("Select difficulty (easy, medium, hard): ").strip().lower()
            difficulty = self.__difficulty_thresholds.get(difficulty_choice, 0.5)
            self.__game_round(phrase, category, difficulty)
            play_again = input("\n🔄 Do you want to play again? (yes/no): ").strip().lower()
            if play_again != "yes":
                break
