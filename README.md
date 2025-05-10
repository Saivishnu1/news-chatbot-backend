# News Chatbot Backend

## Overview
This is a sophisticated backend for a news chatbot that leverages AI to provide intelligent news interactions.

## Features
- News scraping from multiple sources
- Semantic search using vector embeddings
- Redis-based caching
- PostgreSQL news storage
- FastAPI-powered RESTful endpoints

## Prerequisites
- Python 3.9+
- Redis server
- PostgreSQL database

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/news-chatbot-backend.git
cd news-chatbot-backend
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
Create a `.env` file with:
```
DATABASE_URL=postgresql://username:password@localhost/newschatbot
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

## Services

### Ingestion
- Scrapes news from multiple sources
- Supports Hacker News, Reuters, BBC

### Embeddings
- Converts text to semantic vector representations
- Uses sentence-transformers for high-quality embeddings

### Search
- Semantic search across news articles
- Ranks articles by relevance

## Testing
```bash
pytest tests/
```

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License
