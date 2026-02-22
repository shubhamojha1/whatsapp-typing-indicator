# By default, rooms are private and members are only allowed to join by invitation
# By default, users join general room
# Users can join any public room 
# Admins can create and manage rooms
import uuid
from typing import List
class Room:
    def __init__(self,
                 room_owner: str,
                 room_name: str,
                 admins: List,
                 members: List):
        self.room_id = str(uuid.uuid4())
        self.room_owner = room_owner
        self.room_name = room_name
        self.admins = admins if admins else [room_owner]
        self.members = members if members else [room_owner]
        self.is_public = False
        # self.description 