from pydantic import BaseModel


class ClientJoinPayload(BaseModel):
    """Client to Server on Joining"""
    action: str
    username: str
    admin_flag: bool = False

class ServerJoinPayload(BaseModel):
    """Server to Client on Joining"""
    action: str
    username: str
    user_id: str

class ServerDuplicateClientErrorPayload(BaseModel):
    """Server to Client on Duplicate Error"""
    action: str
    username: str
    message_type: str
    user_id: str