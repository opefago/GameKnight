from dataclasses import dataclass
from enum import Enum, auto

from util.text_utils import TextUtils

class ObjectType(Enum):
    ROOM = auto()
    ITEM = auto()
    DOOR = auto()
    FURNITURE = auto()
    CONTAINER = auto()
    PERSON = auto()

    @staticmethod
    def from_string(label):
        if label.lower() == "room":
            return ObjectType.ROOM
        elif label.lower() == "item":
            return ObjectType.ITEM
        elif label.lower() == "furniture":
            return ObjectType.FURNITURE
        elif label.lower() == "container":
            return ObjectType.CONTAINER
        elif label.lower() == "person":
            return ObjectType.PERSON
        elif label.lower() == "door":
            return ObjectType.DOOR
        else:
            raise ValueError("Invalid ObjectType label")

    def __str__(self):
        if self == ObjectType.ROOM:
            return "room"
        elif self == ObjectType.ITEM:
            return "item"
        elif self == ObjectType.FURNITURE:
            return "furniture"
        elif self == ObjectType.CONTAINER:
            return "container"
        elif self == ObjectType.PERSON:
            return "person"
        elif self == ObjectType.DOOR:
            return "door"

class GameObject:
    def __init__(self, name, type, description,  actions=[], position=None):
        self.name = name
        self.description = description
        self.position = position
        self.actions = actions
        self.type = type
    def __str__(self):
        return self.name + ", " + self.description + ", " + str(self.position) + ", " + str(self.actions) + ", " + str(self.type)
    
    def action(self, command, gameDispatcher):
        if command['action'] in self.actions:
            return gameDispatcher.dispatch(command)
        else:
            return "You can't do that."
        

# First, add a Furniture class
class Furniture(GameObject):
    def __init__(self, name, description, liftable=False, hidden_items=None):
        super().__init__(name, ObjectType.FURNITURE, description,  ['lift'])
        self.name = name
        self.description = description
        self.liftable = liftable
        self.hidden_items = hidden_items or []  # Items hidden under this furniture
        self.reavealed_items = []  # Items revealed when this furniture is lifted
        self.is_lifted = False  # Track if furniture has been lifted
        self.behind_items = []  # Items behind this furniture

@dataclass
class Position:
    preposition: str  # on, under, beside, hanging on
    reference_item: str = None  # what item this is relative to

class Container(GameObject):
    def __init__(self, name, description, locked=False, combination=None, key_item=None):
        super().__init__(name, ObjectType.CONTAINER , description,  ['open', 'close', 'look', 'combine'])
        self.name = name
        self.description = description
        self.items = []
        self.locked = locked
        self.combination = combination  # For combination locks
        self.key_item = key_item       # For key-based locks
        self.is_open = False

class Room(GameObject):
    def __init__(self, name, description):
        super().__init__(name, ObjectType.ROOM, description, ['look', 'go'])
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []
        self.containers = {}  # New dictionary to store containers
        self.objects = {}  # New dictionary to store objects
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
    def add_items(self, new_item_names):
        for name in new_item_names:
            self.items.append({'name': name})

class Item(GameObject):
    def __init__(self, name, description, readable=False, content=None, revealed_clue=None):
        super().__init__(name, ObjectType.ITEM, description, ['take', 'read', 'use', 'drop'])
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


class RequirementType(Enum):
    ITEM = auto()
    ACTION = auto()
    COMBINATION = auto()

@dataclass
class Requirement:
    type: RequirementType
    targets: list = None

class Door(GameObject):
    def __init__(self, name, description, locked=False):
        super().__init__(name, ObjectType.ITEM, description, ['open', 'close', 'look', 'use'])
        self.locked = locked
        self.requirement = None

