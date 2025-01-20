from game import Game
import json
import random

class Container:
    def __init__(self, name, description, locked=False, combination=None, key_item=None):
        self.name = name
        self.description = description
        self.items = []
        self.locked = locked
        self.combination = combination  # For combination locks
        self.key_item = key_item       # For key-based locks
        self.is_open = False

class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []
        self.containers = {}  # New dictionary to store containers
        self.requires = None  # For rooms that require specific items to enter

class Item:
    def __init__(self, name, description, readable=False, content=None, revealed_clue=None):
        self.name = name
        self.description = description
        self.readable = readable
        self.content = content
        self.revealed_clue = revealed_clue

class TextAdventureGame(Game):
    def __init__(self, layout_file="game_layouts.json"):
        self.__inventory = []
        self.__rooms = {}
        self.__current_room = None
        self.__objective = None
        self.is_running = True
        self.__items = {}  # Add this line to store all items in the game
        self.__win_condition = None  # Add win condition
        self.__completed = False    # Track if game is completed
        self.__layout_file = layout_file
        self.__command_patterns = {
            "go": ["go", "move", "walk", "run", "travel", "head", "proceed"],
            "take": ["take", "get", "grab", "pick", "collect", "acquire"],
            "drop": ["drop", "leave", "put", "place", "discard"],
            "inventory": ["inventory", "inv", "i", "items", "bag"],
            "quit": ["quit", "exit", "bye", "goodbye", "end"],
            "help": ["help", "commands", "command", "?"],
            "objective": ["objective", "goal", "mission", "task"],
            "read": ["read", "examine", "inspect", "look", "check"],
            "examine": ["examine", "inspect", "look", "check", "study"],
            "open": ["open", "unlock", "access"],
            "close": ["close", "shut"],
            "put": ["put", "place", "insert"],
            "combine": ["combine", "enter", "input"]  # For combination locks
        }
        self.__direction_patterns = {
            "north": ["north", "n", "up north", "northward", "forward"],
            "south": ["south", "s", "down south", "southward", "backward", "back"],
            "east": ["east", "e", "eastward", "right"],
            "west": ["west", "w", "westward", "left"],
            "up": ["up", "u", "upward", "upstairs", "climb up"],
            "down": ["down", "d", "downward", "downstairs", "climb down"]
        }
        self.setup_game()

    def load_layouts(self):
        """Load game layouts from JSON file"""
        try:
            with open(self.__layout_file, 'r') as file:
                layouts = json.load(file)
                return layouts['layouts']
        except FileNotFoundError:
            print(f"Error: Could not find layout file {self.__layout_file}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in layout file {self.__layout_file}")
            return None

    def setup_game(self):
        """Setup game with a random layout from the JSON file"""
        layouts = self.load_layouts()
        if not layouts:
            print("Error loading layouts. Exiting game.")
            self.is_running = False
            return

        # Pick a random layout
        layout = random.choice(layouts)
        self.__objective = layout['objective']
        self.__win_condition = layout.get('win_condition', {})  # Get win condition from layout
        self.__completed = False

         # Create items dictionary
        for item_name, item_data in layout['items'].items():
            self.__items[item_name] = Item(
                item_name,
                item_data['description'],
                item_data.get('readable', False),
                item_data.get('content'),
                item_data.get('revealed_clue')
            )
        
        # Create rooms from the layout
        for room_id, room_data in layout['rooms'].items():
            room = Room(room_data['name'], room_data['description'])
            room.exits = room_data['exits']
            room.items = room_data['items']

            # Set up containers in the room
            if 'containers' in room_data:
                for container_name, container_data in room_data['containers'].items():
                    container = Container(
                        container_name,
                        container_data['description'],
                        container_data.get('locked', False),
                        container_data.get('combination'),
                        container_data.get('key_item')
                    )
                    container.items = container_data.get('items', [])
                    room.containers[container_name] = container

            if 'requires' in room_data:
                room.requires = room_data['requires']
            self.__rooms[room_id] = room

        # Set starting room
        self.__current_room = self.__rooms[layout['startRoom']]
    
    def check_win_condition(self):
        """Check if the win conditions have been met"""
        if not self.__win_condition:
            return False

        # Check if player is in the required room
        if 'room' in self.__win_condition:
            if self.__current_room.name != self.__win_condition['room']:
                return False

        # Check if player has required items
        if 'required_items' in self.__win_condition:
            for item in self.__win_condition['required_items']:
                if item not in self.__inventory:
                    return False
        
        # Check if specific items need to be in specific containers
        if 'container_items' in self.__win_condition:
            for container_name, required_items in self.__win_condition['container_items'].items():
                if container_name not in self.__current_room.containers:
                    return False
                container = self.__current_room.containers[container_name]
                for item in required_items:
                    if item not in container.items:
                        return False
                    
        return True

    def __identify_command(self, user_input):
        """Identifies the core command from user input"""
        words = user_input.lower().split()
        
        for word in words:
            for command, patterns in self.__command_patterns.items():
                if word in patterns:
                    return command, words
        
        return None, words

    def __identify_direction(self, words):
        """Identifies direction from a list of words"""
        for word in words:
            for direction, patterns in self.__direction_patterns.items():
                if word in patterns:
                    return direction
        return None

    def __identify_item(self, words, available_items):
        """Identifies an item from user input"""
        user_phrase = " ".join(words)
        # Check for full item names first
        for item in available_items:
            if item.lower() in user_phrase:
                return item
                
        # Check for partial matches
        for item in available_items:
            words_in_item = item.lower().split()
            for word in words:
                if word in words_in_item:
                    return item
        
        return None

    def get_command(self):
        """Gets and processes user command with natural language understanding"""
        raw_input = input("> ").lower()
        command, words = self.__identify_command(raw_input)
        
        if not command:
            print("\n❓ I'm not sure what you want to do.")
            print("   Try using simple commands like 'go', 'take', or 'read'")
            print("   Type 'help' for a list of commands.")
            return
            
        if command == "quit":
            self.is_running = False
        elif command == "inventory":
            self.show_inventory()
        elif command == "objective":
            self.show_objective()
        elif command == "go":
            direction = self.__identify_direction(words)
            if direction:
                self.move_player(direction)
            else:
                print("\n❓ Which direction do you want to go?")
        elif command == "take":
            #combine the items in the room and the items in the containers
            items = self.__current_room.items + [item for container in self.__current_room.containers.values() for item in container.items if container.is_open]
            print(items)
            item = self.__identify_item(words, items)
            if item:
                self.take_item(item)
            else:
                print("\n❌ What do you want to take?")
        elif command == "drop":
            item = self.__identify_item(words, self.__inventory)
            if item:
                self.drop_item(item)
            else:
                print("\n❌ What do you want to drop?")
        elif command in ["read", "examine"]:
            item_name = self.__identify_item(words, self.__inventory + self.__current_room.items)
            if item_name:
                self.read_item(item_name)
            else:
                print("\n❌ What do you want to read?")
        elif command == "open":
            container_name = self.__identify_container(words)
            if container_name:
                self.open_container(container_name)
            else:
                print("\n❓ What do you want to open?")
        
        elif command == "close":
            container_name = self.__identify_container(words)
            if container_name:
                self.close_container(container_name)
            else:
                print("\n❓ What do you want to close?")
        
        elif command == "put":
            item = self.__identify_item(words, self.__inventory)
            container_name = self.__identify_container(words)
            if item and container_name:
                self.put_item_in_container(item, container_name)
            else:
                print("\n❓ Please specify both an item and a container.")
        
        elif command == "combine":
            container_name = self.__identify_container(words)
            # Look for numbers in the input
            numbers = [word for word in words if word.isdigit()]
            if container_name and numbers:
                self.try_combination(container_name, "".join(numbers))
            else:
                print("\n❓ Please specify a container and combination.")
        elif command == "help":
            self.show_help()
    
    def __identify_container(self, words):
        """Identifies a container from user input"""
        user_phrase = " ".join(words)
        available_containers = self.__current_room.containers.keys()
        
        for container in available_containers:
            if container.lower() in user_phrase:
                return container
        return None
    
    def open_container(self, container_name):
        """Opens a container if possible"""
        container = self.__current_room.containers.get(container_name)
        if not container:
            print(f"\n❌ There's no {container_name} here.")
            return

        if container.is_open:
            print(f"\n❌ The {container_name} is already open.")
            return

        if container.locked:
            if container.key_item:
                if container.key_item not in self.__inventory:
                    print(f"\n🔒 The {container_name} is locked. You need a {container.key_item}.")
                    return
                print(f"\n✨ You unlock the {container_name} with the {container.key_item}.")
            else:
                print(f"\n🔒 The {container_name} is locked. It has a combination lock.")
                return

        container.is_open = True
        print(f"\n✅ You open the {container_name}.")
        if container.items:
            print("\n💡 Inside you find:")
            for item in container.items:
                print(f"   📦 {item}")

    def close_container(self, container_name):
        """Closes an open container"""
        container = self.__current_room.containers.get(container_name)
        if not container:
            print(f"\n❌ There's no {container_name} here.")
            return

        if not container.is_open:
            print(f"\n❌ The {container_name} is already closed.")
            return

        container.is_open = False
        print(f"\n✅ You close the {container_name}.")

    def try_combination(self, container_name, combination):
        """Tries a combination on a locked container"""
        container = self.__current_room.containers.get(container_name)
        if not container:
            print(f"\n❌ There's no {container_name} here.")
            return

        if not container.locked:
            print(f"\n❌ The {container_name} isn't locked.")
            return

        if container.key_item:
            print(f"\n❌ The {container_name} requires a key, not a combination.")
            return

        if combination == container.combination:
            container.locked = False
            print(f"\n✨ Success! The {container_name} unlocks with a satisfying click.")
            self.open_container(container_name)
        else:
            print("\n❌ That combination doesn't work.")

    def put_item_in_container(self, item, container_name):
        """Puts an item into a container"""
        container = self.__current_room.containers.get(container_name)
        if not container:
            print(f"\n❌ There's no {container_name} here.")
            return

        if not container.is_open:
            print(f"\n❌ The {container_name} is closed.")
            return

        if item in self.__inventory:
            self.__inventory.remove(item)
            container.items.append(item)
            print(f"\n✅ You put the {item} in the {container_name}.")
            if self.check_win_condition():  # Check win condition after putting item in container
                self.__completed = True
        else:
            print("\n❌ You don't have that item!")

    
    def read_item(self, item_name):
        """Read or examine an item"""
        item = self.__items[item_name]
        
        # First show the item's description
        print(f"\n📖 {item.description}")
        
        # If the item is readable, show its content
        if item.readable:
            print("\n📜 Upon closer inspection:")
            print(f"   {item.content}")
            
            # If there's a revealed clue, show it
            if item.revealed_clue:
                print(f"\n💡 {item.revealed_clue}")
        else:
            print("\nThere's nothing more to read on this item.")
    
    def handle_game_completion(self):
        """Handle the game completion sequence"""
        if self.__win_condition.get('completion_message'):
            print("\n" + "★" * 50)
            print("🎉 " + self.__win_condition['completion_message'])
            print("★" * 50)
        else:
            print("\n" + "★" * 50)
            print("🎉 Congratulations! You've completed the objective!")
            print("★" * 50)

        while True:
            print("\nWould you like to play again? (yes/no)")
            choice = input("> ").lower().strip()
            if choice in ['yes', 'y']:
                self.reset_game()
                return True
            elif choice in ['no', 'n']:
                self.is_running = False
                return False
            else:
                print("Please answer 'yes' or 'no'")

    def reset_game(self):
        """Reset the game state and start a new game"""
        self.__inventory = []
        self.__rooms = {}
        self.__current_room = None
        self.__objective = None
        self.__win_condition = None
        self.__completed = False
        self.setup_game()

    def move_player(self, direction):
        if direction not in self.__current_room.exits:
            print(f"\n❌ You can't go {direction} from here!")
            return

        next_room = self.__rooms[self.__current_room.exits[direction]]
        
        # Check if the room has requirements
        if next_room.requires:
            required_item = next_room.requires['item']
            if required_item not in self.__inventory:
                print(f"\n🔒 {next_room.requires['message']}")
                return

        self.__current_room = next_room
        print(f"\n✨ You move {direction}.")

        # Check win condition after movement
        if self.check_win_condition():
            self.__completed = True

    def show_objective(self):
        """Display the current game objective with improved formatting"""
        print("\n" + "─" * 50)
        print("🎯 Current Objective:")
        print(f"   {self.__objective}")
        print("─" * 50)

    def show_status(self):
        """Shows current room, description, exits and items with improved formatting"""
        print("\n" + "═" * 50)
        print(f"📍 Location: {self.__current_room.name}")
        print("─" * 50)
        print(f"👁️  {self.__current_room.description}")
        
        # Show exits with directional emojis
        exit_emojis = {
            "north": "⬆️ ",
            "south": "⬇️ ",
            "east": "➡️ ",
            "west": "⬅️ ",
            "up": "↗️ ",
            "down": "↙️ "
        }
        
        if self.__current_room.exits:
            print("\n🚪 Available exits:")
            for direction in self.__current_room.exits.keys():
                emoji = exit_emojis.get(direction, "➡️ ")
                print(f"   {emoji} {direction}")
        
        # Show items in room
        if self.__current_room.items or self.__current_room.containers:
            print("\n💡 You see:")
            if self.__current_room.items:
                for item in self.__current_room.items:
                    print(f"   📦 {item}")
            if self.__current_room.containers:
                for name, container in self.__current_room.containers.items():
                    status = "🔓 (open)" if container.is_open else "🔒 (closed)"
                    print(f"   {status} {name}")
                    if container.is_open and container.items:
                        print("      Contains:")
                        for item in container.items:
                            print(f"      💎 {item}")
            
        # Show inventory
        if self.__inventory:
            print("\n🎒 Inventory:")
            for item in self.__inventory:
                print(f"   💎 {item}")
        
        print("═" * 50)
    
    def take_item(self, item):
        if item in self.__current_room.items:
            self.__current_room.items.remove(item)
            self.__inventory.append(item)
            print(f"\n✅ You take the {item}.")
            if self.check_win_condition():  # Check win condition after taking item
                self.__completed = True
        elif item in [item for container in self.__current_room.containers.values() for item in container.items if container.is_open]:
            # container = self.__current_room.containers[item]
            container = next((container for container in self.__current_room.containers.values() if item in container.items), None)
            if container != None and container.is_open:
                if container.items:
                    container.items.remove(item)
                    self.__inventory.append(item)
                    print(f"\n✅ You take the {item} from 📦 {container.name}.")
                    if self.check_win_condition():  # Check win condition after taking item from container
                        self.__completed = True
                else:
                    print(f"\n❌ The {item} is empty.")
            else:
                print(f"\n❌ The {item} is closed.")
        else:
            print("\n❌ You don't see that here!")
    
    def drop_item(self, item):
        if item in self.__inventory:
            self.__inventory.remove(item)
            self.__current_room.items.append(item)
            print(f"\n✅ You drop the {item}.")
            if self.check_win_condition():  # Check win condition after dropping item (in case it affects the win state)
                self.__completed = True
        else:
            print("\n❌ You don't have that!")

    def show_help(self):
        """Show available commands with improved formatting"""
        print("\n" + "═" * 50)
        print("🎮 Available Commands:")
        print("─" * 50)
        print("  🚶 Movement:")
        print("     go/move/walk [direction] - Move in a direction")
        print("     Example: 'go north' or 'walk to the north'")
        print("\n  📦 Items:")
        print("     take/get/grab [item]    - Pick up an item")
        print("     drop/leave/put [item]   - Drop an item")
        print("     read/examine [item]     - Read or examine an item")
        print("     Example: 'take key' or 'read note'")
        print("\n  📦 Item Container Commands:")
        print("     open [container]        - Open a container")
        print("     close [container]       - Close a container")
        print("     put [item] in [container] - Put an item in a container")
        print("     combine [numbers]       - Try a combination lock")
        print("\n  📝 Other Commands:")
        print("     inventory/inv/i         - Show your inventory")
        print("     objective/goal          - Show current objective")
        print("     help                    - Show this help message")
        print("     quit/exit              - Exit the game")
        print("═" * 50)
    
    def play(self):
        """Main game loop with improved formatting"""
        print("\n" + "═" * 50)
        print("🎮 Welcome to the Adventure!")
        print("Type 'help' for a list of commands.")
        print("═" * 50)
        
        self.show_objective()
        
        while self.is_running:
            self.show_status()
            print("\n💭 What would you like to do?")
            self.get_command()

            # Check if game is completed
            if self.__completed:
                if not self.handle_game_completion():
                    break
                continue
        
        print("\n" + "═" * 50)
        print("👋 Thanks for playing!")
        print("═" * 50)

    def name(self):
        return "Text Adventure"