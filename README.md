# News Chatbot Backend

## Overview
A FastAPI-powered backend for an intelligent news chatbot that combines RAG (Retrieval Augmented Generation) with Google's Gemini model. The system provides context-aware responses by retrieving relevant news articles and using them to generate accurate, informative answers.

## Hosted Webservice URLs:-

 Back-End : [news-chatbot-backend.onrender.com](https://news-chatbot-backend.onrender.com/)
 Front-End : [https://news-chatbot-frontend.onrender.com/](https://news-chatbot-frontend.onrender.com/)
 
 **Note**:- The hosted server might be sleeping due to inactivity. It needs 30-60 seconds to start running.

## Features
- 🤖 **AI-Powered Responses**: Uses Google Gemini for natural language understanding and generation
- 🔍 **Smart Search**: Vector-based semantic search using Qdrant for finding relevant news articles
- 📰 **News Context**: Includes relevant news article snippets in responses
- 💾 **Session Management**: Redis-based persistent chat sessions
- 📝 **News Storage**: PostgreSQL database for storing news articles
- 🔒 **Security**: CORS configuration with support for multiple environments
- 📈 **Scalability**: Cloud-based infrastructure using Render, AWS, and managed services

## Tech Stack

### Core Dependencies
```
# Web Framework
fastapi==0.95.1        # Modern web framework
uvicorn==0.22.0        # ASGI server
python-dotenv==1.0.0   # Environment management
requests==2.31.0       # HTTP client

# Database & Caching
psycopg2-binary==2.9.9 # PostgreSQL adapter
redis==5.0.1           # Redis client

# AI & Vector Search
qdrant-client==1.7.0   # Vector database client
google-ai-generative   # Gemini AI SDK
jina==3.15.2           # Embedding generation
```

### Core Framework
- FastAPI (v0.95.1) - Modern, fast web framework
- Uvicorn (v0.22.0) - Lightning-fast ASGI server
- Pydantic - Data validation using Python type annotations

### Vector Search & Embeddings
- Qdrant Cloud (AWS eu-west-1) - Vector similarity search
- JINA AI - Text embedding generation
- Vector size: 1024 dimensions

### Caching & Session Management
- Redis Cloud (AWS ap-south-1)
  - Chat session storage
  - Response caching
  - Rate limiting

### Database
- PostgreSQL (Neon - AWS ap-southeast-1)
  - News articles storage
  - User preferences
  - System configurations
  - Connection pooling enabled

### AI & News Services
- Google Gemini 2.0 Flash - Latest LLM for chat
- NewsAPI - Real-time news data source

### Infrastructure
- Render - Web service hosting
- Neon - Serverless PostgreSQL
- Redis Cloud (AWS ap-south-1) - Managed Redis
- Environment management via python-dotenv
- Comprehensive error handling and logging

## Prerequisites
- Python 3.9+
- Qdrant Cloud account
- Redis Cloud account
- PostgreSQL database (Render provides one)
- Google Gemini API key
- NewsAPI key

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
```env
# AI Service
GEMINI_API_KEY=your_gemini_api_key

# Vector Database (Qdrant Cloud)
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=news_articles
VECTOR_SIZE=1024

# News Service
NEWSAPI_KEY=your_newsapi_key
NEWS_API_URL=https://newsapi.org/v2/top-headlines

# Redis Cloud Configuration (AWS ap-south-1)
REDIS_HOST=redis-xxxxx.xxxx.ap-south-1-1.ec2.redns.redis-cloud.com
REDIS_PORT=xxxxx
REDIS_PASSWORD=your_redis_password

# PostgreSQL Configuration (Neon)
DATABASE_URL=postgresql://user:password@ep-xxxxx-pooler.ap-southeast-1.aws.neon.tech/dbname?sslmode=require
```

## Running the Application

1. Start the development server:
```bash
uvicorn app.main:app --reload
```

2. The API will be available at `http://localhost:8000`
3. API documentation at `http://localhost:8000/docs`

## API Endpoints

### Chat Endpoints
- `POST /api/chat`
  - Process chat messages
  - Parameters:
    - message: User's question or message
    - session_id: Optional chat session ID
  - Returns:
    - answer: AI-generated response
    - news_context: List of relevant news articles

### Session Management
- `POST /api/session/chat_message/{session_id}`
  - Save messages to session history
  - Parameters:
    - role: 'user' or 'assistant'
    - content: Message content

- `GET /api/session/{session_id}`
  - Get chat history for a session
  - Returns array of messages with timestamps

### Health Check
- `GET /`
  - System health check endpoint
  - Returns service status and version

## Project Structure
```
app/
├── config.py        # Configuration management
├── db/              # Database interactions
│   ├── vector_db.py    # Qdrant vector operations
│   ├── redis_cache.py  # Redis caching & sessions
│   └── sql.py         # PostgreSQL operations
├── routes/          # API endpoints
│   ├── chat.py        # Chat message handling
│   └── session.py     # Session management
├── services/        # Core business logic
│   ├── embeddings.py  # Text embedding generation
│   ├── gemini.py      # Gemini model integration
│   ├── ingestion.py   # News data ingestion
│   └── search.py      # Article search logic
└── main.py          # Application entry point
```

## Deployment

This application is configured for deployment on Render:

1. Create a new Web Service in Render
2. Connect your GitHub repository
3. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add all environment variables from `.env`

## Error Handling & Logging

### API Error Handling
- Validation errors for invalid requests
- Proper HTTP status codes
- Detailed error messages in development
- Sanitized errors in production

### Service Error Handling
- AI model timeout and retry logic
- Database connection error recovery
- Rate limiting for external APIs
- Graceful degradation on service failures

### Logging
- Request/response logging
- Error tracking with stack traces
- Performance metrics
- Service health monitoring

## RAG Pipeline Architecture

### 1. Data Ingestion
- **Source**: NewsAPI (newsapi.org)
  - Real-time news articles
  - Filtered for English language
  - Technology focus
  - Sorted by publish date
  - Limit: 50 articles per fetch

### 2. Text Processing
- **Document Structure**:
  ```python
  {
      "title": "Article title",
      "date": "2024-05-12T16:30:00Z",
      "content": "Article content",
  }
  ```
- **Quality Filters**:
  - Non-empty content validation
  - Title presence check
  - Date parsing and validation

### 3. Embedding Generation
- **Service**: Jina AI Embeddings
- **Embedding Types**:
  - Document embeddings (task="retrieval.document")
  - Query embeddings (task="retrieval.query")
- **Vector Size**: 1024 dimensions
- **Chunking**: Automatic document chunking for long articles

### 4. Vector Storage
- **Database**: Qdrant Cloud
- **Collection**: `news_articles`
- **Vector Configuration**:
  - HNSW index for fast similarity search
  - Cosine similarity metric
  - Optimized for 1024d vectors

### 5. Retrieval Process
1. User query → Query embedding
2. Vector similarity search in Qdrant
3. Top-k most relevant articles retrieved
4. Context preparation for Gemini

### 6. Response Generation
- **Model**: Google Gemini 2.0 Flash
- **Input**: 
  - User question
  - Retrieved news context
  - Chat history from Redis
- **Output**: 
  - Natural language response
  - Source article references

### 7. Caching & Storage
- **Redis Cloud**:
  - Session management
  - Response caching
  - Rate limiting
- **PostgreSQL**:
  - Article metadata
  - User interactions
  - System metrics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
## Redis Caching & Session Management

### Architecture

```
User Request → Redis Cache Check → PostgreSQL Fallback → Response
```

### Session Storage

1. **Message Format**:
```json
{
    "role": "user|assistant",
    "content": "message content",
    "timestamp": "ISO datetime"
}
```

2. **Storage Hierarchy**:
   - Primary: Redis (fast access)
   - Secondary: PostgreSQL (persistence)

3. **Session Flow**:
   ```python
   # Writing messages
   POST /api/session/chat_message/{session_id}
   → Save to PostgreSQL
   → Update Redis cache
   
   # Reading messages
   GET /api/session/{session_id}
   → Check Redis first
   → If not in Redis, check PostgreSQL
   → If found in PostgreSQL, update Redis
   ```

### Redis Configuration

1. **Connection**:
   - Host: Redis Cloud (AWS ap-south-1)
   - Port: 17265
   - SSL/TLS: Enabled
   - Database: default
   - Connection timeout: 10s

2. **Cache Settings**:
   - Default TTL: 3600 seconds (1 hour)
   - JSON serialization for complex objects
   - UTF-8 encoding with decode_responses=True
   - Automatic reconnection enabled

3. **Key Structure**:
   ```
   # Chat Sessions
   session:{id}:messages → List of chat messages
   session:{id}:metadata → Session metadata
   
   # Response Cache
   cache:response:{query_hash} → Generated responses
   cache:embedding:{text_hash} → Vector embeddings
   
   # Rate Limiting
   ratelimit:user:{id} → Request counters
   ratelimit:ip:{ip} → IP-based limits
   ```

4. **Data Schemas**:
   ```python
   # Chat Message
   {
       "role": str,        # "user" or "assistant"
       "content": str,     # Message text
       "timestamp": str,   # ISO format
       "metadata": dict    # Optional metadata
   }
   
   # Session Metadata
   {
       "created_at": str,
       "last_active": str,
       "message_count": int,
       "user_id": str
   }
   ```

### Performance Optimizations

1. **Caching Strategy**:
   - Chat history cached on first retrieval
   - Automatic cache updates on new messages
   - Lazy loading for old messages

2. **Data Persistence**:
   - Write-through caching to PostgreSQL
   - Asynchronous cache updates
   - Automatic cache invalidation

3. **Error Handling**:
   - Redis connection retry logic
   - Fallback to PostgreSQL on Redis errors
   - Automatic cache reconstruction

## Code Walkthrough

### 1. End-to-End Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant G as Gemini AI
    participant Q as Qdrant
    participant R as Redis
    participant P as PostgreSQL

    U->>F: Enter question
    F->>B: POST /api/chat
    B->>Q: Search similar articles
    Q-->>B: Return relevant articles
    B->>G: Generate response
    G-->>B: Return answer
    B->>R: Cache response
    B->>P: Store in history
    B-->>F: Return response
    F-->>U: Display answer
```

### 2. Frontend Implementation

```typescript
// ChatContainer.tsx
const handleSendMessage = async (message: string) => {
  setIsTyping(true);
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message,
        session_id: sessionId 
      })
    });
    const data = await response.json();
    updateMessages(data.answer, data.news_context);
  } catch (error) {
    handleError(error);
  }
  setIsTyping(false);
};
```

### 3. Backend Pipeline

1. **Chat Request Processing**:
```python
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Search relevant articles
    articles = await search_articles(request.message, top_k=5)
    
    # 2. Generate AI response
    answer = generate_final_answer(request.message, articles)
    
    # 3. Save to session history
    save_chat_message(request.session_id, "user", request.message)
    save_chat_message(request.session_id, "assistant", answer)
