import os
import sys
import time

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag import RAGChatbot
from src.evaluation import EvaluationSystem

def test_complex_queries():
    # Path to the vector database
    vector_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vectordb")
    
    # Initialize the RAG chatbot
    print("Initializing RAG chatbot...")
    chatbot = RAGChatbot(
        vector_db_path=vector_db_path,
        model_name="tinyllama",
        num_passages=4
    )
    
    # Initialize the evaluation system
    evaluator = EvaluationSystem()
    
    # Complex test questions
    complex_queries = [
        {
            "question": "Compare LLMChain, RetrievalQA, and ConversationalRetrievalQA chains in LangChain and explain when to use each one.",
            "description": "Comparative question requiring integration of knowledge about multiple components"
        },
        {
            "question": "How would I implement a custom memory system in LangChain that stores conversation history in a database?",
            "description": "Implementation question requiring understanding of LangChain architecture"
        },
        {
            "question": "Explain the relationship between prompt templates, example selectors, and output parsers in LangChain's Model I/O module.",
            "description": "Relationship question requiring deep understanding of module interactions"
        },
        {
            "question": "What are the different document loading and processing techniques in LangChain, and how would I choose between them for a legal document analysis project?",
            "description": "Application-specific question requiring reasoning about use cases"
        },
        {
            "question": "Explain how LangChain's agents work internally, particularly the decision-making process for selecting tools and interpreting outputs.",
            "description": "Technical architecture question requiring deep understanding"
        }
    ]
    
    results = []
    
    # Test each complex query
    for i, query in enumerate(complex_queries, 1):
        question = query["question"]
        description = query["description"]
        
        print(f"\n\nTest Query {i}: {description}")
        print(f"Question: {question}")
        print("Retrieving context and generating answer...")
        
        start_time = time.time()
        response = chatbot.query(question)
        end_time = time.time()
        
        # Calculate response time
        response_time = end_time - start_time
        
        # Print the answer
        print(f"\nAnswer (generated in {response_time:.2f} seconds):")
        print(response["answer"])
        
        # Print sources
        print("\nSources:")
        source_ids = []
        for i, doc in enumerate(response["source_documents"]):
            source_id = doc.metadata.get('id', 'Unknown')
            source_ids.append(source_id)
            print(f"Source {i+1} (ID: {source_id}):")
            clean_content = doc.page_content[:100].replace('\n', ' ')
            print(f"  {clean_content}...")
        
        # Get manual rating (if running interactively)
        rating = 0
        try:
            print("\nHow would you rate this answer? (1-5, where 5 is excellent)")
            rating = int(input("Rating (1-5): "))
            feedback = input("Any feedback? (optional): ")
        except:
            # Non-interactive mode
            rating = None
            feedback = None
        
        # Save result
        result = {
            "question": question,
            "answer": response["answer"],
            "sources": source_ids,
            "response_time": response_time,
            "rating": rating,
            "feedback": feedback
        }
        results.append(result)
        
        # Log evaluation if rating was provided
        if rating:
            evaluator.log_evaluation(
                question=question,
                answer=response["answer"],
                rating=rating,
                feedback=feedback,
                source_ids=source_ids,
                metadata={"response_time": response_time, "description": description}
            )
        
        print("\n" + "="*80)
    
    # Summary
    print("\n\nTesting Summary:")
    print(f"Completed {len(complex_queries)} complex queries")
    if any(r.get("rating") for r in results):
        avg_rating = sum(r["rating"] for r in results if r["rating"]) / sum(1 for r in results if r["rating"])
        print(f"Average rating: {avg_rating:.2f}/5.0")
    avg_time = sum(r["response_time"] for r in results) / len(results)
    print(f"Average response time: {avg_time:.2f} seconds")

if __name__ == "__main__":
    test_complex_queries()