class EnhancedRoom(Room):
    def __init__(self, name, description, persons={}):
        super().__init__(name, description)
        self.revealed_items = set()
        self.furniture = {}
        self.persons = persons
        self.is_dark = False
        self.door = None

    def get_all_items(self):
        return [
            key
            for key, value in self.objects.items()
            if hasattr(value, 'type') and value.type == ObjectType.ITEM
        ] + [
            item
            for key, value in self.objects.items()
            if hasattr(value, 'type') and value.type == ObjectType.CONTAINER and getattr(value, 'is_open', False)
            for item in getattr(value, 'items', [])
        ]
    
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
            item = self.objects[item_name]
            if hasattr(item, 'position') and item.position:
                # Skip hidden items that haven't been revealed
                if item.position.preposition == "under" and item_name not in self.revealed_items:
                    continue

                if item.position.preposition == "behind":
                    ref = item.position.reference_item
                    if ref not in furniture_items:
                        furniture_items[ref] = []
                    furniture_items[ref].append(item_name)
                    continue
                
                ref = item.position.reference_item
                if ref not in furniture_items:
                    furniture_items[ref] = []
                furniture_items[ref].append(item_name)
            else:
                standalone_items.append(item_name)

        for furniture_name, furniture in self.objects.items():
             if furniture.type == ObjectType.FURNITURE:
                furniture_text = [TextUtils.find_replace_enbolden(furniture.description, furniture_name)]
                if furniture.is_lifted:
                    furniture_text.append("It has been moved from its original position.")
                if furniture_name in furniture_items:
                    items = furniture_items[furniture_name]
                    if items:
                        preposition = self.objects[items[0]].position.preposition
                        item_descriptions = [TextUtils.find_replace_enbolden(self.objects[i].description, self.objects[i].name) for i in items]
                        furniture_text.append(f"{preposition.capitalize()} it, you see {self._list_to_natural_language(item_descriptions)}.")
                descriptions.append(" ".join(furniture_text))

        #Describe persons
        for person_name, person in self.objects.items():
            if person.type == ObjectType.PERSON:
                person_text = []
                if person.position:
                    ref = person.position.reference_item
                    article = "an" if person_name[0] in list("aeiou") else "a"
                    ref_obj = self.objects.get(ref, None)
                    if ref_obj and ref_obj.type == ObjectType.FURNITURE:
                        article = "an" if person_name[0] in list("aeiou") else "a"
                        person_text.append(f"{article} {TextUtils.enbolden(person_name)} is {person.position.preposition} the {self.furniture[ref].lower()}.")
                    elif ref_obj and ref_obj.type == ObjectType.ITEM:
                        item_article = "an" if ref_obj.description[0] in list("aeiou") else "a"
                        person_text.append(f"{article} {TextUtils.enbolden(person_name)} is {person.position.preposition} {item_article} {ref_obj.description}.")
                    else:
                        person_text.append(f"{article} {TextUtils.enbolden(person_name)} is {person.position.preposition} the {ref}.")
                person_text.append(person.description)
                descriptions.append(" ".join(person_text))
        
        if standalone_items:
            descriptions.append("In the room, you also see " + 
                             self._list_to_natural_language([self.objects[i].description for i in standalone_items]) + ".")

        return "\n\n".join(descriptions)

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
        for name, container in self.objects.items():
            if container.type != ObjectType.CONTAINER:
                continue
            status = "open" if container.is_open else "closed"
            desc = f"{TextUtils.find_replace_enbolden(container.description, container.name)} The {TextUtils.enbolden(name)} is {status}."
            if container.is_open and container.items:
                item_descs = [TextUtils.find_replace_enbolden(self.objects[i].description, self.objects[i].name) for i in container.items]
                desc += f" Inside, you can see {self._list_to_natural_language(item_descs)}."
            descriptions.append(desc)
        return "\n".join(descriptions) if descriptions else ""


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
        super().__init__(name, ObjectType.PERSON, description,['talk'], position)
        self.name = name
        self.description = description
        self.dialogues = dialogues
        self.position = position