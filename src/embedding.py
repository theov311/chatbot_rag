import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

class DocumentProcessor:
    def __init__(self, chunk_size=512, chunk_overlap=102):
        """
        Initialize the document processor
        
        Args:
            chunk_size: Size of text chunks in tokens (approximately)
            chunk_overlap: Overlap between chunks (20% of chunk_size by default)
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        # Initialize the embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of chunked documents
        """
        chunked_docs = self.text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunked_docs)} chunks")
        return chunked_docs
        
    def create_vector_store(self, documents: List[Dict[str, Any]], persist_directory: str) -> Chroma:
        """
        Create a vector store from documents
        
        Args:
            documents: List of documents to embed
            persist_directory: Directory to persist the vector store
            
        Returns:
            Chroma vector store
        """
        # Create the directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Create and persist the vector store
        vector_db = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=persist_directory
        )
        
        print(f"Created vector store with {len(documents)} documents at {persist_directory}")
        
        return vector_db