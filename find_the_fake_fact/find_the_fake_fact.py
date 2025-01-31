import json
import random
import time
import threading
from typing import Dict

class FindTheFakeFact:
    def __init__(self, fact_file="facts.json"):
        self.players = []
        self.safety_points = [200, 400, 500]
        self.facts = self.load_facts(fact_file)
        self.used_facts = set()
        # Give a 10 seconds allowan ce for taking a screenshot and posting on the group
        # Time allowance is actrually 45 seconds, this is to discourage googling
        self.timer_limit = 55
        self.leaderboard = {}
        self.start_timer = lambda limit: time.sleep(limit)
        self.points_per_round = 100
        self.lifelines = {}
        # Track active special rounds
        self.special_rounds_duration = 120
        self.special_rounds = {
            "speed_round": {'available': False, 'name': 'Speed Round', 'description': f'Answer as many questions as you can in {self.special_rounds_duration} seconds!'},
            "chain_round": {'available': False, 'name': 'Chain Round', 'description': 'Answer questions with increasing rewards!'},
        }
        # Track player streaks for bonuses
        self.player_streaks = {}
        self.reset_game()
        self.special_round_point = 25

    def load_facts(self, fact_file="facts.json"):
        with open(fact_file, "r") as file:
            return json.load(file)

    def get_random_fact(self):
        available_facts = [f for f in self.facts if tuple(f["facts"]) not in self.used_facts]
        if not available_facts:
            print("⚠️ No more available facts. Resetting used facts...")
            self.used_facts.clear()
            available_facts = self.facts

        chosen_fact = random.choice(available_facts)
        self.used_facts.add(tuple(chosen_fact["facts"]))
        return chosen_fact

    def play(self):
        print("\n🎭 Welcome to 'Find the Fake Fact'! 🎭\n")

        while True:
            player_name = input("Enter player name (or 'quit' to exit): ").strip()
            if player_name.lower() == "quit":
                break

            self.players.append({"name": player_name, "earnings": 0})
            self.play_round(player_name)
            self.reset_game()

        self.show_leaderboard()

    def play_round(self, player_name):
        player = next(p for p in self.players if p["name"] == player_name)
        print(f"\n🔹 {player_name}, your game begins now! 🔹\n")
        
        # Initialize streak for new player
        self.player_streaks[player_name] = 0
        rounds_played = 0
        
        # print lifelines
        print("❤️ Lifelines:")
        for lifeline, available in self.lifelines.items():
            if available["available"]:
                print(f"\t{available['name']}: {available['description']}")
        
        rounds_played = 0

        skip_round = False
        next_round = False
        end_game = False

        while rounds_played < 5:
            # Check for special round trigger
            if self.player_streaks[player_name] == 3:
                print("\n🌟 Three correct answers in a row! Special round unlocked!")
                special_round = random.choice(["speed", "chain"])
                
                if special_round == "speed":
                    bonus_earnings = self.initiate_speed_round(player)
                elif special_round == "chain":
                    bonus_earnings = self.play_chain_round(player)
                    
                player["earnings"] += bonus_earnings
                self.player_streaks[player_name] = 0
                continue

            start_time = time.time()
            fact_data = self.get_random_fact()
            facts, fake_index, difficulty = fact_data["facts"], fact_data["fake_index"], fact_data["difficulty"]
            
            print(f"\n🔹 Difficulty: {difficulty.capitalize()}")
            print("Which of the following is FALSE?")

            for i, fact in enumerate(facts):
                print(f"{i + 1}. {fact}")

            while True:
                #print current earnings
                print(f"\n💰 Current earnings: {player['earnings']} Naira")
                user_choice = self.get_valid_input(f"\nEnter the number of the fake fact (1-3) or {self.get_available_lifelines_as_prompt_str()}: ", 1, 3, player)
                end_time = time.time()
                if end_time - start_time > self.timer_limit:
                    print("⏰ Time's up! You took too long to answer.")
                    self.apply_safety_logic(player)
                    break

                if str(user_choice).strip().lower() == "hint":
                    if not self.lifelines["hint"]["available"]:
                        print("You have already used the hint lifeline.")
                        continue
                    self.use_hint(fake_index)
                    self.lifelines["hint"]["available"] = False
                    start_time = time.time()
                    continue
                elif str(user_choice).strip().lower() == "bonus":
                    if not self.lifelines["bonus"]["available"]:
                        print("You have already used the bonus lifeline.")
                        continue
                    self.play_bonus_round(player)
                    start_time = time.time()
                    self.lifelines["bonus"]["available"] = False
                    skip_round = True
                    break
                elif str(user_choice).strip().lower() == "skip":
                    if not self.lifelines["skip"]["available"]:
                        print("You have already used the skip lifeline.")
                        continue
                    print("🔄 Skipped! Moving to a new question...")
                    self.lifelines["skip"]["available"] = False
                    start_time = time.time()
                    skip_round = True
                    break
                elif str(user_choice).strip().lower() == "gamble":
                    if not self.lifelines["gamble"]["available"]:
                        print("You have already used the gamble lifeline.")
                        continue
                    print("🎲 Gamble! If you answer correctly, you earn double your earnings. If you answer incorrectly, you lose all your points.")
                    print(f"🎲 You are staking {player['earnings']} for {player['earnings'] * 2}") if player['earnings'] > 0 else print(f"🎲 You are staking {0} for {self.points_per_round * 2}")
                    self.lifelines["gamble"]["available"] = False
                    user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
                    while user_choice not in ['1', '2', '3']:
                        user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)

                    if int(user_choice) - 1 == fake_index:
                        print("🎉 Correct! You win double the points!")
                        player["earnings"] += player["earnings"] if player["earnings"] > 0 else self.points_per_round * 2
                        player["earnings"] += self.points_per_round
                        next_round = True
                    else:
                        print("❌ Wrong! You lost all your points.")
                        player["earnings"] = 0
                    
                    start_time = time.time()
                    break
                elif str(user_choice).strip().lower() == "ask":
                    if not self.lifelines["ask"]["available"]:
                        print("You have already used the ask group lifeline.")
                        continue
                    print("👥 Ask the group! The group thinks the fake fact is number", random.choice([i for i in range(3) if i != fake_index]) + 1)
                    user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
                    while user_choice not in ['1', '2', '3']:
                        user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
                    self.lifelines["ask"]["available"] = False
                    start_time = time.time()
                    break
                elif str(user_choice).strip().lower() == "double":
                    if not self.lifelines["double"]["available"]:
                        print("You have already used the double chance lifeline.")
                        continue
                    print("🎰 Double chance! You get 2 guesses instead of one.")
                    self.lifelines["double"]["available"] = False
                    for _ in range(2):
                        user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
                        while user_choice not in ['1', '2', '3']:
                            user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)

                        if int(user_choice) - 1 == fake_index:
                            # passing on the correct answer logic to the play_round method
                            start_time = time.time()
                            break
                        else:
                            if _ == 0:
                                print("❌ Wrong! You get another chance.")
                            else:
                                 # passing on the wrong answer logic to the play_round method
                                start_time = time.time()
                                break
                    
                    break
                elif str(user_choice).strip().lower() == "reverse":
                    if not self.lifelines["reverse"]["available"]:
                        print("You have already used the reverse stake lifeline.")
                        continue
                    print("🔄 Reverse stake! If you answer correctly, you win double points. If you answer incorrectly, you lose double points.")
                    user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
                    if int(user_choice) - 1 == fake_index:
                       player["earnings"] += self.points_per_round * 2
                       next_round = True
                    else:
                        player["earnings"] -= self.points_per_round * 2
                    self.lifelines["reverse"]["available"] = False
                    start_time = time.time()
                    break
                elif str(user_choice).strip().lower() == "freeze":
                    if not self.lifelines["freeze"]["available"]:
                        print("You have already used the time freeze lifeline.")
                        continue
                    print("⏸️ Time freeze! Timer is now stopped!!")
                    user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
                    while user_choice not in ['1', '2', '3']:
                        user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
                    self.lifelines["freeze"]["available"] = False
                    start_time = time.time()
                    break
                elif str(user_choice).strip().lower() == "quit":
                    print("👋 Goodbye!")
                    self.show_leaderboard()
                    exit()
                elif str(user_choice).strip().lower() == "walk":
                    print(f"🚶 {player_name}, you walk away with your current earnings of {player['earnings']}.")
                    self.apply_safety_logic(player, has_walked=True)
                    end_game = True
                    break
                elif user_choice in ['1', '2', '3']:
                    break
                else:
                    print("Please enter 'hint', 'bonus', or 'skip' to use those options.")
            if end_game:
                break
            if skip_round:
                skip_round = False
                continue
            if next_round:
                next_round = False
                rounds_played += 1
                continue
            end_time = time.time()

            if end_time - start_time > self.timer_limit:
                print("⏰ Time's up! You took too long to answer.")
                self.apply_safety_logic(player)
                break

            if int(user_choice) - 1 == fake_index:
                print("✅ Correct! That fact is fake!")
                player["earnings"] += self.points_per_round
                self.player_streaks[player_name] += 1
            else:
                # print(f"❌ Wrong! You missed the fake fact.")
                print(f"❌ Wrong! The fake fact was: {facts[fake_index]}")
                self.player_streaks[player_name] = 0
                self.apply_safety_logic(player)
                break

            rounds_played += 1

        print(f"\n🏆 {player_name}, your final earnings for this round: {player['earnings']} Naira")
        self.update_leaderboard(player_name, player["earnings"])
        player["earnings"] = 0  
        print("\n🔁 New game starts with the next player!")

    def reset_game(self):
         self.lifelines = {
            "hint": {"available": True, "name": "Hint", "description": "Get a hint to help you find the fake fact."},
            "bonus": {"available": True, "name": "Bonus", "description": "Play a bonus round to earn double points."},
            "skip": {"available": True, "name": "Skip", "description": "Skip the current question and move to the next one."},
            "ask": {"available": True, "name": "Ask the Group", "description": "Ask the group for their opinion on the fake fact."},
            "double": {"available": True, "name": "Double Chance", "description": "Get 2 guesses instead of one."},
            "reverse": {"available": True, "name": "Reverse Stake", "description": "Win double points if you answer correctly, lose double points if you answer incorrectly."},
            "freeze": {"available": True, "name": "Time Freeze", "description": "Stop the timer for the current question."},
            "gamble": {"available": True, "name": "Gamble", "description": "Double your earnings if you answer correctly, lose all your points if you answer incorrectly."}
        }

    def use_hint(self, fake_index):
        print(f"\n🔍 Hint: The fake fact is NOT number {random.choice([i for i in range(3) if i != fake_index]) + 1}.")

    def play_bonus_round(self, player):
        print(f"\n🎰 Bonus Round! Answer correctly to earn DOUBLE ({self.points_per_round} Naira).")
        fact_data = self.get_random_fact()
        facts, fake_index = fact_data["facts"], fact_data["fake_index"]
        
        print("Which of the following is FALSE?")
        for i, fact in enumerate(facts):
            print(f"{i + 1}. {fact}")

        user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
        while user_choice not in ['1', '2', '3']:
            user_choice = self.get_valid_input("\nEnter the number of the fake fact (1-3): ", 1, 3, player)
        if int(user_choice) - 1 == fake_index:
            print(f"🎉 Correct! You win {self.points_per_round} Naira!")
            player["earnings"] += self.points_per_round * 2
        else:
            print("❌ Wrong! You lost the bonus round.")

    def apply_safety_logic(self, player, has_walked=False):
        rounded_earning = max([s for s in self.safety_points if s <= player["earnings"]], default=0) if not has_walked else player["earnings"]
        print(f"\n💰 You reached a safety point of {rounded_earning} Naira. You walk away with that!")
        player["earnings"] = rounded_earning

    def get_available_lifelines_as_prompt_str(self):
        return "/".join([f"'{lifeline}'" for lifeline, available in self.lifelines.items() if available["available"]]) + "/quit/Walk"

    def get_valid_input(self, prompt, min_val, max_val, player):
        while True:
            user_input = input(prompt).strip().lower()
            if user_input in ["hint", "bonus", "skip", "ask", "double", "reverse", "freeze", "gamble", "quit", "walk", 'bank']:
                return user_input
            try:
                choice = int(user_input)
                if min_val <= choice <= max_val:
                    return user_input
                else:
                    print(f"Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def update_leaderboard(self, player_name, earnings):
        if player_name in self.leaderboard:
            self.leaderboard[player_name] += earnings
        else:
            self.leaderboard[player_name] = earnings

    def show_leaderboard(self):
        print("\n🏆 LEADERBOARD 🏆")
        sorted_leaderboard = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
        for rank, (player, earnings) in enumerate(sorted_leaderboard, 1):
            print(f"{rank}. {player} - {earnings} Naira")
        
        print("\n🎉 Thanks for playing 'Find the Fake Fact'! 🎉")
        print("👋 Goodbye!")
        print("\n")
        print("\n")
    
    def play_chain_round(self, player: Dict) -> int:
        """Implement Chain Round with increasing rewards"""
        print("\n🔗 Chain Round Started! Each correct answer increases your reward!")
        chain_earnings = 0
        
        while True:
            fact_data = self.get_random_fact()
            print(f"\nQuestion worth: {self.special_round_point} Naira")
            
            for i, fact in enumerate(fact_data["facts"]):
                print(f"{i + 1}. {fact}")
                
            choice = self.get_valid_input("\nEnter your answer (1-3) or 'bank' to keep your earnings: ", 1, 3, player)
            
            if choice == "bank":
                print(f"Banking {chain_earnings} Naira!")
                return chain_earnings
                
            if int(choice) - 1 == fact_data["fake_index"]:
                round_earning = self.special_round_point
                chain_earnings += round_earning
                multiplier += 1
                print(f"✅ Correct! Chain earnings: {chain_earnings} Naira")
            else:
                print("❌ Wrong! You lose all chain earnings!")
                return 0

    def initiate_speed_round(self, player: Dict) -> int:
        """Implement Speed Round with quick-fire questions"""
        print(f"\n⚡ Speed Round! Answer as many as you can in {self.special_rounds_duration} seconds!")
        speed_earnings = 0
        end_time = time.time() + self.special_rounds_duration
        
        while time.time() < end_time:
            fact_data = self.get_random_fact()
            remaining_time = int(end_time - time.time())
            print(f"\n⏱️ {remaining_time} seconds remaining!")
            
            for i, fact in enumerate(fact_data["facts"]):
                print(f"{i + 1}. {fact}")
                
            choice = self.get_valid_input("Quick! Enter your answer (1-3): ", 1, 3, player)
            
            if int(choice) - 1 == fact_data["fake_index"]:
                speed_earnings += self.special_round_point
                print(f"✅ Correct! Speed earnings: {speed_earnings} Naira")
            else:
                print("❌ Wrong! Next question!")
                
        print(f"\n⏰ Time's up! You earned {speed_earnings} Naira in the Speed Round!")
        return speed_earnings
