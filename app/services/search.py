from typing import List, Dict, Any
from ..db.vector_db import search_documents, get_collection_info
from .embeddings import generate_query_embedding

async def search_articles(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search for articles related to a query."""
    print(f"\nSearching for articles related to: {query}")
    
    try:
        # Generate query embedding
        print("Generating query embedding...")
        query_embedding = generate_query_embedding(query)
        if not query_embedding:
            print("Failed to generate query embedding")
            return []
        print(f"Generated query embedding with size {len(query_embedding)}")
            
        # Search for similar documents
        print("Searching for similar documents...")
        search_result = search_documents(query_embedding, top_k=top_k)
        if not search_result:
            print("Search failed - no result returned")
            return []
            
        status = search_result.get('status')
        if status != 'ok':
            print(f"Search returned non-OK status: {status}")
            if status == 'vector_size_mismatch':
                print("Vector size mismatch between query and collection")
            return []
            
        points = search_result.get('result', {}).get('points', [])
        if not points:
            print("No matching documents found in search results")
            return []
            
        print(f"Found {len(points)} matching points")
        
        # Format results
        articles = []
        for point in points:
            payload = point.get('payload', {})
            if not payload:
                print(f"Warning: Missing payload for point {point.get('id')}")
                continue
                
            articles.append({
                'title': payload.get('title', 'No title'),
                'content': payload.get('content', 'No content'),
                'date': payload.get('date', ''),
                'url': payload.get('url', ''),
                'score': point.get('score', 0.0)
            })
            
        print(f"Successfully formatted {len(articles)} articles")
        return articles
            
    except Exception as e:
        print(f"Error in search_articles: {str(e)}")
        return []
        best_score = max(chunk["score"] for chunk in chunks)
        
        # Combine chunks into context (limit to first 500 characters)
        context = " ... ".join(chunk["chunk"] for chunk in chunks)[:500]
        
        final_results.append({
            "title": chunks[0]["title"],
            "url": chunks[0]["url"],
            "content": context,
            "score": best_score,
            "matching_chunks": len(chunks)
        })
    
    # Sort final results by score and limit to top_k
    final_results.sort(key=lambda x: x["score"], reverse=True)
    return final_results[:top_k]