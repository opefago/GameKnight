from game import Game
from dataclasses import dataclass
import json
import random

# First, add a Furniture class
class Furniture:
    def __init__(self, description, liftable=False, hidden_items=None):
        self.description = description
        self.liftable = liftable
        self.hidden_items = hidden_items or []  # Items hidden under this furniture
        self.is_lifted = False  # Track if furniture has been lifted

@dataclass
class Position:
    preposition: str  # on, under, beside, hanging on
    reference_item: str = None  # what item this is relative to

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

class EnhancedItem(Item):
    def __init__(self, name, description, readable=False, content=None, revealed_clue=None, position=None, reveals=None, size="medium"):
        super().__init__(name, description, readable, content, revealed_clue)
        self.position = position  # Position object
        self.reveals = reveals or []   # List of items revealed when this item is taken
        self.size = size         # small, medium, large

class EnhancedRoom(Room):
    def __init__(self, name, description, items_dict=None, persons={}):
        super().__init__(name, description)
        self.revealed_items = set()
        self.furniture = {}
        self.persons = persons
        self.items_dict = items_dict or {}  # Store reference to game's items dictionary
    
    def describe_furniture_and_items(self):
        """Returns a naturally worded description of the room's furniture and visible items"""
        descriptions = []
        
        # First add the base room description
        # descriptions.append(self.description)
        
        # Then describe each piece of furniture and its associated items
        furniture_items = {}
        standalone_items = []

        persons = {}
        standalone_persons = []
        
        # # Group items by their furniture reference
        for item_name in self.items:
            item = self.items_dict[item_name]
            if hasattr(item, 'position') and item.position:
                # Skip hidden items that haven't been revealed
                if item.position.preposition == "under" and item_name not in self.revealed_items:
                    continue
                
                ref = item.position.reference_item
                if ref not in furniture_items:
                    furniture_items[ref] = []
                furniture_items[ref].append(item_name)
            else:
                standalone_items.append(item_name)

        # # Describe each piece of furniture and its items
        # for furniture_name, furniture_desc in self.furniture.items():
        #     furniture_text = [furniture_desc]
        #     if furniture_name in furniture_items:
        #         items = furniture_items[furniture_name]
        #         if items:
        #             preposition = self.items_dict[items[0]].position.preposition
        #             item_descriptions = [self.items_dict[i].description for i in items]
        #             furniture_text.append(f"{preposition.capitalize()} it, you see {self._list_to_natural_language(item_descriptions)}.")
        #     descriptions.append(" ".join(furniture_text))

        # # Add standalone items
        # if standalone_items:
        #     descriptions.append("In the room, you also see " + 
        #                      self._list_to_natural_language([self.items_dict[i].description for i in standalone_items]) + ".")

        # # Add revealed items
        # revealed = [i for i in self.revealed_items if i in self.items]
        # if revealed:
        #     descriptions.append("You can now see " + 
        #                      self._list_to_natural_language([self.items_dict[i].description for i in revealed]) + ".")

        # return "\n\n".join(descriptions)
        # Then describe each piece of furniture and its associated items
        for furniture_name, furniture in self.furniture.items():
            furniture_text = [furniture.description]
            if furniture.is_lifted:
                furniture_text.append("It has been moved from its original position.")
            if furniture_name in furniture_items:
                items = furniture_items[furniture_name]
                if items:
                    preposition = self.items_dict[items[0]].position.preposition
                    item_descriptions = [self.items_dict[i].description for i in items]
                    furniture_text.append(f"{preposition.capitalize()} it, you see {self._list_to_natural_language(item_descriptions)}.")
            descriptions.append(" ".join(furniture_text))

        #Describe persons
        for person_name, person in self.persons.items():
            person_text = []
            if person.position:
                ref = person.position.reference_item
                article = "an" if person_name[0] in list("aeiou") else "a"
                if ref in self.furniture:
                    article = "an" if person_name[0] in list("aeiou") else "a"
                    person_text.append(f"{article} {person_name} is {person.position.preposition} the {self.furniture[ref].lower()}.")
                elif ref in self.items_dict:
                    item = self.items_dict[ref]
                    item_article = "an" if item.description[0] in list("aeiou") else "a"
                    person_text.append(f"{article} {person_name} is {person.position.preposition} {item_article} {self.items_dict[ref].description}.")
                else:
                    person_text.append(f"{article} {person_name} is {person.position.preposition} the {ref}.")
            person_text.append(person.description)
            descriptions.append(" ".join(person_text))
        
        if standalone_items:
            descriptions.append("In the room, you also see " + 
                             self._list_to_natural_language([self.items_dict[i].description for i in standalone_items]) + ".")

        # Add visible items
        # visible_items = [i for i in self.items if i in self.items_dict]
        # if visible_items:
        #     descriptions.append("You can see " + 
        #                      self._list_to_natural_language([self.items_dict[i].description for i in visible_items]) + ".")

        return "\n\n".join(descriptions)

    def get_descriptive_item_list(self):
        """Returns a naturally worded description of visible items in the room"""
        descriptions = []
        
        # Group items by their positions
        hanging_items = []
        on_items = {}
        under_items = {}
        beside_items = {}
        standalone_items = []
        
        for item_name in self.items:
            item = self.items_dict[item_name]
            # Skip items that should be hidden
            if hasattr(item, 'position') and item.position:
                if item.position.preposition == "under" and item_name not in self.revealed_items:
                    continue
                    
                if item.position.preposition == "hanging on":
                    hanging_items.append(item_name)
                elif item.position.preposition == "on":
                    ref = item.position.reference_item
                    on_items.setdefault(ref, []).append(item_name)
                elif item.position.preposition == "under":
                    ref = item.position.reference_item
                    under_items.setdefault(ref, []).append(item_name)
                elif item.position.preposition == "beside":
                    ref = item.position.reference_item
                    beside_items.setdefault(ref, []).append(item_name)
            else:
                standalone_items.append(item_name)

        # Create natural language descriptions
        if hanging_items:
            descriptions.append("Hanging on the walls, you see " + 
                             self._list_to_natural_language([self.items_dict[i].description for i in hanging_items]))
        
        for furniture, items in on_items.items():
            if furniture in self.furniture:
                descriptions.append(f"{self.furniture[furniture]} On it, you see " + 
                                 self._list_to_natural_language([self.items_dict[i].description for i in items]))
        
        for furniture, items in beside_items.items():
            if furniture in self.furniture:
                descriptions.append(f"Beside {self.furniture[furniture].lower()}, you notice " + 
                                 self._list_to_natural_language([self.items_dict[i].description for i in items]))
        
        revealed = [i for i in self.revealed_items if i in self.items]
        if revealed:
            descriptions.append("You can now see " + 
                             self._list_to_natural_language([self.items_dict[i].description for i in revealed]))
        
        if standalone_items:
            descriptions.append("In the room, you also see " + 
                             self._list_to_natural_language([self.items_dict[i].description for i in standalone_items]))
        
        return "\n".join(descriptions) if descriptions else "There's nothing of particular interest here."

    def _list_to_natural_language(self, items):
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return ", ".join(items[:-1]) + f", and {items[-1]}"

    def describe_containers(self):
        """Returns a natural description of visible containers"""
        descriptions = []
        for name, container in self.containers.items():
            status = "open" if container.is_open else "closed"
            desc = f"{container.description} The {name} is {status}."
            if container.is_open and container.items:
                item_descs = [self.items_dict[i].description for i in container.items]
                desc += f" Inside, you can see {self._list_to_natural_language(item_descs)}."
            descriptions.append(desc)
        return "\n".join(descriptions) if descriptions else ""


