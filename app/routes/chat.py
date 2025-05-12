from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from ..services.search import search_articles
from ..services.gemini import generate_final_answer
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    news_context: List[Dict] = []

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat messages and generate AI-powered responses with news context
    """
    try:
        print(f"\nReceived chat request: {request.message}")
        
        # Search for relevant articles asynchronously
        articles = await search_articles(request.message, top_k=5)
        print(f"Found {len(articles)} relevant articles")
        
        if not articles:
            print("No relevant articles found")
            return ChatResponse(
                answer="I couldn't find any relevant news articles to answer your question.",
                news_context=[]
            )
        
        # Generate answer using Gemini
        answer = generate_final_answer(request.message, articles)
        if not answer:
            print("No answer generated")
            return ChatResponse(
                answer="I apologize, but I couldn't generate a response based on the available information.",
                news_context=[]
            )
        
        # Format news context for response
        news_context = []
        for article in articles:
            try:
                news_context.append({
                    "title": str(article.get("title", "No title")),
                    "content": str(article.get("content", "No content")),
                    "url": str(article.get("url", "")),
                    "relevance_score": float(article.get("score", 0.0))
                })
            except Exception as e:
                print(f"Error formatting article: {str(e)}")
                continue
        
        return ChatResponse(
            answer=answer,
            news_context=news_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))