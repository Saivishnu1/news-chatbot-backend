import os
import psycopg2
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Use environment variable for database connection
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create chat_history table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id SERIAL PRIMARY KEY,
        session_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def save_chat_message(session_id: str, role: str, content: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "INSERT INTO chat_history (session_id, role, content) VALUES (%s, %s, %s)"
    cursor.execute(query, (session_id, role, content))
    
    conn.commit()
    cursor.close()
    conn.close()

def get_chat_history(session_id: str, limit: int = 50) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT role, content, timestamp 
    FROM chat_history 
    WHERE session_id = %s 
    ORDER BY timestamp DESC 
    LIMIT %s
    """
    cursor.execute(query, (session_id, limit))
    
    messages = [{
        "role": row[0],
        "content": row[1],
        "timestamp": row[2].isoformat()
    } for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return messages[::-1]  # Reverse to get chronological order

def delete_chat_history(session_id: str) -> None:
    """Delete all chat history for a given session ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "DELETE FROM chat_history WHERE session_id = %s"
    cursor.execute(query, (session_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
