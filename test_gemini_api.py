from typing import Tuple, List, Dict
import google.generativeai as genai
import os
import json
import uuid
import dotenv
import datetime
import glob
from the_veiled_realm.models import (
    GameWorld,
    Player,
    Location,
    Item,
    NPC,
    Path,
    Races,
    CharacterClasses
)

# Load environment variables from .env file in the backend directory
dotenv.load_dotenv(dotenv_path='backend/.env')

# Print the GEMINI_MODEL_NAME for verification
print("GEMINI_MODEL_NAME:", os.getenv('GEMINI_MODEL_NAME'))

# Import the JSON schemas
with open('./initial_loc_schema.json') as f:
    initial_loc_json_schema = json.load(f)
with open('./action_schema.json') as f:
    action_json_schema = json.load(f)

# Configure the Google Gemini API with the API key from the environment variable
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# Function to log LLM responses to a file
def log_llm_response(response_text):
    # Delete the oldest log file if it exists
    log_files = glob.glob('d:/AI/Windsurfer/the_veiled_realm/logs/llm_response_*.log')
    if log_files:
        oldest_log = min(log_files, key=os.path.getctime)
        os.remove(oldest_log)

    # Create a new log file with the current timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'd:/AI/Windsurfer/the_veiled_realm/logs/llm_response_{timestamp}.log'
    with open(log_filename, 'w') as log_file:
        log_file.write(response_text)

# Function to create the starting location based on player attributes
def create_starting_location(player: Player) -> Location:
    prompt = f"""
    Create a starting location for a {player.race} {player.class_type} in a fantasy RPG.
    Creatively work into the narrative:
    1. A detailed description of the surroundings
    2. A unique feature based on the character's class
    3. Three or four paths leading to different Locations
    4. Two to four items that can be found in this location
    5. Zero or more NPCs with different races and classes that can be found in this location
    
    EXTREMELY IMPORTANT: The game expects you to return a 'Location' object in
    JSON format using the following schema (note that the Location class
    is made up of some of the other classes defined here, so you'll need
    to match their structures when you create your JSON response):
    {initial_loc_json_schema}
    """

    model = genai.GenerativeModel(os.getenv('GEMINI_MODEL_NAME'))
    raw_response = model.generate_content(prompt)
    response_text = raw_response.text.strip()
    log_llm_response(response_text)
    json_start = response_text.find('{')
    json_end = response_text.rfind('}') + 1
    response = response_text[json_start:json_end]

    # Attempt to parse the response
    try:
        location_data = json.loads(response)
    except json.JSONDecodeError:
        # Handle JSON decode error
        error_prompt = f"""
        The previous response could not be parsed as JSON. Please provide a valid JSON response for a Location using the following schema:
        {initial_loc_json_schema}
        
        Ensure the response is a single, valid JSON object with no additional text before or after.
        """
        retry_response = model.generate_content(error_prompt)
        retry_text = retry_response.text.strip()
        try:
            location_data = json.loads(retry_text)
        except json.JSONDecodeError:
            print("Failed to decode JSON after retry. Response was:", retry_text)
            return Location(name="Error Location", description="An error occurred while creating the starting location.")

    # Check for required keys in location_data
    required_keys = ['name', 'description']
    missing_keys = [key for key in required_keys if key not in location_data.get('Location', {})]
    if missing_keys:
        print(f"Error: Missing {', '.join(missing_keys)} in location data.")
        return Location(name="Error Location", description="An error occurred while creating the starting location.")

    location_data = location_data.get('Location', {})

    # Create the starting location
    starting_location = Location(
        name=location_data["name"],
        description=location_data["description"],
        coordinates=(0, 0),
    )

    # Add items to the starting location
    if 'items' in location_data:
        for item_data in location_data["items"]:
            if 'name' in item_data and 'description' in item_data:
                item = Item(name=item_data["name"], description=item_data["description"])
                starting_location.add_item(item)
            else:
                print("Error: Missing 'name' or 'description' in item data.")

    # Add NPCs to the starting location
    if 'npcs' in location_data:
        for npc_data in location_data["npcs"]:
            npc = NPC(
                name=npc_data.get("name", "Unknown"),
                description=npc_data.get("description", "No description available."),
                race=npc_data.get("race", "Unknown"),
                class_type=npc_data.get("class_type", "Unknown"),
                health=npc_data.get("health", 100),  # Default health
                mana=npc_data.get("mana", 100)       # Default mana
            )
            starting_location.add_npc(npc)

    # Add paths to the starting location
    if 'paths' in location_data:
        for path_data in location_data["paths"]:
            if 'description' in path_data and 'destination_coordinates' in path_data and 'cardinal_direction' in path_data:
                path = Path(
                    description=path_data["description"],
                    destination_coordinates=path_data["destination_coordinates"],
                    cardinal_direction=path_data["cardinal_direction"]
                )
                starting_location.add_path(path)
            else:
                print("Error: Missing required keys in path data.")

    return starting_location

