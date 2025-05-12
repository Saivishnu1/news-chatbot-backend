from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat, session
from .services.gemini import initialize_gemini
from .db.vector_db import ensure_collection_exists, get_collection_info
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get frontend URL from environment variable, default to localhost for development
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router, prefix="/api/session", tags=["session"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("Starting application...")
    
    try:
        # Initialize Gemini model
        initialize_gemini()
        print("Gemini model initialized")
        
        # Ensure Qdrant collection exists
        ensure_collection_exists()
        print("Qdrant collection initialized")
        
        # Check if collection is empty
        collection_info = get_collection_info()
        if collection_info:
            print(f"Collection has {collection_info.get('points_count', 0)} points")
            
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise e



@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "News Chatbot Backend is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)