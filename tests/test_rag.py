import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag import RAGChatbot

def test_rag_query():
    # Path to the vector database
    vector_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vectordb")
    
    # Initialize the RAG chatbot
    chatbot = RAGChatbot(
        vector_db_path=vector_db_path,
        model_name="tinyllama",
        num_passages=4
    )
    
    # Test questions about LangChain
    test_questions = [
        "What is LangChain?",
        "How can I use LangChain with OpenAI?",
        "What's the purpose of the RetrievalQA class?"
    ]
    
    # Test each question
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("Retrieving context and generating answer...")
        
        # Get the response
        response = chatbot.query(question)
        
        # Print the answer
        print(f"\nAnswer: {response['answer']}")
        
        # Print the sources (optional)
        print("\nSources:")
        for i, doc in enumerate(response['source_documents']):
            print(f"Source {i+1}:")
            print(f"Content: {doc.page_content[:150]}...")
            print(f"Metadata: {doc.metadata}")
            print()
        
        print("-" * 80)

if __name__ == "__main__":
    test_rag_query()