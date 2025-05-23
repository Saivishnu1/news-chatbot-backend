from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, session
from app.services.gemini import initialize_gemini
from app.db.vector_db import ensure_collection_exists, get_collection_info
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get frontend URLs - support both local and production
FRONTEND_URLS = [
    'http://localhost:5173',                            # Local development
    'http://localhost:10000',                           # Local production
    'https://news-chatbot-frontend.onrender.com',       # Render frontend
    'https://news-chatbot-frontend.onrender.com'        # Render frontend (no trailing slash)
]

# Add custom frontend URL if specified
custom_frontend_url = os.getenv('FRONTEND_URL')
if custom_frontend_url:
    FRONTEND_URLS.append(custom_frontend_url)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_origin_regex=r'https://.*\.onrender\.com',  # Allow all Render subdomains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router, prefix="/api/session", tags=["session"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/ping")
async def ping():
    """Endpoint to check if backend is awake"""
    return {"status": "ok", "message": "Backend is awake"}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("Starting application...")
    
    try:
        # Initialize Gemini model
        initialize_gemini()
        print("Gemini model initialized")
        
        # Ensure Qdrant collection exists
        if not ensure_collection_exists():
            print("Failed to initialize Qdrant collection")
            return
        print("Qdrant collection initialized")
        
        # Check if collection is empty
        collection_info = get_collection_info()
        if collection_info:
            print(f"Collection has {collection_info.get('points_count', 0)} points")
            
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        # Don't raise the error, just log it
        print(f"Application will continue running with limited functionality")



@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "News Chatbot Backend is running"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable for Render deployment
    port = int(os.getenv("PORT", 8000))
    
    # Bind to 0.0.0.0 for Render
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        forwarded_allow_ips='*'      # Trust all forwarding IPs
    )