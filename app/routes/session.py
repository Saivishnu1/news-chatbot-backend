import uuid
import redis
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
redis_client = redis.Redis(host="localhost", port=6379, db=0)

class SessionResponse(BaseModel):
    session_id: str

@router.get("/new_session/", response_model=SessionResponse)
def create_session():
    session_id = str(uuid.uuid4())
    redis_client.set(session_id, "[]")  # Empty chat history
    return {"session_id": session_id}