```

2. **Vector Search Process**:
```python
# 1. Generate query embedding
query_vector = generate_query_embedding(query)

# 2. Search in Qdrant
results = client.search(
    collection_name=COLLECTION_NAME,
    query_vector=query_vector,
    limit=top_k
)

# 3. Format and return matches
return [format_article(match) for match in results]
```

3. **Session Management**:
```python
# Redis-first with PostgreSQL fallback
def get_chat_history(session_id: str):
    # Try Redis first
    messages = get_messages_from_redis(session_id)
    if messages:
        return messages
        
    # Fallback to PostgreSQL
    messages = get_messages_from_db(session_id)
    if messages:
        # Update Redis cache
        set_messages_in_redis(session_id, messages)
    return messages
```

### 4. Key Design Decisions

1. **Hybrid Storage Strategy**
   - Redis for fast access to recent sessions
   - PostgreSQL for permanent storage
   - Automatic sync between both

2. **Vector Search Optimization**
   - HNSW index for fast similarity search
   - Batch processing for embeddings
   - Caching frequent queries

3. **Error Handling**
   - Graceful degradation
   - Automatic retries
   - Fallback responses

### 5. Potential Improvements

1. **Performance**
   - Implement websockets for real-time updates
   - Add query result caching
   - Optimize embedding generation

2. **Features**
   - Multi-language support
   - User preferences
   - Source filtering

3. **Infrastructure**
   - Load balancing
   - Rate limiting
   - Analytics tracking

## Testing
```bash
pytest tests/
```

