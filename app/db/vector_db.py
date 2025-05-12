from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Qdrant client

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME')
VECTOR_SIZE = int(os.getenv('VECTOR_SIZE'))

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=20.0  # Increase timeout further
)

def get_collection_info():
    """Get information about the Qdrant collection"""
    try:
        collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
        points_count = collection_info.points_count
        vector_size = collection_info.config.params.vectors.size
        print(f"\nCollection details:")
        print(f"Name: {QDRANT_COLLECTION_NAME}")
        print(f"Points count: {points_count}")
        print(f"Vector size: {vector_size}")
        print(f"Expected vector size: {VECTOR_SIZE}")
        
        # Get sample points to inspect structure
        if points_count > 0:
            sample = client.scroll(
                collection_name=QDRANT_COLLECTION_NAME,
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
            'name': QDRANT_COLLECTION_NAME,
            'vector_size': vector_size,
            'points_count': points_count
        }
    except Exception as e:
        print(f"Error getting collection info: {str(e)}")
        return None

def ensure_collection_exists():
    """Ensure Qdrant collection exists with proper configuration"""
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        exists = any(c.name == QDRANT_COLLECTION_NAME for c in collections)
        
        if not exists:
            # Create collection with proper configuration
            client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config={
                    "size": VECTOR_SIZE,
                    "distance": "Cosine"
                },
                optimizers_config={
                    "default_segment_number": 2,
                    "max_optimization_threads": 2
                },
                hnsw_config={
                    "m": 16,
                    "ef_construct": 100,
                    "full_scan_threshold": 10000
                }
            )
            print(f"Created collection {QDRANT_COLLECTION_NAME}")
        else:
            print(f"Collection {QDRANT_COLLECTION_NAME} already exists")
    except Exception as e:
        print(f"Error ensuring collection exists: {str(e)}")
        raise
    try:
        # Check if collection exists first
        try:
            collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
            print(f"Collection already exists with {collection_info.points_count} points")
            return True
        except Exception as e:
            # Only proceed to create if collection doesn't exist
            if 'Not Found' not in str(e):
                print(f"Error checking collection: {str(e)}")
                return False
            
        # Collection doesn't exist, create it
        print(f"Creating new collection {QDRANT_COLLECTION_NAME}")
        try:
            client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE
                ),
                hnsw_config=models.HnswConfigDiff(
                    m=16,
                    ef_construct=100
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    default_segment_number=2,
                    indexing_threshold=0,
                    memmap_threshold=0
                ),
                on_disk_payload=True
            )
            print(f"Successfully created collection {QDRANT_COLLECTION_NAME}")
            return True
        except Exception as create_error:
            if 'already exists' in str(create_error):
                print(f"Collection {QDRANT_COLLECTION_NAME} already exists (concurrent creation)")
                return True
            raise create_error
            
    except Exception as e:
        print(f"Fatal error managing collection: {str(e)}")
        return False

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
        client.upsert(collection_name=QDRANT_COLLECTION_NAME, points=points)

def search_documents(query_vector, top_k=15):
    """Search for similar documents in Qdrant collection."""
    try:
        # Get collection info
        collection_info = client.get_collection(QDRANT_COLLECTION_NAME)
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
        count = client.count(QDRANT_COLLECTION_NAME)
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
            collection_name=QDRANT_COLLECTION_NAME,
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