# Initialize the game state
def get_player_choice(prompt, options, description_getter):
    print(prompt)
    for option, description in options:
        print(f"- {option}: {description}")
    
    while True:
        choice = input("Enter your choice: ")
        if choice in [option[0] for option in options]:
            return choice
        print("Invalid choice. Please choose from the available options.")

def create_player():
    player_name = input("Enter your character's name: ")
    player_race = get_player_choice("Choose your character's race:", Races.list_races(), lambda x: x[1])
    player_class = get_player_choice("Choose your character's class:", CharacterClasses.list_classes(), lambda x: x[1])
    return player_name, player_race, player_class

def generate_stats(race, class_type):
    import random

    base_stats = {
        'strength': 10, 'intelligence': 10, 'wisdom': 10,
        'charisma': 10, 'stealth': 10, 'dexterity': 10, 'constitution': 10
    }
    
    race_modifiers = {
        'Human': {'all': 1},
        'Elf': {'intelligence': 2, 'dexterity': 2, 'constitution': -1},
        'Dwarf': {'strength': 2, 'constitution': 2, 'charisma': -1},
        'Halfling': {'dexterity': 2, 'charisma': 1, 'strength': -1},
        'Orc': {'strength': 3, 'constitution': 1, 'intelligence': -1},
        'Goblin': {'dexterity': 2, 'stealth': 2, 'charisma': -1},
        'Faun': {'charisma': 2, 'dexterity': 1, 'constitution': -1}
    }
    
    class_modifiers = {
        'Warrior': {'strength': 2, 'constitution': 2, 'intelligence': -1},
        'Mage': {'intelligence': 3, 'wisdom': 1, 'strength': -1},
        'Rogue': {'dexterity': 2, 'stealth': 2, 'wisdom': -1},
        'Cleric': {'wisdom': 2, 'charisma': 2, 'dexterity': -1},
        'Ranger': {'dexterity': 2, 'wisdom': 2, 'charisma': -1},
        'Paladin': {'strength': 2, 'charisma': 2, 'stealth': -1},
        'Bard': {'charisma': 2, 'dexterity': 2, 'constitution': -1}
    }

    for stat in base_stats:
        if stat in race_modifiers.get(race, {}):
            base_stats[stat] += race_modifiers[race][stat]
        elif 'all' in race_modifiers.get(race, {}):
            base_stats[stat] += race_modifiers[race]['all']
        
        if stat in class_modifiers.get(class_type, {}):
            base_stats[stat] += class_modifiers[class_type][stat]
        
        base_stats[stat] += random.randint(0, 2)
    
    return base_stats


