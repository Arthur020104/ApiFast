import uvicorn
from fastapi import FastAPI, HTTPException
import databases
import sqlalchemy
from datetime import datetime 
from fastapi import HTTPException
from message import Message, MessageUpdate
from user import Usuario, UsuarioUpdate
from conversation import Conversation
#Db tables
""""

USE Historico;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    number_tel VARCHAR(20) NOT NULL
);

CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT
);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    text TEXT,
    is_user BOOLEAN,
    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Add datetime column with default value
    conversation_id INTEGER,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);



"""



DATABASE_URL = "URL"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
users_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id",sqlalchemy.Integer, primary_key=True,autoincrement=True),
    sqlalchemy.Column("name",sqlalchemy.Integer),
    sqlalchemy.Column("number_tel",sqlalchemy.String),
)
messages_table = sqlalchemy.Table(
    "messages",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("is_user", sqlalchemy.Boolean), 
    sqlalchemy.Column("datetime", sqlalchemy.DateTime, default=datetime.utcnow),
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
    update_values = updated_data.model_dump(exclude_unset=True)
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

@app.delete("/delete_conversation/{conversation_id}")
async def delete_conversation(conversation_id: int):
    # Check if the conversation exists
    existing_conversation = await database.fetch_one(
        conversations_table.select().where(conversations_table.c.id == conversation_id)
    )
    
    if not existing_conversation:
        raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")

    # Delete the conversation and its associated messages from the database
    await database.execute(messages_table.delete().where(messages_table.c.conversation_id == conversation_id))
    await database.execute(conversations_table.delete().where(conversations_table.c.id == conversation_id))

    return {"conversation_id": conversation_id, "status": {"code": 200, "text": "Conversation deleted successfully"}}

@app.post("/create_usuario")
async def create_usuario(usuario_data: Usuario):
    query = users_table.insert().values(
        id=usuario_data.id,
        name=usuario_data.name,
        number_tel=usuario_data.number_tel,
    )
    usuario_id = await database.execute(query)
    return {"usuario_id": usuario_id, "status": {"code": 201, "text": "Usuario created successfully"}, **usuario_data.dict()}

@app.get("/get_usuario/{usuario_id}")
async def get_usuario(usuario_id: int):
    usuario = await database.fetch_one(users_table.select().where(users_table.c.id == usuario_id))
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario not found")

    return {"usuario_id": usuario_id, **usuario}

@app.put("/update_usuario/{usuario_id}")
async def update_usuario(usuario_id: int, updated_data: UsuarioUpdate):
    usuario = await database.fetch_one(users_table.select().where(users_table.c.id == usuario_id))
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario not found")

    update_values = updated_data.dict(exclude_unset=True)
    await database.execute(
        users_table.update().where(users_table.c.id == usuario_id).values(**update_values)
    )

    updated_usuario = await database.fetch_one(users_table.select().where(users_table.c.id == usuario_id))
    
    return {"usuario_id": usuario_id, "updated_usuario": updated_usuario, "status": {"code": 200, "text": "Usuario updated successfully"}}


@app.delete("/delete_usuario/{usuario_id}")
async def delete_usuario(usuario_id: int):
    usuario = await database.fetch_one(users_table.select().where(users_table.c.id == usuario_id))
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario not found")

    await database.execute(users_table.delete().where(users_table.c.id == usuario_id))
    
    return {"usuario_id": usuario_id, "status": {"code": 200, "text": "Usuario deleted successfully"}}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
