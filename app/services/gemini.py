from google import generativeai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
# Global variable to store the initialized Gemini model
_gemini_model = None


def format_news_context(news_context: list) -> str:
    """Format news context for the prompt"""
    formatted = []
    for i, article in enumerate(news_context, 1):
        formatted.append(f"Article {i}:")
        formatted.append(f"Title: {article.get('title', 'No title')}")
        formatted.append(f"Content: {article.get('content', 'No content')}\n")
    return "\n".join(formatted)


def count_tokens(text: str) -> int:
    """Estimate token count using a simple heuristic"""
    # A rough estimate: 1 token ≈ 4 characters
    return len(text) // 4


def initialize_gemini():
    """Initialize the Gemini model (if needed) and return it."""
    global _gemini_model
    if _gemini_model is None:
        try:
            generativeai.configure(api_key=GEMINI_API_KEY)
            _gemini_model = generativeai.GenerativeModel('models/gemini-2.0-flash')
            print("Gemini model initialized.")
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            raise  # Re-raise the exception to be handled in main.py
    return _gemini_model



def generate_final_answer(query: str, news_context: list):
    """Generate an answer using the Gemini model."""
    try:
        # Initialize model if needed
        model = initialize_gemini()
        if not model:
            return "I apologize, but I'm currently unable to process your request due to a technical issue."
        
        # Format news context into a string
        context_str = "\n\n".join(
            f"Article {i+1}:\nTitle: {article.get('title', 'No title')}\n{article.get('content', 'No content')}"
            for i, article in enumerate(news_context)
        )
        
        # Construct the prompt
        prompt = f"""Based on the following news articles, answer this question: {query}

Context from news articles:
{context_str}

Please provide a comprehensive answer based on the provided news articles. If the articles don't contain relevant information to answer the question, please indicate that."""
        
        # Generate response
        print("Generating response from Gemini...")
        response = model.generate_content(prompt)
        
        # Extract and process the response
        if not response or not response.text:
            print("No response generated from Gemini")
            return "I apologize, but I couldn't generate a response based on the provided context."
        
        answer = response.text.strip()
        print(f"Generated answer: {answer[:200]}...")
        
        return answer
        
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return "I apologize, but I encountered an error while processing your request."

        if "API_KEY_INVALID" in str(e):
            return "Error: Invalid API key. Please check your API key configuration."
        elif "PERMISSION_DENIED" in str(e):
            return "Error: Permission denied. Please check API key permissions."
        elif "QUOTA_EXCEEDED" in str(e):
            return "Error: API quota exceeded. Please try again later."
        elif "model not found" in str(e).lower():
            return "Error: Model not found. Please check model configuration."
        else:
            return "I apologize, but I encountered an error while trying to generate an answer. Please try again."



# Test the Gemini service if run directly
if __name__ == "__main__":
    load_dotenv()
    apikey = os.getenv("GEMINI_API_KEY")
    if not apikey:
        print("Error: GEMINI_API_KEY environment variable not set for direct test.")
    else:
        generativeai.configure(api_key=apikey)  # Configure here for direct test
        model = initialize_gemini()
        if model:
            response = model.generate_content("Say hello.")
            print("Test response:", response.text)