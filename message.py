from pydantic import BaseModel
from datetime import datetime 
from typing import Optional
class Message(BaseModel):
    text: str
    is_user: bool 
    datetime: datetime
    conversation_id: int

    
class MessageUpdate(BaseModel):
    text: Optional[str]
    is_user: Optional[bool]
    datetime: Optional[datetime]
    conversation_id: Optional[int]