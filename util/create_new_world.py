import json
from adventure.models import Player, Room
import random
import math


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def __str__(self):
        arr = []
        current = self.head
        while current:
            arr.append(current.value["title"])
            current = current.next
        return f"{arr}"

    def __len__(self):
        return self.size

    def enqueue(self, value):
        new_node = Node(value)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def dequeue(self):
        if not self.head:
            return None
        else:
            val = self.head.value
            self.head = self.head.next
            self.size -= 1
            return val


# Get neighbors is mutating visited, incrementing count (which needs to be returned, it's not a reference type) and returning an array of the neighbors of the room we are looking at
def get_neighbors(
    current, visited, count, num_rooms, keys_list, vals_list, random_grid_size,
):
    holder = [None] * 4
    i = 0
    directions = ["n_to", "s_to", "e_to", "w_to"]
    opposites = {"n_to": "s_to", "s_to": "n_to", "e_to": "w_to", "w_to": "e_to"}
    for direction in directions:
        # look through our available directions, if this room has that direction available, look to see if there is a room already in that position. If so link these two up, if not create a new room.
        if getattr(current, direction) is 0:
            look_y = None
            look_x = None
            # For each check we have to see if we stil even have anymore rooms to create, and we have to check the bounds. For example, if the current y is already 0, we cannot place a room north of that!
            if direction == "n_to" and count < num_rooms and current.y > 0:
                look_x = current.x
                look_y = current.y - 1
            if (
                direction == "e_to"
                and count < num_rooms
                and current.x < random_grid_size
            ):
                look_x = current.x + 1
                look_y = current.y
            if (
                direction == "s_to"
                and count < num_rooms
                and current.y < random_grid_size
            ):
                look_x = current.x
                look_y = current.y + 1
            if direction == "w_to" and count < num_rooms and current.x > 0:
                look_x = current.x - 1
                look_y = current.y
            # If look_y or look_x is still None, we don't want to put at room in this direction, continue the loop and start at the next direction
            if not look_y or not look_x:
                continue
            # If there is a room in that direction link these two
            if visited[look_y][look_x] is not None:
                another_room = visited[look_y][look_x]
                current.connectRooms(another_room, direction)
                another_room.connectRooms(current, opposites[direction])
            # otherwise create a new room, increment count, link the two rooms
            else:
                another_room = Room(
                    title=keys_list[count],
                    description=vals_list[count]["description"],
                    x=look_x,
                    y=look_y,
                    items=vals_list[count]["items"],
                )
                another_room.save()
                count += 1
                current.connectRooms(another_room, direction)
                another_room.connectRooms(current, opposites[direction])
                visited[look_y][look_x] = another_room
            # add the linked room to the holder, holder holds all our neighbors, and will be added to the queue
            holder[i] = another_room
            i += 1
    return [holder, count]


def generate_rooms(num_rooms=100):
    # delete existing rooms and start fresh
    Room.objects.all().delete()
    # get data from json file
    with open("./util/shuffled.json", "r") as json_file:
        data = json.load(json_file)
        keys_list = list(data.keys())
        vals_list = list(data.values())

    # rooms array holds the rooms that will be output to the json file and count keeps track of created rooms. We'll use the queue to keep track of rooms that might still need neighbors
    # rooms = []
    count = 0
    q = Queue()
    # I wanted a square area to start with, but if it one side is the square of the number of the rooms, we'll end up with a boring square grid.
    random_grid_size = math.floor(math.sqrt(num_rooms) * 1.5)
    # Get our visited array ready. The visited array exists to help with room collisions. If I want to put a room north of the room I am looking at, how can I tell if there is already a room there? Visited keeps track of that.
    visited = [
        [None for i in range(random_grid_size + 1)] for j in range(random_grid_size + 1)
    ]
    # random start position of first room
    random_start_x = random.randint(0, random_grid_size)
    random_start_y = random.randint(0, random_grid_size)
    # create first room, increment count
    new_room = Room(
        title=keys_list[count],
        description=vals_list[count]["description"],
        items=vals_list[count]["items"],
        x=random_start_x,
        y=random_start_y,
    )
    new_room.save()
    count += 1
    # add the new room to the queue to be evaluated
    q.enqueue(new_room)
    visited[random_start_y][random_start_x] = new_room

    while count < num_rooms:
        current = q.dequeue()
        holder, count = get_neighbors(
            current, visited, count, num_rooms, keys_list, vals_list, random_grid_size,
        )
        # shuffle our neighbors for more variance
        random.shuffle(holder)
        for item in holder:
            if item is not None:
                q.enqueue(item)


rooms = generate_rooms(100)
print(f"Generated Rooms")
