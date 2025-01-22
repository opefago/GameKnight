from dataclasses import dataclass


class GameObject:
    def __init__(self, name, description, position=None):
        self.name = name
        self.description = description
        self.position = position

# First, add a Furniture class
class Furniture(GameObject):
    def __init__(self, name, description, liftable=False, hidden_items=None):
        super().__init__(name, description)
        self.name = name
        self.description = description
        self.liftable = liftable
        self.hidden_items = hidden_items or []  # Items hidden under this furniture
        self.is_lifted = False  # Track if furniture has been lifted

@dataclass
class Position:
    preposition: str  # on, under, beside, hanging on
    reference_item: str = None  # what item this is relative to

class Container(GameObject):
    def __init__(self, name, description, locked=False, combination=None, key_item=None):
        super().__init__(name, description)
        self.name = name
        self.description = description
        self.items = []
        self.locked = locked
        self.combination = combination  # For combination locks
        self.key_item = key_item       # For key-based locks
        self.is_open = False

class Room(GameObject):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []
        self.containers = {}  # New dictionary to store containers
        self.requires = None  # For rooms that require specific items to enter
    
    def find_item(self, name_to_find):
        # Using a loop to find the item
        for item in self.items:
            if item['name'] == name_to_find:
                return item
        return None
    def remove_item(self, item_name):
       # Using a loop to remove the item
        for item in self.items:
            if item['name'] == item_name:
                self.items.remove(item)
                break
    def add_items(self, items, new_item_names):
        for name in new_item_names:
            self.items.append({'name': name})

class Item(GameObject):
    def __init__(self, name, description, readable=False, content=None, revealed_clue=None):
        super().__init__(name, description)
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
        for item_obj in self.items:
            item_name = item_obj['name']
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

class Person(GameObject):
    def __init__(self, name, description, position=None, dialogues=[]):
        super().__init__(name, description, position)
        self.name = name
        self.description = description
        self.dialogues = dialogues
        self.position = position