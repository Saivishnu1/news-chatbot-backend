import os
import requests
from datetime import datetime
from .embeddings import generate_embeddings
from ..db.vector_db import insert_documents
from dotenv import load_dotenv

load_dotenv()

# Using NewsAPI for more reliable access
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

def fetch_news_articles(limit=50):
    articles = []
    try:
        params = {
            "apiKey": NEWS_API_KEY,
            "language": "en",
            "q": "technology",  # Search term
            "sortBy": "publishedAt",
            "pageSize": limit
        }
        print("Using params:", params)
        
        print("Fetching articles from NewsAPI...")
        response = requests.get(NEWS_API_URL, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Full API response:", data)
            print(f"Total articles from API: {len(data.get('articles', []))}")
            for article in data.get("articles", []):
                if article.get("content") and article.get("title"):
                    articles.append({
                        "title": article["title"],
                        "date": datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
                        "content": article["content"]
                    })
            print(f"Articles with content: {len(articles)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error fetching articles: {str(e)}")
    
    return articles

def scrape_and_store_articles():
    # Fetch articles from BBC News feeds
    articles = fetch_news_articles()
    if not articles:
        print("No articles found")
        return 0
    
    # Extract contents for embedding generation
    contents = [article["content"] for article in articles]
    
    if articles:
        # Generate embeddings for all article contents
        chunks_data = generate_embeddings(contents)
        
        # Create chunked articles for vector storage
        chunked_articles = [{
            "title": articles[chunk["doc_idx"]]["title"],
            "date": articles[chunk["doc_idx"]]["date"],
            "content": chunk["content"],
            "embedding": chunk["embedding"],
            "doc_idx": chunk["doc_idx"],
            "chunk_idx": chunk["chunk_idx"]
        } for chunk in chunks_data]
        
        # Store chunked articles in vector database
        insert_documents(chunked_articles)
        
        return len(chunked_articles)
    return 0
