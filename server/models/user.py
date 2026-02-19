import uuid
from enum import Enum
from typing import Set, Optional, Dict, Any

class UserStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    # MODERATOR = "moderator"

class User:
    def __init__(self, 
    username: str, 
    websocket, 
    user_role: UserRole = UserRole.USER, 
    status: UserStatus = UserStatus.ONLINE,
    # bio: str = "", 
    # avatar: Optional[str] = None
    ):
        self.user_id = str(uuid.uuid4())
        self.username = username
        self.user_role = user_role
        self.status = status
        # self.bio = bio
        # self.avatar = avatar
        self.friends: Set[str] = set()
        self.blocked: Set[str] = set()
        # self.created_at = datetime.utcnow()
        # self.last_seen = datetime.utcnow()
        self.is_online = True
        # self.current_room: Optional[str] = None
        # self.unread_messages: List[Message] = []
        self.websocket = websocket
        self.settings: Dict[str, Any] = {
            "notifications": True,
            "theme": "dark",
            "privacy": "everyone",
            "dnd_mode": False
        }