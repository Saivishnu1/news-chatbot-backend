import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

JINA_API_KEY = os.getenv('JINA_API_KEY')


def generate_embeddings(texts, task="retrieval.document"):
    """Generate embeddings for documents. Uses document task type for better chunking."""
    return _generate_embeddings(texts, task)

def generate_query_embedding(query):
    """Generate embedding for a search query. Uses query task type for better matching."""
    print(f"Generating embedding for query: {query}")
    try:
        results = _generate_embeddings([query], task="retrieval.query")
        if not results:
            print("No results from _generate_embeddings")
            return None
        
        # Check if results is a list and has at least one element.
        if not isinstance(results, list) or not results:
            print(f"Invalid result format: {results}")
            return None

        if not isinstance(results[0], dict) or 'embedding' not in results[0]:
            print(f"Invalid result format: {results[0]}")
            return None
        
        embedding = results[0]['embedding']
        if not isinstance(embedding, list):
            print(f"Invalid embedding type: {type(embedding)}")
            return None
        
        print(f"Successfully generated query embedding with size {len(embedding)}")
        return embedding
    except Exception as e:
        print(f"Error in generate_query_embedding: {str(e)}")
        return None

def _generate_embeddings(texts, task):
    """
    Generate embeddings for a list of texts using the Jina AI API.

    Args:
        texts (list): A list of strings or dictionaries (with "content" key) representing the texts to embed.
        task (str): The task type ("retrieval.document" or "retrieval.query").

    Returns:
        list: A list of dictionaries, where each dictionary contains the embedding and related information.
              Returns an empty list in case of errors or no texts.
              Each dictionary has the following structure:
              {
                  "embedding": list,  # The embedding vector (list of floats)
                  "doc_idx": int,      # Index of the original document
                  "chunk_idx": int,    # Index of the chunk within the document (always 0 for queries)
                  "title": str,        # Title of the document (if available)
                  "date": str,         # Date of the document (if available)
                  "content": str,      # Content of the chunk
                  "url": str           # URL of the document (if available)
              }
    """
    if not texts:
        print("No texts provided for embedding generation")
        return []
    
    print(f"Processing {len(texts)} documents for embedding generation")
    
    if not JINA_API_KEY:
        print("Error: JINA_API_KEY not found in environment variables")
        print("Available environment variables:")
        # Attempt to print the key, but mask it for security
        masked_key = '*' * len(JINA_API_KEY) if hasattr(JINA_API_KEY, 'JINA_API_KEY') and JINA_API_KEY else 'Not set'
        print(f"JINA_API_KEY: {masked_key}")
        return []

    url = "https://api.jina.ai/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}"
    }
    
    try:
        # For queries, just process a single text
        if task == "retrieval.query":
            try:
                print(f"Generating embedding for query: {texts[0][:100]}...")
                data = {
                    "model": "jina-embeddings-v3",
                    "task": task,
                    "late_chunking": True,
                    "truncate": True,
                    "input": texts
                }
                
                print("Making request to Jina API...")
                response = requests.post(url, headers=headers, json=data)
                print(f"Jina API response status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"Error response from Jina API: {response.text}")
                    return []
                
                response.raise_for_status()
                result = response.json()
                
                if not result.get('data'):
                    print("No embeddings data in response")
                    print(f"Response content: {result}")
                    return []
                
                embedding = result['data'][0]['embedding']
                print(f"Successfully generated embedding with size {len(embedding)}")
                
                return [{
                    "embedding": embedding,
                    "doc_idx": 0,
                    "chunk_idx": 0
                }]
            except Exception as e:
                print(f"Error generating query embedding: {str(e)}")
                return []
        
        # For documents, process in batches
        batch_size = 20  # Process 20 texts at a time for better performance
        chunks_data = []
        
        try:
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                # Convert texts to list of strings if they're dictionaries
                batch_contents = [text["content"] if isinstance(text, dict) else text for text in batch_texts]
                
                data = {
                    "model": "jina-embeddings-v3",
                    "task": "retrieval.document", # Changed to retrieval.document
                    "late_chunking": True,
                    "truncate": True,
                    "input": batch_contents
                }
                
                print(f"Processing batch {i//batch_size + 1} of {(len(texts)-1)//batch_size + 1}")
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code != 200:
                    print(f"Error response from Jina API: {response.text}")
                    continue  # Continue to the next batch
                
                response.raise_for_status()
                result = response.json()
                
                if not result.get('data'):
                    print("No embeddings data in response")
                    continue  # Continue to the next batch
                
                # Process each document's embedding
                for j, embedding_data in enumerate(result['data']):
                    doc_idx = i + j
                    original_text = batch_texts[j]
                    metadata = original_text if isinstance(original_text, dict) else {}
                    
                    embedding = embedding_data.get('embedding')
                    if not isinstance(embedding, list):
                        print(f"Warning: Invalid embedding format for document {doc_idx}")
                        continue
                    
                    # Check the embedding size
                    if 'VECTOR_SIZE' in dir(config) and len(embedding) != config.VECTOR_SIZE:
                        print(f"Warning: Incorrect embedding size {len(embedding)} for document {doc_idx}. Expected {config.VECTOR_SIZE if 'VECTOR_SIZE' in dir(config) else 'Unknown'}")
                        continue
                    
                    chunks_data.append({
                        "embedding": embedding,
                        "doc_idx": doc_idx,
                        "chunk_idx": j,
                        "title": metadata.get("title", ""),
                        "date": metadata.get("date", ""),
                        "content": metadata.get("content", batch_contents[j]),
                        "url": metadata.get("url", "")
                    })
            
            print(f"Generated {len(chunks_data)} valid embeddings")
            return chunks_data
        except Exception as e:
            print(f"Error in batch processing: {str(e)}")
            return []
            
    except Exception as e:
        print(f"Error in _generate_embeddings: {str(e)}")
        return []