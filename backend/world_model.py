class Location:
    def __init__(self, name, description, coordinates, is_passable=True):
        self.name = name  # Name of the location
        self.description = description  # Description of the location
        self.coordinates = coordinates  # Tuple (x, y) for location in the world
        self.is_passable = is_passable  # True if the player can move here
        self.items = []  # List of items present in the location
        self.dwellings = []  # List of dwellings (houses, shops, etc.)
        self.dungeons = []  # List of dungeons (caves, etc.)
        self.paths = {}  # Dictionary to hold paths and their descriptions

    def add_item(self, item):
        self.items.append(item)

    def add_dwelling(self, dwelling):
        self.dwellings.append(dwelling)

    def add_dungeon(self, dungeon):
        self.dungeons.append(dungeon)

    def add_path(self, direction, description, destination_coordinates):
        self.paths[direction] = {'description': description, 'destination': destination_coordinates}

class World:
    def __init__(self):
        self.locations = {}  # Dictionary to hold all locations

    def add_location(self, location):
        self.locations[location.coordinates] = location

    def get_location(self, coordinates):
        return self.locations.get(coordinates, None)  # Returns None if location not found

    def move_player(self, current_location, direction):
        # Logic to move the player based on direction (e.g., 'north', 'south')
        pass

# Example usage
if __name__ == '__main__':
    world = World()
    loc1 = Location('Clearing', 'A sunny clearing in the forest.', (0, 0))
    loc1.add_path('north', 'You see a dense forest ahead.', (0, 1))
    loc2 = Location('Rock Outcropping', 'A large rock outcropping that blocks the path.', (1, 0), is_passable=False)
    world.add_location(loc1)
    world.add_location(loc2)
