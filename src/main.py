import os
from utils import load_jsonl_documents
from embedding import DocumentProcessor

def main():
    # Create data directories if they don't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    input_dir = os.path.join(data_dir, "input")
    db_dir = os.path.join(data_dir, "vectordb")
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(db_dir, exist_ok=True)
    
    # Path to your JSONL file (you need to download and place it in the input directory)
    # Download from https://huggingface.co/datasets/antonioibars/langchain-docs
    jsonl_path = os.path.join(input_dir, "train.jsonl")
    
    # Check if the file exists
    if not os.path.exists(jsonl_path):
        print(f"Please download the JSONL file and place it at: {jsonl_path}")
        print("Dataset URL: https://huggingface.co/datasets/antonioibars/langchain-docs")
        return
    
    # Load documents
    print("Loading documents...")
    documents = load_jsonl_documents(jsonl_path, content_key="text")
    
    if not documents:
        print("No documents were loaded. Please check the file format and content_key.")
        return
    
    # Initialize document processor
    processor = DocumentProcessor(chunk_size=512, chunk_overlap=102)
    
    # Chunk documents
    print("Chunking documents...")
    chunked_docs = processor.chunk_documents(documents)
    
    # Create vector store
    print("Creating vector database...")
    vector_db = processor.create_vector_store(chunked_docs, db_dir)
    
    print("Document processing complete!")
    
if __name__ == "__main__":
    main()