import os
from dotenv import load_dotenv

load_dotenv()

# Print environment variables for debugging
print("\nEnvironment variables:")

# Qdrant Vector Database Configuration
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'news_articles')
VECTOR_SIZE = int(os.getenv('VECTOR_SIZE', '1024'))  # Using 1024-dimensional vectors for jina-embeddings-v3

print(f"QDRANT_URL: {'Set' if QDRANT_URL else 'Not set'}")
print(f"QDRANT_API_KEY: {'Set' if QDRANT_API_KEY else 'Not set'}")
print(f"COLLECTION_NAME: {COLLECTION_NAME}")
print(f"VECTOR_SIZE: {VECTOR_SIZE}")

# Jina AI Configuration
JINA_API_KEY = os.getenv('JINA_API_KEY')
print(f"JINA_API_KEY: {'Set' if JINA_API_KEY else 'Not set'}")

# Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
print(f"GEMINI_API_KEY: {'Set' if GEMINI_API_KEY else 'Not set'}")
print(f"GEMINI_MODEL: {GEMINI_MODEL}")

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# Validate required environment variables
required_vars = {
    'QDRANT_URL': QDRANT_URL,
    'QDRANT_API_KEY': QDRANT_API_KEY,
    'JINA_API_KEY': JINA_API_KEY,
    'GEMINI_API_KEY': GEMINI_API_KEY
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
