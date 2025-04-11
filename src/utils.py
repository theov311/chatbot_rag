import os
import json
from typing import List, Dict, Any
from langchain.schema import Document

def load_jsonl_documents(file_path: str, content_key: str = "text") -> List[Document]:
    """Load documents from a JSONL file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        documents = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                # Skip comment lines
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                
                try:
                    # Parse the JSON line
                    data = json.loads(line)
                    
                    # Extract the content using the content_key
                    if content_key in data:
                        content = data[content_key]
                        # Create a Document with the content and any metadata
                        doc = Document(
                            page_content=content,
                            metadata={"source": data.get("source", "Unknown"), "id": data.get("id", f"line_{line_number}")}
                        )
                        documents.append(doc)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON on line {line_number}: {e}")
                    # Continue with the next line instead of failing the entire process
                    continue
        
        print(f"Loaded {len(documents)} documents from {file_path}")
        return documents
        
    except Exception as e:
        print(f"Error loading documents: {e}")
        return []