def handle_game_action(user_input: str, game_state: GameWorld) -> dict:
    model = genai.GenerativeModel(os.getenv('GEMINI_MODEL_NAME'))
    inventory = ', '.join([item.name for item in game_state.player.inventory])
    party_members = ', '.join([f"{member.name} ({member.class_type}, Level {member.level})" for member in game_state.player.party_members]) if game_state.player.party_members else "None"
    active_quests = ', '.join([f"{quest.name} - {quest.description[:50]}..." for quest in game_state.player.quest_list]) if game_state.player.quest_list else "None"
    prompt = f"""
    You are the Game Master of a text-based adventure game. Your role is to interpret player actions, provide narrative responses, and update the game state. The current game state is:

    Player:
        ID: {game_state.player.id}
        Name: {game_state.player.name}
        Race: {game_state.player.race}
        Class: {game_state.player.class_type}
        Health: {game_state.player.health}
        Mana: {game_state.player.mana}
        Level: {game_state.player.level}
        Experience: {game_state.player.experience}
        Inventory: {inventory}
        Stats:
            Strength: {game_state.player.stats['strength']}
            Intelligence: {game_state.player.stats['intelligence']}
            Wisdom: {game_state.player.stats['wisdom']}
            Charisma: {game_state.player.stats['charisma']}
            Stealth: {game_state.player.stats['stealth']}
            Dexterity: {game_state.player.stats['dexterity']}
            Constitution: {game_state.player.stats['constitution']}
        Party Members: {party_members}
        Active Quests: {active_quests}
    Location: {game_state.current_location.name}
    Description: {game_state.current_location.description}

    The player's action is: {user_input}

    Examine this schema and use it as a guide for the JSON objects you will create:
    {action_json_schema}
    your response must be in this exact format:
    {{
        "RESPONSE": "Your narrative response here",
        "GAME_STATE_UPDATE": "A list of JSON objects from the schema above representing the updated game state"
    }}

    Guidelines:
    1. Interpret the player's action in the context of the current game state.
    2. If the action is valid (e.g., "go east" when there's an eastern path), describe the result and update the location.
    3. If the action is invalid (e.g., "go east" when there's no path), explain why it's not possible.
    4. For item interactions, check if the item is in the inventory or current location before allowing its use.
    5. Combat actions should affect health. If health reaches 0, end the game with a creative narrative and add {{"PLAYER_DIED": "yes"}},
    otherwise, {{"PLAYER_DIED": "no"}}.
    6. Maintain internal consistency with previous responses and the game world.
    7. Do not use or refer to any nouns that could be considered copyrighted or trademarked or that is known as existing intellectual property.
    8. Always provide a narrative response, even if it's just a description of the current location.
    9. Always provide a list of JSON objects representing the updated game state.
    10. If the player is moving to another location, always add a JSON object for {{"MOVING": "the cardinal direction"}}
    11. If you add a location object, make sure the key is named "Location".

    Notes:
    - Include only changed state values in GAME_STATE_UPDATE.
    - Use an empty dictionary {{}} if no updates are needed.
    - Ensure all JSON in GAME_STATE_UPDATE is valid and matches the ones in the schema.
    - IMPORTANT: Try to write a creative narrative in the style of a fantasy novel.
    Creatively work into the narrative:
    1. A detailed description of the surroundings
    3. IMPORTANT: One to four paths leading to different Locations. If a cardinal direction is available, use it, otherwise have a valid description of what's blocking it.
    4. Zero to four items that can be found in this location
    5. Zero or more NPCs with different races and classes that can be found in this location
    """
    response = model.generate_content(prompt)
    response_text = response.text
    # response_json = json.loads(response_text)
    # response_text = response_json["RESPONSE"]
    json_start = response_text.find('{')
    json_end = response_text.rfind('}') + 1
    cleaned_response = response_text[json_start:json_end] if json_start != -1 and json_end != -1 else response_text
    log_llm_response(cleaned_response)
    try:
        response_data = json.loads(cleaned_response)
        return response_data
    except json.JSONDecodeError:
        return {
            "RESPONSE": response.text,
            "GAME_STATE_UPDATE": {}
        }

