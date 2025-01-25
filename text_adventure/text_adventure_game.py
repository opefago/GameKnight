from game import Game
import json
import random

from text_adventure.command_dispatcher import CommandDispatcher
from text_adventure.command_parser import CommandParser
from text_adventure.game_objects import Container, Door, EnhancedItem, EnhancedRoom, Furniture, Interaction, InteractionAction, InteractionResponse, InteractionType, Item, ObjectType, Person, Position, Requirement, Room
from util.text_utils import TextUtils

class TextAdventureGame(Game):
    def __init__(self, layout_file="game_layouts.json"):
        self._inventory = []
        self._rooms = {}
        self._current_room = None
        self._objective = None
        self.is_running = True
        self._items = {}  # Add this line to store all items in the game
        self._win_condition = None  # Add win condition
        self._completed = False    # Track if game is completed
        self._layout_file = layout_file
        self.dispatcher = CommandDispatcher(self)
        self._command_patterns = {
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
            "combine": ["combine", "enter", "input"],  # For combination locks
            "lift": ["lift", "raise", "move", "shift", "check under"]
        }
        self._direction_patterns = {
            "north": ["north", "n", "up north", "northward", "forward"],
            "south": ["south", "s", "down south", "southward", "backward", "back"],
            "east": ["east", "e", "eastward", "right"],
            "west": ["west", "w", "westward", "left"],
            "up": ["up", "u", "upward", "upstairs", "climb up"],
            "down": ["down", "d", "downward", "downstairs", "climb down"]
        }
        self.parser = CommandParser()
        self.setup_game()

    def load_layouts(self):
        """Load game layouts from JSON file"""
        try:
            with open(self._layout_file, 'r') as file:
                layouts = json.load(file)
                return layouts['layouts']
        except FileNotFoundError:
            print(f"Error: Could not find layout file {self._layout_file}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in layout file {self._layout_file}")
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
        self._objective = layout['objective']
        self._win_condition = layout.get('win_condition', {})  # Get win condition from layout
        self._completed = False

         # Create items dictionary
        for item_name, item_data in layout['items'].items():
            self._items[item_name] = Item(
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
            
            for item in room_data['items']:
                item_name = item['name']
                position = item.get('position', {})
                item_obj = self._items[item_name]
                item_obj.position = Position(
                    position.get('preposition', None),
                    position.get('reference', None)
                )
                room.objects[item_name] = item_obj

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
                    room.objects[container_name] = container

            if 'requires' in room_data:
                room.requires = room_data['requires']
            self._rooms[room_id] = room

        # Set starting room
        self._current_room = self._rooms[layout['startRoom']]
    
    def check_win_condition(self):
        """Check if the win conditions have been met"""
        if not self._win_condition:
            return False

        # Check if player is in the required room
        if 'room' in self._win_condition:
            if self._current_room.name != self._win_condition['room']:
                return False

        # Check if player has required items
        if 'required_items' in self._win_condition:
            for item in self._win_condition['required_items']:
                if item not in self._inventory:
                    return False
        
        # Check if specific items need to be in specific containers
        if 'container_items' in self._win_condition:
            for container_name, required_items in self._win_condition['container_items'].items():
                if container_name not in self._current_room.containers:
                    return False
                container = self._current_room.containers[container_name]
                for item in required_items:
                    if item not in container.items:
                        return False
                    
        return True

    def _identify_command(self, user_input):
        """Identifies the core command from user input"""
        return self.parser.parse_command(user_input)

    def _identify_direction(self, words):
        """Identifies direction from a list of words"""
        for word in words:
            for direction, patterns in self._direction_patterns.items():
                if word in patterns:
                    return direction
        return None

    def _identify_item(self, command, available_items):
        """Identifies an item from user input"""
        user_phrase = command['direct_object']
        # Check for full item names first
        for item in available_items:
            if item.lower() in user_phrase:
                return item
                
        # Check for partial matches
        for item in available_items:
            words_in_item = item.lower().split()
            for word in user_phrase.split():
                if word in words_in_item:
                    return item
        
        return None

    def get_command(self):
        """Gets and processes user command with natural language understanding"""
        raw_input = input("> ").lower()
        command = self._identify_command(raw_input)
        
        if not command['action']:
            print("\n❓ I'm not sure what you want to do.")
            print("   Try using simple commands like 'go', 'take', or 'read'")
            print("   Type 'help' for a list of commands.")
            return
            
        if command["action"] == "quit":
            self.is_running = False
        elif command["action"] == "inventory":
            self.show_inventory()
        elif command["action"] == "objective":
            self.show_objective()
        elif command["action"] == "go":
            direction = self._identify_direction(command["direction"])
            if direction:
                self.move_player(direction)
            else:
                print("\n❓ Which direction do you want to go?")
        elif command["action"] == "take":
            #combine the items in the room and the items in the containers
            items = [item['name'] for item in self._current_room.items] + [item for container in self._current_room.containers.values() for item in container.items if container.is_open]
            item = self._identify_item(command, items)
            if item:
                self.take_item(item)
            else:
                print("\n❌ What do you want to take?")
        elif command["action"] == "drop":
            item = self._identify_item(command, self._inventory)
            if item:
                self.drop_item(item)
            else:
                print("\n❌ What do you want to drop?")
        elif command["action"] in ["read", "examine"]:
            item_name = self._identify_item(command, self._inventory + self._current_room.items)
            if item_name:
                self.read_item(item_name)
            else:
                print("\n❌ What do you want to read?")
        elif command["action"] == "open":
            container_name = self._identify_container(command)
            if container_name:
                self.open_container(container_name)
            else:
                print("\n❓ What do you want to open?")
        
        elif command["action"] == "close":
            container_name = self._identify_container(command)
            if container_name:
                self.close_container(container_name)
            else:
                print("\n❓ What do you want to close?")
        
        elif command["action"] == "put":
            item = self._identify_item(command, self._inventory)
            container_name = self._identify_container(command)
            if item and container_name:
                self.put_item_in_container(item, container_name)
            else:
                print("\n❓ Please specify both an item and a container.")
        
        elif command["action"] == "combine":
            container_name = self._identify_container(command)
            # Look for numbers in the input
            numbers = [word for word in command["direct_object"].split() if word.isdigit()]
            if len(numbers) == 0:
                numbers = [word for word in command["indirect_object"].split() if word.isdigit()]
            if container_name and numbers:
                self.try_combination(container_name, "".join(numbers))
            else:
                print("\n❓ Please specify a container and combination.")

        elif command["action"] == "help":
            self.show_help()
    
    def _identify_container(self, command):
        """Identifies a container from user input"""
        user_phrase = command['direct_object']
        available_containers = self._current_room.containers.keys()
        
        for container in available_containers:
            if container.lower() in user_phrase:
                return container
        return None
    
    def open_container(self, container_name):
        """Opens a container if possible"""
        container = self._current_room.containers.get(container_name)
        if not container:
            print(f"\n❌ There's no {container_name} here.")
            return

        if container.is_open:
            print(f"\n❌ The {container_name} is already open.")
            return

        if container.locked:
            if container.key_item:
                if container.key_item not in self._inventory:
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
        container = self._current_room.containers.get(container_name)
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
        container = self._current_room.containers.get(container_name)
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
        container = self._current_room.containers.get(container_name)
        if not container:
            print(f"\n❌ There's no {container_name} here.")
            return

        if not container.is_open:
            print(f"\n❌ The {container_name} is closed.")
            return

        if item in self._inventory:
            self._inventory.remove(item)
            container.items.append(item)
            print(f"\n✅ You put the {item} in the {container_name}.")
            if self.check_win_condition():  # Check win condition after putting item in container
                self._completed = True
        else:
            print("\n❌ You don't have that item!")

    def read_item(self, item_name):
        """Read or examine an item"""
        item = self._items[item_name]

        # first read the item description
        print(f"\n📖 {item.description}")
        # If the item is readable, show its content
        if item.readable:
            print("\n📜 Upon closer inspection:")
            print(f"   {item.content}")
            
            # If there's a revealed clue, show it
            if item.revealed_clue:
                print(f"\n💡 {item.revealed_clue}")
        
            
    
    def handle_game_completion(self):
        """Handle the game completion sequence"""
        if self._win_condition.get('completion_message'):
            print("\n" + "★" * 50)
            print("🎉 " + self._win_condition['completion_message'])
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
        self._inventory = []
        self._rooms = {}
        self._current_room = None
        self._objective = None
        self._win_condition = None
        self._completed = False
        self.setup_game()

    def move_player(self, direction):
        if direction not in self._current_room.exits:
            print(f"\n❌ You can't go {direction} from here!")
            return

        next_room = self._rooms[self._current_room.exits[direction]]
        
        # Check if the room has requirements
        if next_room.requires:
            required_item = next_room.requires['item']
            if required_item not in self._inventory:
                print(f"\n🔒 {next_room.requires['message']}")
                return

        self._current_room = next_room
        print(f"\n✨ You move {direction}.")

        # Check win condition after movement
        if self.check_win_condition():
            self._completed = True

    def show_objective(self):
        """Display the current game objective with improved formatting"""
        print("\n" + "─" * 50)
        print("🎯 Current Objective:")
        print(f"   {self._objective}")
        print("─" * 50)

    def show_status(self):
        """Shows current room, description, exits and items with improved formatting"""
        print("\n" + "═" * 50)
        print(f"📍 Location: {self._current_room.name}")
        print("─" * 50)
        print(f"👁️  {self._current_room.description}")
        
        # Show exits with directional emojis
        exit_emojis = {
            "north": "⬆️ ",
            "south": "⬇️ ",
            "east": "➡️ ",
            "west": "⬅️ ",
            "up": "↗️ ",
            "down": "↙️ "
        }
        
        if self._current_room.exits:
            print("\n🚪 Available exits:")
            for direction in self._current_room.exits.keys():
                emoji = exit_emojis.get(direction, "➡️ ")
                print(f"   {emoji} {direction}")
        
        # Show items in room
        if self._current_room.items or self._current_room.containers:
            print("\n💡 You see:")
            if self._current_room.items:
                for item in self._current_room.items:
                    print(f"   📦 {item['name']}")
            if self._current_room.containers:
                for name, container in self._current_room.containers.items():
                    status = "🔓 (open)" if container.is_open else "🔒 (closed)"
                    print(f"   {status} {name}")
                    if container.is_open and container.items:
                        print("      Contains:")
                        for item in container.items:
                            print(f"      💎 {item}")
            
        # Show inventory
        if self._inventory:
            print("\n🎒 Inventory:")
            for item in self._inventory:
                print(f"   💎 {item}")
        
        print("═" * 50)
    
    def take_item(self, item):
        found_item = self._current_room.find_item(item)
        if found_item:
            self._current_room.remove_item(item)
            self._inventory.append(item)
            print(f"\n✅ You take the {item}.")
            if self.check_win_condition():  # Check win condition after taking item
                self._completed = True
        elif item in [item for container in self._current_room.containers.values() for item in container.items if container.is_open]:
            # container = self._current_room.containers[item]
            container = next((container for container in self._current_room.containers.values() if item in container.items), None)
            if container != None and container.is_open:
                if container.items:
                    container.items.remove(item)
                    self._inventory.append(item)
                    print(f"\n✅ You take the {item} from 📦 {container.name}.")
                    if self.check_win_condition():  # Check win condition after taking item from container
                        self._completed = True
                else:
                    print(f"\n❌ The {item} is empty.")
            else:
                print(f"\n❌ The {item} is closed.")
        else:
            print("\n❌ You don't see that here!")
    
    def drop_item(self, item):
        if item in self._inventory:
            self._inventory.remove(item)
            self._current_room.items.append({'name': item})
            print(f"\n✅ You drop the {item}.")
            if self.check_win_condition():  # Check win condition after dropping item (in case it affects the win state)
                self._completed = True
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
            if self._completed:
                if not self.handle_game_completion():
                    break
                continue
        
        print("\n" + "═" * 50)
        print("👋 Thanks for playing!")
        print("═" * 50)

    def name(self):
        return "Text Adventure"



class EnhancedTextAdventureGame(TextAdventureGame):
    def __init__(self, layout_file="game_layouts.json"):
        super().__init__(layout_file)
        self._inventory = []
        self._rooms = {}
        self._current_room = None
        self._objective = None
        self.is_running = True
        self._items = {}
        self._win_condition = None
        self._completed = False
        self._layout_file = layout_file
        self.dispatcher = CommandDispatcher(self)
        self._setup_commands()
        self.setup_game()

    def _setup_commands(self):
        self._command_patterns = {
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
            "combine": ["combine", "enter", "input"],
            "lift": ["lift", "raise", "move", "shift", "check under"]
        }
        
        self._direction_patterns = {
            "north": ["north", "n", "up north", "northward", "forward"],
            "south": ["south", "s", "down south", "southward", "backward", "back"],
            "east": ["east", "e", "eastward", "right"],
            "west": ["west", "w", "westward", "left"],
            "up": ["up", "u", "upward", "upstairs", "climb up"],
            "down": ["down", "d", "downward", "downstairs", "climb down"]
        }

    # Update the setup_game method in EnhancedTextAdventureGame
    def setup_game(self):
        """Setup game with enhanced room and furniture descriptions"""
        layouts = self.load_layouts()
        if not layouts:
            print("Error loading layouts. Exiting game.")
            self.is_running = False
            return

        layout = random.choice(layouts)
        self._objective = layout['objective']
        self._win_condition = layout.get('win_condition', {})
        self._completed = False

        # Create items
        for item_name, item_data in layout['items'].items():
            # position_data = item_data.get('position', {})
            self._items[item_name] = EnhancedItem(
                item_name,
                item_data['description'],
                item_data.get('readable', False),
                item_data.get('content'),
                item_data.get('revealed_clue'),
                None,
                item_data.get('reveals', []),
                item_data.get('size', 'medium')
            )

        # Create rooms with furniture
        for room_id, room_data in layout['rooms'].items():

            room_items_dict = {}
            for item in room_data['items']:
                item_name = item['name']
                room_obj = self._items[item_name]
                position_data = item.get('position', {})
                room_obj.position = Position(
                    position_data.get('preposition', None),
                    position_data.get('reference', None)
                )
                room_items_dict[item_name] = room_obj

            room = EnhancedRoom(room_data['name'], room_data['description'], room_items_dict)
            door = room_data.get('door', None)
            # //name, description, locked=False, key_item=None
            if door:
                room.door = Door(door.get('name', 'door'), door.get('description', 'A simple door'), door.get('locked', False))
                requirement = door.get('requirement', None)
                if requirement:
                    room.door.requirement = Requirement(requirement.get('type', None), requirement.get('targets', None))

                room.objects[door.get('name', 'door')] = room.door

            room.exits = room_data['exits']
            room.items = room_data['items']
            room.objects = room.objects | room_items_dict

            
            
            # Create Furniture objects
            for furniture_name, furniture_data in room_data.get('furniture', {}).items():
                if isinstance(furniture_data, str):
                    # Handle old format where furniture was just a description
                    furniture = Furniture('', furniture_data, liftable=False)
                else:
                    # Handle new format with full furniture data
                    furniture = Furniture(
                        furniture_data['name'] if 'name' in furniture_data else '',
                        furniture_data['description'],
                        liftable=furniture_data.get('liftable', False),
                        hidden_items=furniture_data.get('hidden_items', [])
                    )
                room.objects[furniture_name] = furniture
            
            # create persons in the room
            for person_name, person_data in room_data.get('persons', {}).items():
                position_data = person_data.get('position', None)

                interactions = []
                for interaction_data in person_data.get('interactions', []):
                    responses = []
                    for response_data in interaction_data.get('responses', []):
                        responses.append(InteractionResponse(
                            response_data['response'],
                            [InteractionAction.from_string(a) for a in response_data.get('actions', [])]
                        ))
                    interactions.append(Interaction(
                        interaction_data['name'],
                        interaction_data['prompt'],
                        InteractionType.from_string(interaction_data.get('type', 'passive')),
                        responses
                    ))
                    
                person = Person(
                    person_name,
                    person_data['description'],
                    Position(
                        position_data.get('preposition', None),
                        position_data.get('reference', None)
                    ) if position_data else None,
                    interactions
                )
                room.persons[person_name] = person
                room.objects[person_name] = person

            # Handle containers and other room setup...
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
                    room.objects[container_name] = container

                    for item_name in container.items:
                        item_obj = self._items[item_name]
                        item_obj.position = Position(
                            'in',
                            container_name
                        )
                        if item_name not in room.objects:
                            room.objects[item_name] = item_obj

            if 'requires' in room_data:
                room.requires = room_data['requires']
            self._rooms[room_id] = room
        self._current_room = self._rooms[layout['startRoom']]
    
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

        print("\n  📦 Furniture interaction Commands:")
        print("     lift/raise/move [furniture]   - Lift or move an furniture to check underneath")

        print("\n  📝 Other Commands:")
        print("     inventory/inv/i         - Show your inventory")
        print("     objective/goal          - Show current objective")
        print("     help                    - Show this help message")
        print("     quit/exit              - Exit the game")
        print("═" * 50)

    def take_item(self, item):
        """Enhanced take item that reveals hidden items"""
        found_item = self._current_room.find_item(item)
        if found_item:
            item_obj = self._items[item]
            if found_item['position']:
                if found_item['position']['preposition'] == "under" and item not in self._current_room.revealed_items:
                    print(f"\n❌ You don't see the {item} anywhere obvious.")
                    return
            
            self._current_room.remove_item(item)
            self._inventory.append(item)
            print(f"\n✅ You take the {item}.")
            
            # Handle revealing hidden items
            if hasattr(item_obj, 'reveals') and item_obj.reveals:
                revealed = item_obj.reveals
                self._current_room.revealed_items.update(revealed)
                print(f"\nMoving the {item} reveals: {', '.join(revealed)}")
                self._current_room.items.extend(revealed)
                
            if self.check_win_condition():
                self._completed = True
        else:
            # Check containers
            found_in_container = False
            for container in self._current_room.containers.values():
                if container.is_open and item in container.items:
                    container.items.remove(item)
                    self._inventory.append(item)
                    print(f"\n✅ You take the {item} from the {container.name}.")
                    found_in_container = True
                    if self.check_win_condition():
                        self._completed = True
                    break
            
            if not found_in_container:
                print("\n❌ You don't see that here!")

    # Add the lift_furniture method
    def lift_furniture(self, furniture_name):
        """Attempt to lift a piece of furniture"""
        furniture = self._current_room.objects[furniture_name]

        if not furniture:
            print(f"\n❌ You don't see {furniture_name} here.")
            return

        if not furniture.type == ObjectType.FURNITURE:
            print(f"\n❌ You can't lift the {furniture_name}.")
            return
        
        if not furniture.liftable:
            print(f"\n❌ The {furniture_name} is too heavy to lift or cannot be moved.")
            return
            
        if furniture.is_lifted:
            print(f"\n❌ You've already moved the {furniture_name}.")
            return
        
        #find all the items in the room hidden under the furniture
        hidden_items = [item['name'] for item in self._current_room.items if item['position'] and item['position']['preposition'] == "under" and item['position']['reference'] == furniture_name]

        furniture.is_lifted = True
        # Add to revealed items
        self._current_room.revealed_items.update(hidden_items)
        items_desc = ", ".join(hidden_items)
        print(f"\n✨ You lift the {furniture_name} and find: {items_desc}")
        

    def show_status(self):
        """Shows current room with enhanced descriptions"""
        print("\n" + "═" * 50)
        print(f"📍 Location: {self._current_room.name}")
        print("─" * 50)
        print(f"👁️  {self._current_room.description}\n")
        
        if self._current_room.is_dark:
            self._current_room.is_dark = False
            print("🌑 The room is dark. You can't see anything.")
            print("🔦 You might need a light source to see better.")
            print("🔦 You can use the 'take torch' command to pick up a torch.")
            print("🔦 Once you have the torch, you can use the 'light torch' command to illuminate the room.")
            print("🔦 The torch will automatically light up dark rooms.")
            print("🔦 You can also use the 'inventory' command to check your items.")
            print("🔦 Try 'help' for a list of commands.")
            print("═" * 50)
            return
            


        # Show room description with furniture and items
        print(self._current_room.describe_furniture_and_items())
        
        # Show item descriptions
        # items_desc = self._current_room.get_descriptive_item_list()
        # if items_desc:
        #     print(f"\n{items_desc}")
        
        # Show container descriptions
        containers_desc = self._current_room.describe_containers()
        if containers_desc:
            print(f"\n{containers_desc}")
        
        # Show exits
        if self._current_room.exits:
            print("\n🚪 You can go:")
            for direction in self._current_room.exits.keys():
                print(f"   ➡️ {direction}")
        
        # Show inventory
        if self._inventory:
            print("\n🎒 In your inventory:")
            for item in self._inventory:
                print(f"   💎 {item}")
        
        print("═" * 50)

    def go(self, command):
        """Move the player in a direction"""
        direction = self._identify_direction(command["direction"])
        if direction:
            self.move_player(direction)
        else:
            print("\n❓ Which direction do you want to go?")
    def look_in_direction(self, direction):
        if direction in self._current_room.exits:
            next_room = self._rooms[self._current_room.exits[direction]]
            print(f"\n👁️  You look to the {direction} and see:")
            if next_room.door:
                print(f"   {TextUtils.enbolden(next_room.door.description, next_room.door.name)}")
            elif next_room.is_dark:
                print(f"   A dark room. From here, you can't make out what's inside.")
            else:
                print(f"   {TextUtils.enbolden(next_room.name)}")
            
        else:
            print(f"\n❌ There's no exit to the {direction}.")
    
    def look(self, command):
        """Look around the room for items and exits"""
        direction = command.get('direction', None)
        if direction:
            self.look_in_direction(direction)
        else:
            direct_object = command.get('direct_object', None)
            if direct_object:
                self.look_at_object(direct_object)

    def inventory(self, command):
        """Show the player's inventory"""
        self.show_inventory()
    
    def take(self, command):
        """Take an item from the room"""
        item = self._identify_item(command, self._current_room.get_all_items())
        if item:
            self.take_item(item)
        else:
            print("\n❌ What do you want to take?")

    def drop(self, command):
        """Drop an item from the player's inventory"""
        item = self._identify_item(command, self._inventory)
        if not item:
            print("\n❌ What do you want to drop?")
            return
        preposition = command.get('preposition', None)
        if preposition == "in":
            container_name = command.get('direct_object', None)
            if container_name:
                object =self._current_room.objects[container_name]
                if object.type == "container":
                    self.put_item_in_container(item, container_name)
                    return
                else:
                    print("\n❓ You can't put it in that.")
                    return
            else:
                print("\n❓ What do you want to drop?")
                return
        elif preposition == "on":
            furniture_name = command.get('reference', None)
            if furniture_name:
                furniture = self._current_room.objects[furniture_name]
                if furniture.type == ObjectType.FURNITURE:
                    position = Position("on", furniture_name)
                    self._current_room.objects[item].position = position
                    self.drop_item(item)
                    return
                elif furniture.type == "person":
                    print("\n❓ Shocking you want to put it on that person.")
                else: 
                    print("\n❓ You can't put it on that.")
                return
            else:
                print("\n❓ What do you want to put it on?")
                return
        
        self.drop_item(item)
        
    def quit(self, command):
        """Quit the game"""
        self.is_running = False

    def help(self, command):
        """Show available commands"""
        self.show_help()
    
    def read(self, command):
        """Read or examine an item"""
        item_name = self._identify_item(command, self._inventory + self._current_room.get_all_items())
        if item_name:
            self.read_item(item_name)
        else:
            print("\n❌ What do you want to read?")

    def combine(self, command):
        """Try a combination on a locked container"""
        container_name = self._identify_container(command)
        # Look for numbers in the input
        numbers = [word for word in command["direct_object"].split() if word.isdigit()]
        if len(numbers) == 0:
            numbers = [word for word in command["indirect_object"].split() if word.isdigit()]
        if container_name and numbers:
            self.try_combination(container_name, "".join(numbers))
        else:
            print("\n❓ Please specify a container and combination.")
    def put(self, command):
        """Put an item into a container"""
        item = self._identify_item(command, self._inventory)
        container_name = self._identify_container(command)
        if item and container_name:
            self.put_item_in_container(item, container_name)
        else:
            print("\n❓ Please specify both an item and a container.")

    def open(self, command):
        """Open a container"""
        container_name = self._identify_container(command)
        if container_name:
            self.open_container(container_name)
        else:
            print("\n❓ What do you want to open?")

    def close(self, command):
        """Close a container"""
        container_name = self._identify_container(command)
        if container_name:
            self.close_container(container_name)
        else:
            print("\n❓ What do you want to close?")

    def talk(self, command):
        """Talk to a person in the room"""
        person_name = command.get('direct_object', None)
        if person_name:
            person = self._current_room.persons.get(person_name)
            if person:
                self.talk_to_person(person)
            else:
                print(f"\n❌ There's no {person_name} here.")
        else:
            print("\n❓ Who do you want to talk to?")
    
    def objective(self, command):
        """Show the current objective"""
        self.show_objective()

    def light_torch(self):
        if self._inventory.count("torch") > 0:
            if self._current_room.is_dark:
                self._current_room.is_dark = False
                print("\n✨ The room is now illuminated.")
            else:
                print("\n❓ The room is already lit. Do you want to look around?")
        else:
            print("\n❌ You do not have a light source in your inventory, do you want to look around?")
    
    def light(self, command):
        """Light up a dark room"""
        direct_object = command.get('direct_object', None)
        if not direct_object:
            print("\n❓ What do you want to light?")
            return
        if direct_object == "torch":
            self.light_torch()
        else:
            print("\n❓ What do you want to light?")

    def lift(self, command):
        """Lift a piece of furniture"""
        furniture_name = command.get('direct_object', None)
        if furniture_name:
            self.lift_furniture(furniture_name)
        else:
            print("\n❓ What do you want to lift?")

    def show_inventory(self):
        """Show the player's inventory"""
        if self._inventory:
            print("\n🎒 Inventory:")
            for item in self._inventory:
                print(f"   💎 {item}")
        else:
            print("\n🎒 Your inventory is empty.")
    
    def open_container(self, container_name):
        """Opens a container if possible"""
        container = self._current_room.containers.get(container_name)
        if not container:
            print(f"\n❌ There's no {container_name} here.")
            return

        if container.is_open:
            print(f"\n❌ The {container_name} is already open.")
            return

        if container.locked:
            if container.key_item:
                if container.key_item not in self._inventory:
                    print(f"\n🔒 The {container_name} is locked. You need a {container.key_item}.")
                    return
                print(f"\n✨ You unlock the {container_name} with the {container.key_item}.")
            else:
                print(f"\n🔒 The {container_name} is locked. It has a combination lock.")
                return

        container.is_open = True
        print(f"\n✅ You open the {container_name}.")
        if self.check_win_condition():  # Check win condition after opening container
            self._completed = True
    
    def get_command(self):
        """Gets and processes user command with natural language understanding"""
        raw_input = input("> ").lower()
        command = self._identify_command(raw_input)
        
        if not command['action']:
            print("\n❓ I'm not sure what you want to do.")
            print("   Try using simple commands like 'go', 'take', or 'read'")
            print("   Type 'help' for a list of commands.")
            return
            
        if command["action"] == "quit":
            self.is_running = False
        elif command["action"] == "inventory":
            self.show_inventory()
        elif command["action"] == "objective":
            self.show_objective()
        elif command["action"] == "help":
            self.show_help()
        elif command["action"] == "go":
            self.go(command)
        elif command["action"] == "look" and command.get("direction"):
            self.look(command)
        else:
            direct_object = command.get("direct_object", None)
            if not direct_object:
                print("\n❓ Can you elaborate what you would like to do with that action?")
                print(f"   Try adding object to your sentence like '{command['action']} item name'")
                return
            object = self._current_room.objects.get(direct_object, None)
            if object:
                object.action(command, self.dispatcher)
            else:
                print("\n❌ You don't see that here!")
        # elif command["action"] == "go":
        #     direction = self._identify_direction(command["direction"])
        #     if direction:
        #         self.move_player(direction)
        #     else:
        #         print("\n❓ Which direction do you want to go?")
        # elif command["action"] == "take":
        #     object = self._current_room.objects[command["direct_object"]]
        #     print(object)
            
        #     #combine the items in the room and the items in the containers
        #     items = [item['name'] for item in self._current_room.items] + [item for container in self._current_room.containers.values() for item in container.items if container.is_open]
        #     item = self._identify_item(command, items)
        #     if item:
        #         self.take_item(item)
        #     else:
        #         print("\n❌ What do you want to take?")
        # elif command["action"] == "drop":
        #         item = self._identify_item(command, self._inventory)
        #         if item:
        #             self.drop_item(item)
        #         else:
        #             print("\n❌ What do you want to drop?")
        # elif command["action"] in ["read", "examine"]:
        #     item_name = self._identify_item(command, self._inventory + [item['name'] for item in self._current_room.items])
        #     if item_name:
        #         self.read_item(item_name)
        #     else:
        #         print("\n❌ What do you want to read?")
        # elif command["action"] == "open":
        #     container_name = self._identify_container(command)
        #     if container_name:
        #         self.open_container(container_name)
        #     else:
        #         print("\n❓ What do you want to open?")
        
        # elif command["action"] == "close":
        #     container_name = self._identify_container(command)
        #     if container_name:
        #         self.close_container(container_name)
        #     else:
        #         print("\n❓ What do you want to close?")
        
        # elif command["action"] == "put":
        #     item = self._identify_item(command, self._inventory)
        #     container_name = self._identify_container(command)
        #     if item and container_name:
        #         self.put_item_in_container(item, container_name)
        #     else:
        #         print("\n❓ Please specify both an item and a container.")
        
        # elif command["action"] == "combine":
        #     container_name = self._identify_container(command)
        #     # Look for numbers in the input
        #     numbers = [word for word in command["direct_object"].split() if word.isdigit()]
        #     if len(numbers) == 0:
        #         numbers = [word for word in command["indirect_object"].split() if word.isdigit()]
        #     if container_name and numbers:
        #         self.try_combination(container_name, "".join(numbers))
        #     else:
        #         print("\n❓ Please specify a container and combination.")
        
        # elif command["action"] == "lift":
        #     # First check if it's a piece of furniture
        #     furniture_name = next((f for f in self._current_room.furniture.keys() 
        #                         if f.lower() == command["direct_object"].lower()), None)
        #     if furniture_name:
        #         self.lift_furniture(furniture_name)
        #     else:
        #         print("\n❓ What do you want to lift?")
        