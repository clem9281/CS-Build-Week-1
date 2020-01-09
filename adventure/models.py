from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.postgres.fields import ArrayField

import uuid


class Room(models.Model):
    title = models.CharField(max_length=50, default="DEFAULT TITLE")
    description = models.CharField(max_length=500, default="DEFAULT DESCRIPTION")
    n_to = models.IntegerField(default=0)
    s_to = models.IntegerField(default=0)
    e_to = models.IntegerField(default=0)
    w_to = models.IntegerField(default=0)
    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)
    items = ArrayField(models.CharField(max_length=200, blank=True), default=list)

    def connectRooms(self, destinationRoom, direction):
        destinationRoomID = destinationRoom.id
        try:
            destinationRoom = Room.objects.get(id=destinationRoomID)
        except Room.DoesNotExist:
            print("That room does not exist")
        else:
            if direction == "n_to":
                self.n_to = destinationRoomID
            elif direction == "s_to":
                self.s_to = destinationRoomID
            elif direction == "e_to":
                self.e_to = destinationRoomID
            elif direction == "w_to":
                self.w_to = destinationRoomID
            else:
                print("Invalid direction")
                return
            self.save()

    def playerNames(self, currentPlayerID):
        return [
            p.user.username
            for p in Player.objects.filter(currentRoom=self.id)
            if p.id != int(currentPlayerID)
        ]

    def playerUUIDs(self, currentPlayerID):
        return [
            p.uuid
            for p in Player.objects.filter(currentRoom=self.id)
            if p.id != int(currentPlayerID)
        ]


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currentRoom = models.IntegerField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    inventory = ArrayField(models.CharField(max_length=200, blank=True), default=list)

    def initialize(self):
        if self.currentRoom == 0:
            self.currentRoom = Room.objects.first().id
            self.save()

    def room(self):
        print(Room.objects.first())
        try:
            return Room.objects.get(id=self.currentRoom)
        except Room.DoesNotExist:
            self.currentRoom = Room.objects.first().id
            return self.room()


@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()

