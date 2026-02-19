from pydantic import BaseModel


class ClientJoinPayload(BaseModel):
    """Client to Server"""
    action: str
    username: str
    admin_flag: bool = False

class ServerJoinPayload(BaseModel):
    """Server to Client"""
    action: str
    username: str
    user_id: str