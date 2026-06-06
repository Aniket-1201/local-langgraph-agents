from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import PromptTemplate

# 1. Setup the exact same models used in ingestion
EMBEDDING_MODEL = "all-minilm"
GENERATION_MODEL = "llama3.2:3b"
DB_DIR = "chroma_db"

def main():
    print("Connecting to the local ChromaDB...")
    
    # Initialize the embedding model so it knows how to translate the user's question into math
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    # Load the persistent database that ingest.py created
    vector_store = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings,
        collection_name="corporate_policies" # This must match what Aniket set!
    )
    
    # 2. Perform the Search
    # CHANGE THIS QUESTION TO MATCH YOUR 42 PAGES OF PDF DATA!
    question = question = "According to the document, what are the three primary tool types that Google models are able to interact with?"
    print(f"\nSearching for answers to: '{question}'\n")
    
    # Get the top 3 most relevant chunks from the database
    retrieved_docs = vector_store.similarity_search(question, k=3)
    
    # Combine the text from the 3 chunks into one large string
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # 3. Setup the Local LLM Generation
    print("Handing context to Llama 3.2 for the final answer...")
    llm = ChatOllama(model=GENERATION_MODEL, temperature=0)
    
    # Create strict instructions for the LLM
    prompt_template = PromptTemplate.from_template(
        "You are a helpful enterprise AI assistant. Answer the user's question using ONLY the context provided below.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    
    # Format the prompt with our variables
    final_prompt = prompt_template.format(context=context_text, question=question)
    
    # Ask the LLM and print the response!
    response = llm.invoke(final_prompt)
    print("\n--- AI RESPONSE ---")
    print(response.content)

if __name__ == "__main__":
    main()