import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS
import google.generativeai as genai
from config import Config
import time
import threading
from models import GameWorld, Player, NPC, Quest, QuestCriteria  # Import your models

app = Flask(__name__)
CORS(app, resources=r'/api/*')  # Enable CORS for all routes that start with /api

app.config.from_object(Config)

mongo = PyMongo(app)

# Configure the Google Gemini API with the API key from the environment variable
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# Global variable for autosave interval
AUTOSAVE_INTERVAL = 600  # 10 minutes in seconds

# Function to save the GameWorld and its children to the database
def save_game_world(game_world):
    try:
        # Save the player
        player_data = {
            'id': str(game_world.player.id),
            'name': game_world.player.name,
            'race': game_world.player.race,
            'class_type': game_world.player.class_type,
            'level': game_world.player.level,
            'experience': game_world.player.experience,
            'coordinates': game_world.player.coordinates,
            'inventory': [{'id': str(item.id), 'name': item.name, 'description': item.description} for item in game_world.player.inventory],
            'quests': [{'id': str(quest.id), 'name': quest.name, 'completed': quest.completed} for quest in game_world.player.quest_list],
        }
        mongo.db.players.update_one({'id': player_data['id']}, {'$set': player_data}, upsert=True)

        # Save NPCs
        for npc in game_world.npcs:
            npc_data = {
                'id': str(npc.id),
                'name': npc.name,
                'race': npc.race,
                'class_type': npc.class_type,
                'level': npc.level,
                'experience': npc.experience,
                'coordinates': npc.coordinates,
                'inventory': [{'id': str(item.id), 'name': item.name, 'description': item.description} for item in npc.inventory],
            }
            mongo.db.npcs.update_one({'id': npc_data['id']}, {'$set': npc_data}, upsert=True)

        # Save locations
        for location in game_world.locations.values():
            location_data = {
                'id': str(location.id),
                'name': location.name,
                'description': location.description,
                'coordinates': location.coordinates,
                'items': [{'id': str(item.id), 'name': item.name, 'description': item.description} for item in location.items],
                'npcs': [{'id': str(npc.id)} for npc in location.npcs],
            }
            mongo.db.locations.update_one({'id': location_data['id']}, {'$set': location_data}, upsert=True)

        print("GameWorld saved successfully to the_veiled_realm.db")
    except Exception as e:
        print(f"Error saving GameWorld to the_veiled_realm.db: {e}")

# Function for autosaving the GameWorld
def autosave(game_world):
    while True:
        save_game_world(game_world)
        time.sleep(AUTOSAVE_INTERVAL)

# Function to start the autosave feature
def start_autosave(game_world):
    autosave_thread = threading.Thread(target=autosave, args=(game_world,))
    autosave_thread.daemon = True  # Allows thread to exit when the main program exits
    autosave_thread.start()

@app.route('/api/players', methods=['POST'])
def create_player():
    data = request.json
    player = {
        "name": data['name'],
        "race": data['race'],
        "class_type": data['class_type'],
        "health": 100,
        "mana": 100,
        "inventory": {},
        "game_state": {},
        "stats": {
            "strength": data.get('strength', 10),
            "intelligence": data.get('intelligence', 10),
            "charisma": data.get('charisma', 10),
            "stealth": data.get('stealth', 10),
            "dexterity": data.get('dexterity', 10)
        }
    }
    mongo.db.players.insert_one(player)

    # Prepare input for the LLM
    input_text = f"Create a character named {player['name']} who is a {player['race']} {player['class_type']} with the following stats: {player['stats']}"

    # Interact with the LLM using the Google Gemini API
    # Assuming you want to get a response from the API
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(input_text)
    player['description'] = response.text

    return jsonify({'playerId': str(player['_id']), 'description': player['description']}), 201

@app.route('/api/players', methods=['GET'])
def list_players():
    players = mongo.db.players.find()  # Fetch all players from the database
    player_list = []
    for player in players:
        player['_id'] = str(player['_id'])  # Convert ObjectId to string
        player_list.append(player)

    return jsonify(player_list), 200

@app.route('/players', methods=['GET'])
def list_players_old():
    players = mongo.db.players.find()
    return jsonify([{ "id": str(player['_id']), "name": player['name'], "race": player['race'], "class_type": player['class_type']} for player in players]), 200

@app.route('/api/players/<player_id>', methods=['GET'])
def get_player(player_id):
    player = mongo.db.players.find_one({'_id': player_id})  # Fetch the player by ID
    if player:
        player['_id'] = str(player['_id'])  # Convert ObjectId to string
        return jsonify(player), 200
    return jsonify({'error': 'Player not found'}), 404

@app.route('/players/<player_id>', methods=['GET'])
def get_player_old(player_id):
    player = mongo.db.players.find_one({"_id": player_id})
    if player:
        return jsonify({"id": str(player['_id']), "name": player['name'], "race": player['race'], "class_type": player['class_type']}), 200
    return jsonify({"error": "Player not found"}), 404

@app.route('/players/<player_id>', methods=['PUT'])
def update_player(player_id):
    data = request.json
    result = mongo.db.players.update_one({"_id": player_id}, {"$set": data})
    if result.modified_count > 0:
        return jsonify({"message": "Player updated successfully"}), 200
    return jsonify({"error": "Player not found or no changes made"}), 404

@app.route('/players/<player_id>', methods=['DELETE'])
def delete_player(player_id):
    result = mongo.db.players.delete_one({"_id": player_id})
    if result.deleted_count > 0:
        return jsonify({"message": "Player deleted successfully"}), 200
    return jsonify({"error": "Player not found"}), 404

@app.route('/api/players/<player_id>/load', methods=['GET'])
def load_game(player_id):
    player = mongo.db.players.find_one({'_id': player_id})  # Fetch the player by ID
    if player:
        player['_id'] = str(player['_id'])  # Convert ObjectId to string
        return jsonify(player), 200
    return jsonify({'error': 'Player not found'}), 404

@app.route('/character-creation/<player_id>', methods=['GET'])
def character_creation(player_id):
    # Logic to render the character creation page
    return render_template('character_creation.html', player_id=player_id)

@app.route('/api/game_action', methods=['POST'])
def game_action():
    data = request.get_json()
    action = data.get('action')
    
    # Here you would use the Gemini LLM to generate a response based on the action
    response = generate_response(action)  # Implement this function to interact with Gemini
    
    return jsonify({'response': response})

@app.route('/')
def home():
    return 'Welcome to The Veiled Realm!'

if __name__ == '__main__':
    app.run(debug=True)
