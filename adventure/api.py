from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json
from django.core import serializers
from django.forms.models import model_to_dict

# instantiate pusher
# PUSHER_APP_ID = config('PUSHER_APP_ID')
# PUSHER_KEY = config('PUSHER_KEY')
# PUSHER_SECRET = config('PUSHER_SECRET')
# PUSHER_CLUSTER = config('PUSHER_CLUSTER')

# pusher = Pusher(app_id=PUSHER_APP_ID, key=PUSHER_KEY, secret=PUSHER_SECRET, cluster=PUSHER_CLUSTER)


"""
What is @csrf_exempt?

Csrf exempt is a feature of django which allows bypassing of csrf verification by django.
By default, django check for csrf token with each POST request, it verifies csrf token before rendering the view. 
Its a very good security practice to verify csrf of post requests as we know django can’t be compromised in case of security.

Source: https://khalsalabs.com/csrf-exempt-in-django/
"""


@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    player_obj = model_to_dict(player)
    player_obj['room'] = model_to_dict(Room.objects.get(id=player.currentRoom))
    player_obj['username'] = user.username
    return JsonResponse(
        {
            "player": player_obj,
            # "uuid": uuid,
            # "name": player.user.username,
            # "title": room.title,
            # "description": room.description,
            "players": players,
            # "inventory": player.inventory,
            # "room_items": room.items,
            "rooms": serializers.serialize("json", Room.objects.all()),
        },
        safe=True,
    )


@csrf_exempt
@api_view(["GET"])
def rooms(request):
    return JsonResponse(serializers.serialize("json", Room.objects.all()), safe=False)


@csrf_exempt
@api_view(["POST"])
def move(request):
    user = request.user
    dirs = {"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data["direction"]
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom = nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        player_obj = model_to_dict(player)
        player_obj['room'] = model_to_dict(Room.objects.get(id=player.currentRoom))
        player_obj['username'] = user.username
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse(
            {
                # "name": player.user.username,
                # "title": nextRoom.title,
                # "description": nextRoom.description,
                "players": players,
                "error_msg": "",
                # "inventory": player.inventory,
                # "room_items": nextRoom.items,
                "player": player_obj
            },
            safe=True,
        )
    else:
        players = room.playerNames(player_id)
        player_obj = model_to_dict(player)
        player_obj['room'] = model_to_dict(Room.objects.get(id=player.currentRoom))
        player_obj['username'] = user.username
        return JsonResponse(
            {
                # "name": player.user.username,
                # "title": room.title,
                # "description": room.description,
                "players": players,
                "player": player_obj,
                # "inventory": player.inventory,
                # "room_items": room.items,
                "error_msg": "You cannot move that way.",
            },
            safe=True,
        )


@csrf_exempt
@api_view(["POST"])
def take_item(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    item = request.data["item"]
    if item in player.inventory:
        return JsonResponse(
            {
                "uuid": uuid,
                "name": player.user.username,
                "title": room.title,
                "description": room.description,
                "inventory": player.inventory,
                "room_items": room.items,
                "message": "You've already got one of those!",
            },
            safe=True,
        )
    if item in room.items:
        room.items.remove(item)
        room.save()
        player.inventory.append(item)
        player.save()
        return JsonResponse(
            {
                "uuid": uuid,
                "name": player.user.username,
                "title": room.title,
                "description": room.description,
                "inventory": player.inventory,
                "room_items": room.items,
                "message": "",
            },
            safe=True,
        )
    return JsonResponse(
        {
            "uuid": uuid,
            "name": player.user.username,
            "title": room.title,
            "description": room.description,
            "inventory": player.inventory,
            "room_items": room.items,
            "message": "Something went wrong picking up that item",
        },
        safe=True,
    )


@csrf_exempt
@api_view(["POST"])
def drop_item(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    item = request.data["item"]
    if item in player.inventory:
        player.inventory.remove(item)
        player.save()
        room.items.append(item)
        room.save()
        return JsonResponse(
            {
                "uuid": uuid,
                "name": player.user.username,
                "title": room.title,
                "description": room.description,
                "inventory": player.inventory,
                "room_items": room.items,
                "message": "",
            },
            safe=True,
        )
    else:
        return JsonResponse(
            {
                "uuid": uuid,
                "name": player.user.username,
                "title": room.title,
                "description": room.description,
                "inventory": player.inventory,
                "room_items": room.items,
                "message": "Something went wrong dropping that item",
            },
            safe=True,
        )


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({"error": "Not yet implemented"}, safe=True, status=500)