from enum import Enum

class InteractionType(Enum):
    PASSIVE = 1
    ACTIVE = 2

    @staticmethod
    def from_string(label):
        if label.lower() == "passive":
            return InteractionType.PASSIVE
        elif label.lower() == "active":
            return InteractionType.ACTIVE
        else:
            raise ValueError("Invalid InteractionType label")
            

class InteractionAction(Enum):
    NEXT = 1
    PREVIOUS = 2
    END = 3

    @staticmethod
    def from_string(label):
        if label.lower() == "next":
            return InteractionAction.NEXT
        elif label.lower() == "previous":
            return InteractionAction.PREVIOUS
        elif label.lower() == "end":
            return InteractionAction.END
        else:
            raise ValueError("Invalid IteractionAction label")

class InteractionResponse:
    def __init__(self, response, actions=[InteractionAction.END]):
        self.response = response
        self.actions = actions


class Interaction:
    def __init__(self, name, prompt, interaction_type=InteractionType.PASSIVE, responses=[]):
        self.name = name
        self.prompt = prompt
        self.interaction_type = interaction_type
        self.responses = responses

class Person:
    def __init__(self, name, description, position=None, dialogues=[]):
        self.name = name
        self.description = description
        self.dialogues = dialogues
        self.position = position

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
        words = user_input.lower().split()
        
        for word in words:
            for command, patterns in self._command_patterns.items():
                if word in patterns:
                    return command, words
        
        return None, words

    def _identify_direction(self, words):
        """Identifies direction from a list of words"""
        for word in words:
            for direction, patterns in self._direction_patterns.items():
                if word in patterns:
                    return direction
        return None

    def _identify_item(self, words, available_items):
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
        command, words = self._identify_command(raw_input)
        
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
            direction = self._identify_direction(words)
            if direction:
                self.move_player(direction)
            else:
                print("\n❓ Which direction do you want to go?")
        elif command == "take":
            #combine the items in the room and the items in the containers
            items = self._current_room.items + [item for container in self._current_room.containers.values() for item in container.items if container.is_open]
            item = self._identify_item(words, items)
            if item:
                self.take_item(item)
            else:
                print("\n❌ What do you want to take?")
        elif command == "drop":
            item = self._identify_item(words, self._inventory)
            if item:
                self.drop_item(item)
            else:
                print("\n❌ What do you want to drop?")
        elif command in ["read", "examine"]:
            item_name = self._identify_item(words, self._inventory + self._current_room.items)
            if item_name:
                self.read_item(item_name)
            else:
                print("\n❌ What do you want to read?")
        elif command == "open":
            container_name = self._identify_container(words)
            if container_name:
                self.open_container(container_name)
            else:
                print("\n❓ What do you want to open?")
        
        elif command == "close":
            container_name = self._identify_container(words)
            if container_name:
                self.close_container(container_name)
            else:
                print("\n❓ What do you want to close?")
        
        elif command == "put":
            item = self._identify_item(words, self._inventory)
            container_name = self._identify_container(words)
            if item and container_name:
                self.put_item_in_container(item, container_name)
            else:
                print("\n❓ Please specify both an item and a container.")
        
        elif command == "combine":
            container_name = self._identify_container(words)
            # Look for numbers in the input
            numbers = [word for word in words if word.isdigit()]
            if container_name and numbers:
                self.try_combination(container_name, "".join(numbers))
            else:
                print("\n❓ Please specify a container and combination.")

        elif command == "help":
            self.show_help()
    
    def _identify_container(self, words):
        """Identifies a container from user input"""
        user_phrase = " ".join(words)
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
                    print(f"   📦 {item}")
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
        if item in self._current_room.items:
            self._current_room.items.remove(item)
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
            self._current_room.items.append(item)
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
        self._inventory = []
        self._rooms = {}
        self._current_room = None
        self._objective = None
        self.is_running = True
        self._items = {}
        self._win_condition = None
        self._completed = False
        self._layout_file = layout_file
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
            position_data = item_data.get('position', {})
            self._items[item_name] = EnhancedItem(
                item_name,
                item_data['description'],
                item_data.get('readable', False),
                item_data.get('content'),
                item_data.get('revealed_clue'),
                Position(
                    position_data.get('preposition', None),
                    position_data.get('reference', None)
                ) if position_data else None,
                item_data.get('reveals', []),
                item_data.get('size', 'medium')
            )

        # Create rooms with furniture
        for room_id, room_data in layout['rooms'].items():
            room = EnhancedRoom(room_data['name'], room_data['description'], self._items)
            room.exits = room_data['exits']
            room.items = room_data['items']
            
            # Create Furniture objects
            for furniture_name, furniture_data in room_data.get('furniture', {}).items():
                if isinstance(furniture_data, str):
                    # Handle old format where furniture was just a description
                    furniture = Furniture(furniture_data, liftable=False)
                else:
                    # Handle new format with full furniture data
                    furniture = Furniture(
                        furniture_data['description'],
                        liftable=furniture_data.get('liftable', False),
                        hidden_items=furniture_data.get('hidden_items', [])
                    )
                room.furniture[furniture_name] = furniture
            
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
        if item in self._current_room.items:
            item_obj = self._items[item]
            if hasattr(item_obj, 'position') and item_obj.position:
                if item_obj.position.preposition == "under" and item not in self._current_room.revealed_items:
                    print(f"\n❌ You don't see the {item} anywhere obvious.")
                    return
            
            self._current_room.items.remove(item)
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
        if furniture_name not in self._current_room.furniture:
            print(f"\n❌ You don't see {furniture_name} here.")
            return

        furniture = self._current_room.furniture[furniture_name]
        
        if not furniture.liftable:
            print(f"\n❌ The {furniture_name} is too heavy to lift or cannot be moved.")
            return
            
        if furniture.is_lifted:
            print(f"\n❌ You've already moved the {furniture_name}.")
            return

        furniture.is_lifted = True
        
        if furniture.hidden_items:
            # Add hidden items to the room
            self._current_room.items.extend(furniture.hidden_items)
            # Add to revealed items
            self._current_room.revealed_items.update(furniture.hidden_items)
            items_desc = ", ".join(furniture.hidden_items)
            print(f"\n✨ You lift the {furniture_name} and find: {items_desc}")
        else:
            print(f"\n❌ You lift the {furniture_name} but find nothing underneath.")

    def show_status(self):
        """Shows current room with enhanced descriptions"""
        print("\n" + "═" * 50)
        print(f"📍 Location: {self._current_room.name}")
        print("─" * 50)
        print(f"👁️  {self._current_room.description}\n")

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
    
    def get_command(self):
        """Gets and processes user command with natural language understanding"""
        raw_input = input("> ").lower()
        command, words = self._identify_command(raw_input)
        
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
            direction = self._identify_direction(words)
            if direction:
                self.move_player(direction)
            else:
                print("\n❓ Which direction do you want to go?")
        elif command == "take":
            #combine the items in the room and the items in the containers
            items = self._current_room.items + [item for container in self._current_room.containers.values() for item in container.items if container.is_open]
            print(items)
            item = self._identify_item(words, items)
            if item:
                self.take_item(item)
            else:
                print("\n❌ What do you want to take?")
        elif command == "drop":
            item = self._identify_item(words, self._inventory)
            if item:
                self.drop_item(item)
            else:
                print("\n❌ What do you want to drop?")
        elif command in ["read", "examine"]:
            item_name = self._identify_item(words, self._inventory + self._current_room.items)
            if item_name:
                self.read_item(item_name)
            else:
                print("\n❌ What do you want to read?")
        elif command == "open":
            container_name = self._identify_container(words)
            if container_name:
                self.open_container(container_name)
            else:
                print("\n❓ What do you want to open?")
        
        elif command == "close":
            container_name = self._identify_container(words)
            if container_name:
                self.close_container(container_name)
            else:
                print("\n❓ What do you want to close?")
        
        elif command == "put":
            item = self._identify_item(words, self._inventory)
            container_name = self._identify_container(words)
            if item and container_name:
                self.put_item_in_container(item, container_name)
            else:
                print("\n❓ Please specify both an item and a container.")
        
        elif command == "combine":
            container_name = self._identify_container(words)
            # Look for numbers in the input
            numbers = [word for word in words if word.isdigit()]
            if container_name and numbers:
                self.try_combination(container_name, "".join(numbers))
            else:
                print("\n❓ Please specify a container and combination.")

        elif command == "lift":
            # First check if it's a piece of furniture
            furniture_name = next((f for f in self._current_room.furniture.keys() 
                                if f.lower() in " ".join(words).lower()), None)
            if furniture_name:
                self.lift_furniture(furniture_name)
        elif command == "help":
            self.show_help()
        elif command == "lift":
            # First check if it's a piece of furniture
            furniture_name = next((f for f in self._current_room.furniture.keys() 
                                if f.lower() in " ".join(words).lower()), None)
            if furniture_name:
                self.lift_furniture(furniture_name)
            else:
                print("\n❓ What do you want to lift?")
        