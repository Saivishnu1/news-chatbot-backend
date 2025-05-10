from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from app.services.search import NewsSearchEngine
from app.db.redis import RedisCache

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    news_context: List[Dict] = []

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat messages and generate AI-powered responses with news context
    """
    try:
        # Initialize services
        search_engine = NewsSearchEngine()
        redis_cache = RedisCache()

        # Search relevant news articles
        news_results = search_engine.search_articles(request.query, top_k=3)
        
        # Generate context-aware response
        #response_text = generate_response(request.query, news_results)
        response_text = generate_response(request.query, news_results)
        
        # Cache chat history
        redis_cache.store_chat_history(
            request.session_id, 
            [{
                "query": request.query, 
                "response": response_text,
                "news_context": news_results
            }]
        )
        
        return ChatResponse(
            answer=response_text, 
            news_context=news_results
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_response(query: str, news_context: List[Dict]) -> str:
    """Generate an intelligent response using query and news context"""
    # Simple implementation for now
    if not news_context:
        return "I couldn't find any relevant news for your query."
    
    # Simple response generation logic
    response_templates = [
        "Based on recent news, ",
        "Considering the latest developments, ",
        "Here's what I found: "
    ]
    
    # Select a random response template
    template = response_templates[hash(query) % len(response_templates)]
    
    # Compile news titles
    news_titles = [article.get('title', '') for article in news_context]
    context_summary = " | ".join(news_titles)
    
    return f"{template}{context_summary}"