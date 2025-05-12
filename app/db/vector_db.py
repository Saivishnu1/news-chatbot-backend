from qdrant_client import QdrantClient
from qdrant_client.http import models
from .. import config
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Qdrant client
client = QdrantClient(
    url=config.QDRANT_URL,
    api_key=config.QDRANT_API_KEY,
    timeout=10.0  # Increase timeout
)

def get_collection_info():
    """Get information about the Qdrant collection"""
    try:
        collection_info = client.get_collection(config.COLLECTION_NAME)
        points_count = collection_info.points_count
        vector_size = collection_info.config.params.vectors.size
        print(f"\nCollection details:")
        print(f"Name: {config.COLLECTION_NAME}")
        print(f"Points count: {points_count}")
        print(f"Vector size: {vector_size}")
        print(f"Expected vector size: {config.VECTOR_SIZE}")
        
        # Get sample points to inspect structure
        if points_count > 0:
            sample = client.scroll(
                collection_name=config.COLLECTION_NAME,
                limit=1,
                with_payload=True,
                with_vectors=True
            )[0]
            
            if sample:
                print("\nSample point structure:")
                point = sample[0]
                print(f"Vector size in sample: {len(point.vector)}")
                print(f"Payload keys: {list(point.payload.keys())}")
                print(f"Sample title: {point.payload.get('title', 'No title')}")
                print(f"Sample content length: {len(point.payload.get('content', ''))} chars")
        
        return {
            'name': config.COLLECTION_NAME,
            'vector_size': vector_size,
            'points_count': points_count
        }
    except Exception as e:
        print(f"Error getting collection info: {str(e)}")
        return None

def ensure_collection_exists():
    try:
        # Check if collection exists
        collection_info = client.get_collection(config.COLLECTION_NAME)
        print(f"Collection info: {collection_info}")
        
        # Verify vector size matches
        if collection_info.config.params.vectors.size != config.VECTOR_SIZE:
            print(f"\nVector size mismatch detected:")
            print(f"Collection vector size: {collection_info.config.params.vectors.size}")
            print(f"Expected vector size: {config.VECTOR_SIZE}")
            print("Recreating collection with correct vector size...")
            
            # Delete existing collection
            client.delete_collection(config.COLLECTION_NAME)
            print(f"Deleted collection {config.COLLECTION_NAME}")
            
            # Create new collection
            client.create_collection(
                collection_name=config.COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=config.VECTOR_SIZE,
                    distance=models.Distance.COSINE
                )
            )
            print(f"Created new collection {config.COLLECTION_NAME} with vector size {config.VECTOR_SIZE}")
            
        return True
    except Exception as e:
        print(f"Creating new collection {config.COLLECTION_NAME}: {str(e)}")
        client.create_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=config.VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )
        return True

def insert_documents(documents):
    # Ensure collection exists before insertion
    ensure_collection_exists()
    
    # Create points from documents
    points = []
    for doc in documents:
        # Create a unique ID that combines document and chunk indices
        point_id = doc["doc_idx"] * 10000 + doc["chunk_idx"]
        
        # Create point for each document
        point = models.PointStruct(
            id=point_id,
            vector=doc["embedding"],
            payload={
                "doc_idx": doc["doc_idx"],
                "chunk_idx": doc["chunk_idx"],
                "title": doc["title"],
                "date": doc["date"],
                "content": doc["content"],
                "url": doc.get("url", "")
            }
        )
        points.append(point)
    
    # Batch insert all points
    if points:
        print(f"Inserting {len(points)} points into Qdrant")
        client.upsert(collection_name=config.COLLECTION_NAME, points=points)

def search_documents(query_vector, top_k=15):
    """Search for similar documents in Qdrant collection."""
    try:
        # Get collection info
        collection_info = client.get_collection(config.COLLECTION_NAME)
        print(f"Collection info: {collection_info}")
        
        # Verify vector size
        if len(query_vector) != collection_info.config.params.vectors.size:
            print(f"Query vector size mismatch: expected {collection_info.config.params.vectors.size}, got {len(query_vector)}")
            return {
                "result": {"points": []},
                "status": "vector_size_mismatch",
                "time": 0
            }
        
        # Check if collection has points
        count = client.count(config.COLLECTION_NAME)
        if count.count == 0:
            print("Collection exists but has no points")
            return {
                "result": {"points": []},
                "status": "empty_collection",
                "time": 0
            }
            
        print(f"Searching in collection with {count.count} points")
        
        # Perform vector search
        search_response = client.search(
            collection_name=config.COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )
        
        if not search_response:
            print("No results found")
            return {
                "result": {"points": []},
                "status": "no_results",
                "time": 0
            }
        
        # Convert search results to expected format
        points = []
        for hit in search_response:
            try:
                points.append({
                    "id": str(hit.id),
                    "score": float(hit.score),
                    "payload": dict(hit.payload)
                })
            except Exception as e:
                print(f"Error converting hit: {str(e)}")
        
        print(f"Found {len(points)} matching documents")
        return {
            "result": {"points": points},
            "status": "ok",
            "time": 0
        }
        
    except Exception as e:
        print(f"Error in search_documents: {str(e)}")
        return {
            "result": {"points": []},
            "status": "error",
            "time": 0
        }
