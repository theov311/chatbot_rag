import os
import re
from rag import RAGChatbot
from evaluation import EvaluationSystem

def main():
    # Path to the vector database
    vector_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vectordb")
    
    # Check if the vector database exists
    if not os.path.exists(vector_db_path):
        print("Vector database not found. Please run main.py first to create the database.")
        return
    
    # Initialize the RAG chatbot
    print("Initializing RAG chatbot...")
    chatbot = RAGChatbot(
        vector_db_path=vector_db_path,
        model_name="tinyllama",
        num_passages=4  # Retrieve 4 most relevant passages
    )
    
    # Initialize the evaluation system
    evaluator = EvaluationSystem()
    
    print("\nRAG Chatbot initialized!")
    print("This chatbot can answer questions about LangChain documentation.")
    print("Type 'exit' to quit.")
    
    # Main interaction loop
    while True:
        # Get user input
        user_question = input("\nAsk a question: ")
        
        # Check if user wants to exit
        if user_question.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        
        # Skip empty questions
        if not user_question.strip():
            continue
        
        print("Thinking...")
        
        # Get response from the chatbot
        response = chatbot.query(user_question)
        answer = response["answer"]
        
        # Print the answer
        print("\nAnswer:")
        print(answer)
        
        # Collect source IDs for logging
        source_ids = [doc.metadata.get('id', 'unknown') for doc in response["source_documents"]]
        
        # Ask if user wants to see sources
        show_sources = input("\nDo you want to see the sources? (y/n): ").lower()
        if show_sources == "y":
            print("\nSources:")
            for i, doc in enumerate(response["source_documents"]):
                # Simple emoji removal with regex
                clean_content = re.sub(r'[^\x00-\x7F]+', '', doc.page_content[:200])
                print(f"Source {i+1}:")
                print(f"Content: {clean_content}...")
                print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"ID: {doc.metadata.get('id', 'Unknown')}")
                print()
        
        # Get user evaluation
        print("\nHow would you rate this answer? (1-5, where 5 is excellent)")
        rating = 0
        while rating < 1 or rating > 5:
            try:
                rating = int(input("Rating (1-5): "))
                if rating < 1 or rating > 5:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get optional feedback
        feedback = input("Any additional feedback? (optional): ")
        
        # Log the evaluation
        evaluator.log_evaluation(
            question=user_question,
            answer=answer,
            rating=rating,
            feedback=feedback,
            source_ids=source_ids
        )
        
        print("Thank you for your feedback!")

if __name__ == "__main__":
    main()