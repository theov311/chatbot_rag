import os
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document

class RAGChatbot:
    def __init__(
        self, 
        vector_db_path: str,
        model_name: str = "tinyllama",
        num_passages: int = 4
    ):
        """
        Initialize the RAG Chatbot
        
        Args:
            vector_db_path: Path to the Chroma vector database
            model_name: Name of the Ollama model to use
            num_passages: Number of passages to retrieve (3-5 recommended)
        """
        # Initialize the embedding model (same as used for indexing)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        # Load the vector store
        self.vector_store = Chroma(
            persist_directory=vector_db_path,
            embedding_function=self.embeddings
        )
        
        # Set up the retriever with the specified number of passages
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": num_passages}
        )
        
        # Initialize the LLM
        self.llm = OllamaLLM(model=model_name)
        
        # Create the prompt template
        template = """
        You are an AI assistant answering questions about LangChain documentation.
        Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say "I don't know", don't try to make up an answer.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer with a detailed explanation:
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create the RAG chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Simple approach that stuffs all documents into the prompt
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )
        
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question in natural language
            
        Returns:
            Dictionary containing the answer and source documents
        """
        # Get response from the chain
        response = self.qa_chain({"query": question})
        
        # Format and return the results
        result = {
            "answer": response["result"],
            "source_documents": response["source_documents"]
        }
        
        return result
    
    def get_retrieved_context(self, question: str) -> List[Document]:
        """
        Get the retrieved context for a question without generating an answer
        (useful for debugging)
        
        Args:
            question: User question in natural language
            
        Returns:
            List of retrieved documents
        """
        # Get documents from the retriever
        docs = self.retriever.get_relevant_documents(question)
        return docs