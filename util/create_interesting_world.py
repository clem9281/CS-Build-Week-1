import json
from adventure.models import Player, Room

class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
    def generate_rooms(self, size_x, size_y):
        '''
        Fill up the grid, bottom to top, in a zig-zag pattern
        '''
        # Initialize the grid
        self.grid = [None] * size_y
        self.width = size_x
        self.height = size_y
        for i in range( len(self.grid) ):
            self.grid[i] = [None] * size_x

        with open('./util/data.json', 'r') as json_file:
            data = json.load(json_file)
            keys_list = list(data.keys())
            vals_list = list(data.values())

        # Start from lower-left corner (0,0)
        x = -1 # (this will become 0 on the first step)
        y = 0
        room_count = 0
        num_rooms = len(keys_list)

        # Start generating rooms to the east
        direction = 1  # 1: east, -1: west


        # While there are rooms to be created...
        previous_room = None
        while room_count < num_rooms:

            # Calculate the direction of the room to be created
            if direction > 0 and x < size_x - 1:
                room_direction = "e"
                x += 1
            elif direction < 0 and x > 0:
                room_direction = "w"
                x -= 1
            else:
                # If we hit a wall, turn north and reverse direction
                room_direction = "n"
                y += 1
                direction *= -1

            # Create a room in the given direction
            room = Room(title=keys_list[room_count], description=vals_list[room_count]['description'], items=vals_list[room_count]['items'])
            room.save()
            # Note that in Django, you'll need to save the room after you create it
            # Save the room in the World grid
            self.grid[y][x] = room

            # Connect the new room to the previous room
            if previous_room is not None:
                self.connect_rooms(self, room, previous_room, room_direction)

            # Update iteration variables
            previous_room = room
            room_count += 1
        players=Player.objects.all()
        for p in players:
            p.currentRoom=self.grid[0][0].pk
            p.save()
    def connect_rooms(self, room, connecting_room, direction):
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        reverse_dir = reverse_dirs[direction]
        connecting_room.connectRooms(room, direction)
        connecting_room.save()
        room.connectRooms(connecting_room, reverse_dir)
        room.save()

w = World
width = 10
height = 11
w.generate_rooms(self=w, size_x = width, size_y=height)