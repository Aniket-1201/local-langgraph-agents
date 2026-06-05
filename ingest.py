import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# NEW IMPORTS: Using the modern, dedicated packages to clear the warnings
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

DATA_PATH = "data/Newwhitepaper_Agents2.pdf"
DB_DIR = "chroma_db"

def main():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Please place a PDF named {DATA_PATH} in the 'data/' folder.")
        return

    print("Loading PDF document...")
    loader = PyPDFLoader(DATA_PATH)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages.")

    # FIX: Reduced chunk size from 1000 to 500 characters.
    # This ensures no chunk ever exceeds all-minilm's strict 256-token limit.
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split the document into {len(chunks)} distinct chunks.")

    print("Initializing embedding model (all-minilm)...")
    embedding_model = OllamaEmbeddings(model="all-minilm")

    print("Converting text to vectors and saving to ChromaDB...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=DB_DIR,
        collection_name="corporate_policies" 
    )
    
    print(f"Success! Vector database saved locally to the '{DB_DIR}' folder.")

if __name__ == "__main__":
    main()