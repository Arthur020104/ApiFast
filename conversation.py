from pydantic import BaseModel
from typing import List
from message import Message

class Conversation(BaseModel):
    user_id: int
    messages: List[Message] = []