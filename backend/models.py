from flask_pymongo import PyMongo
import uuid
from datetime import datetime
from typing import List, Dict, Tuple

# Initialize the database
# This will be imported in app.py

mongo = PyMongo()

EXP_FACTOR = 100  # Base experience factor for leveling up

class Item:
    def __init__(self, name, description):
        self.id = uuid.uuid4()  # Generate a unique ID
        self.name = name
        self.description = description

class Path:
    def __init__(self, description: str, destination_coordinates: Tuple[int, int], cardinal_direction: str):
        self.id = uuid.uuid4()  # Unique identifier
        self.description = description  # A brief description of the path
        self.destination_coordinates: Tuple[int, int] = destination_coordinates  # Tuple for destination coordinates
        self.cardinal_direction = cardinal_direction  # Cardinal direction (north, south, east, west)

class NPC:
    def __init__(self, name: str, description: str, race: str, class_type: str, health: int = 100, mana: int = 100, inventory: List[Item] = None, stats: Dict[str, int] = None, coordinates: Tuple[int, int] = (0, 0), party_potential: int = 0, level: int = 1, experience: int = 0):
        self.id: uuid.UUID = uuid.uuid4()  # Unique identifier
        self.name: str = name
        self.description: str = description
        self.race: str = race
        self.class_type: str = class_type
        self.health: int = health
        self.mana: int = mana
        self.inventory: List[Item] = inventory if inventory is not None else []
        self.stats: Dict[str, int] = stats if stats is not None else {
            'strength': 10,
            'intelligence': 10,
            'wisdom': 10,
            'charisma': 10,
            'stealth': 10,
            'dexterity': 10,
            'constitution': 10
        }
        self.coordinates: Tuple[int, int] = coordinates  # NPC's current coordinates in the GameWorld
        self.party_potential: int = party_potential  # Chance to join the player's party
        self.level: int = level  # NPC's level
        self.experience: int = experience  # NPC's current experience points

    def experience_to_next_level(self):
        return EXP_FACTOR * self.level  # Experience required for the next level

class Location:
    def __init__(self, name: str, description: str, coordinates: Tuple[int, int] = (0, 0), items: List[Item] = None, npcs: List[NPC] = None, paths: List[Path] = None):
        self.id: uuid.UUID = uuid.uuid4()
        self.name: str = name
        self.description: str = description
        self.coordinates: Tuple[int, int] = coordinates
        self.items: List[Item] = items if items is not None else []
        self.npcs: List[NPC] = npcs if npcs is not None else []
        self.paths: List[Path] = paths if paths is not None else []

    def add_item(self, item):
        self.items.append(item)

    def add_npc(self, npc):
        self.npcs.append(npc)

    def add_path(self, path: Path):
        self.paths.append(path)  # Method to add a Path object

    def del_item(self, item):
        if item in self.items:
            self.items.remove(item)

class QuestCriteria:
    def __init__(self, description):
        self.id = uuid.uuid4()  # Unique identifier
        self.description = description  # Description of the objective
        self.completed = False  # Quest completion status

class Quest:
    def __init__(self, name, description, criteria):
        self.id = uuid.uuid4()  # Unique identifier
        self.name = name
        self.description = description
        self.criteria = criteria  # List of QuestCriteria objects
        self.completed = False  # Quest completion status

class Player:
    def __init__(self, name, race, class_type, health=100, mana=100, inventory=None, stats=None, coordinates=(0, 0), level=1, experience=0):
        self.id = uuid.uuid4()  # Unique identifier
        self.name = name
        self.race = race
        self.class_type = class_type
        self.health = health
        self.mana = mana
        self.inventory = inventory if inventory is not None else []  # List of Item objects
        self.stats = stats if stats is not None else {
            'strength': 10,
            'intelligence': 10,
            'wisdom': 10,
            'charisma': 10,
            'stealth': 10,
            'dexterity': 10,
            'constitution': 10
        }
        self.coordinates = coordinates  # Player's current coordinates in the GameWorld
        self.level = level  # Player's level
        self.experience = experience  # Player's current experience points
        self.party_members = []  # List of NPC objects in the player's party
        self.quest_list = []  # List of Quest objects for the player

    def max_party_members(self):
        return (self.level // 10) + 1  # Maximum party members based on player's level

    def experience_to_next_level(self):
        return EXP_FACTOR * self.level  # Experience required for the next level

class GameWorld:
    def __init__(self, player, current_location=None):
        self.id = uuid.uuid4()  # Unique identifier
        self.player = player  # Player object
        self.current_location = current_location  # Current location object
        self.locations = {}  # Dictionary to hold locations by coordinates

    def add_location(self, location):
        self.locations[location.coordinates] = location

    def get_location(self, coordinates):
        return self.locations.get(coordinates, None)  # Returns None if location not found

class GameSave:
    def __init__(self, player, game_world, save_name, user_id):
        self.id = uuid.uuid4()  # Generate a unique ID
        self.player = player
        self.game_world = game_world
        self.save_name = save_name
        self.user_id = user_id  # Link to the user
        self.timestamp = datetime.now()  # Save time

class GameSaves:
    def __init__(self):
        self.id = uuid.uuid4()  # Unique identifier
        self.saves = []  # List of GameSave objects

    def add_save(self, game_save):
        self.saves.append(game_save)

    def del_save(self, game_save):
        if game_save in self.saves:
            self.saves.remove(game_save)

    def get_saves_by_user(self, user_id):
        return [save for save in self.saves if save.user_id == user_id]

class Races:
    VALID_RACES = [
        ("Human", "Versatile and adaptable, with a wide range of skills and cultures"),
        ("Elf", "Graceful and long-lived, with keen senses and a deep connection to nature"),
        ("Dwarf", "Sturdy and skilled craftsmen, known for their resilience and expertise in mining"),
        ("Halfling", "Small and nimble, with a cheerful disposition and surprising resourcefulness"),
        ("Orc", "Strong and fierce warriors, with a proud tribal culture and indomitable spirit"),
        ("Goblin", "Cunning and mischievous, with a knack for tinkering and causing chaos"),
        ("Faun", "Nature-loving and musical, with goat-like features and a carefree attitude"),
    ]

    @classmethod
    def is_valid_race(cls, race):
        return race in cls.VALID_RACES

    @classmethod
    def list_races(cls):
        return cls.VALID_RACES

class CharacterClasses:
    VALID_CLASSES = [
        ("Warrior", "Strong melee fighters skilled in combat and defense"),
        ("Mage", "Spellcasters who harness arcane energies to cast powerful spells"),
        ("Rogue", "Stealthy and agile characters specializing in subterfuge and precision strikes"),
        ("Cleric", "Divine spellcasters who heal allies and smite foes with holy power"),
        ("Ranger", "Skilled archers and trackers with a deep connection to nature"),
        ("Paladin", "Holy warriors who combine martial prowess with divine magic"),
        ("Bard", "Versatile performers who use music and magic to inspire allies and confound enemies"),
    ]

    @classmethod
    def is_valid_class(cls, character_class):
        return any(character_class == c[0] for c in cls.VALID_CLASSES)

    @classmethod
    def list_classes(cls):
        return cls.VALID_CLASSES
