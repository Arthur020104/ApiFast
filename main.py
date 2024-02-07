from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import databases
import sqlalchemy
from datetime import datetime 
from typing import Optional
from fastapi import HTTPException



class Message(BaseModel):
    text: str
    is_user: bool 
    datetime: datetime
    conversation_id: int

class Conversation(BaseModel):
    user_id: int
    messages: List[Message] = []
    
class MessageUpdate(BaseModel):
    text: Optional[str]
    is_user: Optional[bool]
    datetime: Optional[datetime]
    conversation_id: Optional[int]


DATABASE_URL = "mysql+mysqlconnector://Arthur:pass@localhost/Historico"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
messages_table = sqlalchemy.Table(
    "messages",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("is_user", sqlalchemy.Boolean),  # Change to Boolean for better representation
    sqlalchemy.Column("datetime", sqlalchemy.DateTime, default=datetime.utcnow),  # Add datetime column
    sqlalchemy.Column("conversation_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("conversations.id")),
)

conversations_table = sqlalchemy.Table(
    "conversations",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer),
)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

# Define a shutdown event to close the database connection
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    
@app.post("/create_message")
async def create_message(message_data: Message):
    query = messages_table.insert().values(
        text=message_data.text,
        is_user=message_data.is_user,
        datetime=message_data.datetime,
        conversation_id=message_data.conversation_id,
    )
    message_id = await database.execute(query)
    return {"message_id": message_id, "status": {"code": 201, "text": "Message created successfully"}, **message_data.model_dump()}

@app.get("/get_message/{message_id}")
async def get_message(message_id: int):
    # Fetch the message from the database by its ID
    message = await database.fetch_one(messages_table.select().where(messages_table.c.id == message_id))

    # If the message does not exist, raise an HTTPException
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return {"message_id": message_id, "message_content": message["text"], "status": {"code": 200, "text": "Message retrieved successfully"}}

@app.post("/add_message_to_conversation/{conversation_id}")
async def add_message_to_conversation(conversation_id: int, message_data: Message):
    # Check if the conversation exists
    conversation_query = conversations_table.select().where(conversations_table.c.id == conversation_id)
    existing_conversation = await database.fetch_one(conversation_query)

    if not existing_conversation:
        raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")

    # If the conversation exists, insert the message
    query = messages_table.insert().values(
        text=message_data.text,
        is_user=message_data.is_user,
        datetime=message_data.datetime,
        conversation_id=conversation_id,
    )
    message_id = await database.execute(query)

    return {"message_id": message_id, "status": {"code": 201, "text": "Message added to conversation successfully"}, **message_data.model_dump()}


@app.put("/update_message/{message_id}")
async def update_message(message_id: int, updated_data: MessageUpdate):
    # Fetch the message from the database by its ID
    message = await database.fetch_one(messages_table.select().where(messages_table.c.id == message_id))

    # If the message does not exist, raise an HTTPException
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Update the message with the provided data
    update_values = updated_data.dict(exclude_unset=True)
    await database.execute(
        messages_table.update().where(messages_table.c.id == message_id).values(**update_values)
    )

    # Fetch the updated message from the database
    updated_message = await database.fetch_one(messages_table.select().where(messages_table.c.id == message_id))

    return {"message_id": message_id, "updated_message": updated_message, "status": {"code": 200, "text": "Message updated successfully"}}

@app.delete("/delete_message/{message_id}")
async def delete_message(message_id: int):
    # Check if the message exists
    existing_message = await database.fetch_one(messages_table.select().where(messages_table.c.id == message_id))
    if not existing_message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Delete the message from the database
    await database.execute(messages_table.delete().where(messages_table.c.id == message_id))

    return {"message_id": message_id, "status": {"code": 200, "text": "Message deleted successfully"}}


@app.post("/create_conversation")
async def create_conversation(conversation_data: Conversation):
    query = conversations_table.insert().values(user_id=conversation_data.user_id)
    conversation_id = await database.execute(query)

    return {"conversation_id": conversation_id, "messages": [], "status": {"code": 201, "text": "Conversation created successfully"}}



if __name__ == "__main__":
    import uvicorn

    # Use uvicorn to run the FastAPI app
    uvicorn.run(app, host="127.0.0.1", port=8000)