def update_game_state(response_data: dict, game_state: GameWorld) -> None:
    if not response_data:
        return

    updates = response_data
    paths_to_update = []
    for update in updates:
        if any(key.upper() == 'PLAYER' for key in update):
            player_data = update[next(key for key in update if key.upper() == 'PLAYER')]
            for attr, value in player_data.items():
                if hasattr(game_state.player, attr.lower()):
                    setattr(game_state.player, attr.lower(), value)

        if any(key.upper() == 'LOCATION' for key in update):
            location_data = update[next(key for key in update if key.upper() == 'LOCATION')]
            new_location = Location(
                name=location_data.get('name') or location_data.get('NAME'),
                description=location_data.get('description') or location_data.get('DESCRIPTION'),
            )
            new_location.paths = [
                Path(p.get('description') or p.get('DESCRIPTION'),
                     None,  # Destination coordinates will be calculated later
                     p.get('cardinal_direction') or p.get('CARDINAL_DIRECTION'))
                for p in location_data.get('paths') or location_data.get('PATHS', [])
            ]
            paths_to_update.extend(new_location.paths)
            new_location.items = [
                Item(i.get('name') or i.get('NAME'),
                     i.get('description') or i.get('DESCRIPTION'))
                for i in location_data.get('items') or location_data.get('ITEMS', [])
            ]
            game_state.current_location = new_location
            
        if any(key.upper() == 'MOVING' for key in update):
            direction = update[next(key for key in update if key.upper() == 'MOVING')]
            new_coordinates = list(game_state.player.coordinates)
            if direction.upper() == 'NORTH':
                new_coordinates[1] += 1
            elif direction.upper() == 'SOUTH':
                new_coordinates[1] -= 1
            elif direction.upper() == 'EAST':
                new_coordinates[0] += 1
            elif direction.upper() == 'WEST':
                new_coordinates[0] -= 1
            game_state.player.coordinates = tuple(new_coordinates)
            game_state.current_location.coordinates = game_state.player.coordinates

        if any(key.upper() == 'NPCS' for key in update):
            npcs_data = update[next(key for key in update if key.upper() == 'NPCS')]
            for npc_data in npcs_data:
                new_npc = NPC(
                    name=npc_data.get('name', 'Unknown'),
                    description=npc_data.get('description', 'No description available.'),
                    race=npc_data.get('race', 'Unknown'),
                    class_type=npc_data.get('class_type', 'Unknown'),
                    health=npc_data.get('health', 100),
                    mana=npc_data.get('mana', 100),
                    inventory=[Item(item['name'], item['description']) for item in npc_data.get('inventory', [])],
                    stats=npc_data.get('stats', {}),
                    party_potential=npc_data.get('party_potential', 0),
                    level=npc_data.get('level', 1),
                    experience=npc_data.get('experience', 0)
                )
                game_state.current_location.add_npc(new_npc)

    print("\nAvailable paths:")
    # Calculate coordinates for paths after the loop
    for path in paths_to_update:
        print(f"- {path.cardinal_direction.capitalize()}: {path.description}")
        x, y = game_state.current_location.coordinates
        if path.cardinal_direction.upper() == 'NORTH':
            path.destination_coordinates = (x, y + 1)
        elif path.cardinal_direction.upper() == 'SOUTH':
            path.destination_coordinates = (x, y - 1)
        elif path.cardinal_direction.upper() == 'EAST':
            path.destination_coordinates = (x + 1, y)
        elif path.cardinal_direction.upper() == 'WEST':
            path.destination_coordinates = (x - 1, y)

    print(f"Updated location coordinates: {game_state.current_location.coordinates}")
    if game_state.current_location.npcs:
        print(f"NPCs in current location: {', '.join([npc.name for npc in game_state.current_location.npcs])}")
    print(f"Updated location: {game_state.current_location.name}")


if __name__ == '__main__':
    player_name, player_race, player_class = create_player()
    player = Player(
        name=player_name,
        race=player_race,
        class_type=player_class,
        health=100,
        mana=100,
        inventory=[],
        stats=generate_stats(player_race, player_class),
        coordinates=(0, 0),
        level=1,
        experience=0
    )

    starting_location = create_starting_location(player)
    game_state = GameWorld(player=player, current_location=starting_location)

    print(f"Welcome, {game_state.player.name}, to The Veiled Realm! Type 'exit' to quit.")
    print(f"\nYou find yourself in {starting_location.name}.")
    print(starting_location.description)
    if starting_location.paths:
        print("\nAvailable paths:")
        for path in starting_location.paths:
            print(f"- {path.cardinal_direction.capitalize()}: {path.description}")
    else:
        print("\nThere are no visible paths from here.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting the game. Goodbye!")
            break
        try:
            response = handle_game_action(user_input, game_state)
            
            if isinstance(response, dict):
                if "RESPONSE" in response:
                    print("Game Master:", response["RESPONSE"].strip())
                if "GAME_STATE_UPDATE" in response:
                    update_game_state(response["GAME_STATE_UPDATE"], game_state)
            else:
                # If response doesn't match expected format, just print it directly
                print("Game Master:", str(response).strip())
                
        except Exception as e:
            print(f"An error occurred: {e}")
