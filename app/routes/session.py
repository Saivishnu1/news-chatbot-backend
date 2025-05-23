import uuid
import json
import redis
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..db.sql import get_chat_history, save_chat_message, delete_chat_history

router = APIRouter()
from dotenv import load_dotenv
import os

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis-17265.c212.ap-south-1-1.ec2.redns.redis-cloud.com'),
    port=int(os.getenv('REDIS_PORT', '17265')),
    db=os.getenv('REDIS_DB', 'default'),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

class Message(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[Message]

class SessionResponse(BaseModel):
    session_id: str

def get_messages_from_redis(session_id: str) -> List[dict]:
    try:
        messages_str = redis_client.get(f'chat:{session_id}')
        if messages_str:
            # No need to decode since decode_responses=True
            return json.loads(messages_str)
        return []
    except Exception as e:
        print(f"Redis error: {e}")
        return []

def set_messages_in_redis(session_id: str, messages: List[dict], expire_time: int = 3600) -> None:
    try:
        # Convert messages to a format that can be serialized
        serializable_messages = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in messages
        ]
        redis_client.setex(
            f'chat:{session_id}',
            expire_time,
            json.dumps(serializable_messages)
        )
    except Exception as e:
        print(f"Redis error: {e}")

@router.get("/new_session/", response_model=SessionResponse)
def create_session():
    session_id = str(uuid.uuid4())
    set_messages_in_redis(session_id, [])  # Empty chat history
    return {"session_id": session_id}

@router.get("/chat_history/{session_id}", response_model=ChatHistory)
def get_session_history(session_id: str):
    try:
        # Always get from PostgreSQL first for consistency
        db_messages = get_chat_history(session_id)
        if db_messages:
            # Format messages
            messages = [{
                "role": msg["role"],
                "content": msg["content"]
            } for msg in db_messages]
            # Update Redis cache
            set_messages_in_redis(session_id, messages)
            return {"messages": messages}
        
        # If no messages in PostgreSQL, try Redis as fallback
        messages = get_messages_from_redis(session_id)
        if messages:
            # If found in Redis, persist to PostgreSQL
            for msg in messages:
                save_chat_message(session_id, msg["role"], msg["content"])
            return {"messages": messages}
        
        # No messages found anywhere
        return {"messages": []}
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return {"messages": []}

@router.post("/chat_message/{session_id}")
def save_message(session_id: str, message: Message):
    # Save to PostgreSQL for persistence
    save_chat_message(session_id, message.role, message.content)
    
    # Update Redis for fast access
    messages = get_messages_from_redis(session_id)
    messages.append({
        "role": message.role,
        "content": message.content
    })
    set_messages_in_redis(session_id, messages)
    
    return {"status": "success"}

@router.post("/reset/{session_id}")
def reset_chat(session_id: str):
    try:
        # Delete from PostgreSQL
        delete_chat_history(session_id)
        
        # Delete from Redis
        redis_client.delete(f'chat:{session_id}')
        
        return {"status": "success", "message": "Chat history cleared"}
    except Exception as e:
        print(f"Error resetting chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset chat history")