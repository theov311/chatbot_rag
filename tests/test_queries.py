from langchain_ollama import OllamaLLM

def test_ollama_model():
    # Initialize the Ollama model using the new class
    llm = OllamaLLM(model="tinyllama", temperature=0.7, max_tokens=256)
    
    # Simple test query
    test_prompt = "give me a haiku"
    
    print(f"Sending test query: '{test_prompt}'")
    print("Waiting for response...\n")
    
    # Get the response
    response = llm.invoke(test_prompt)
    
    print(f"Response:\n{response}")
    
    return response

if __name__ == "__main__":
    test_ollama_model()