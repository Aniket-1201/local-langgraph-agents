import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

DATA_DIR = "data"
DB_DIR = "chroma_db"

def main():
    if not os.path.exists(DATA_DIR):
        print(f"Error: The '{DATA_DIR}' folder does not exist.")
        return

    documents = []
    
    # 1. Iterate through every PDF in the data folder
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".pdf"):
            file_path = os.path.join(DATA_DIR, filename)
            try:
                print(f"Loading {filename}...")
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            except Exception as e:
                # This prevents the crash we saw earlier!
                print(f"⚠️ Skipping corrupted file {filename}: {e}")

    if not documents:
        print("No documents loaded. Please check your data folder.")
        return

    print(f"Total pages loaded: {len(documents)}.")

    # 2. Split text
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split document into {len(chunks)} distinct chunks.")

    # 3. Embed and Save
    print("Initializing embedding model (all-minilm)...")
    embedding_model = OllamaEmbeddings(model="all-minilm")

    print("Converting text to vectors and saving to ChromaDB...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=DB_DIR,
        collection_name="corporate_policies" 
    )
    
    print(f"Success! Vector database saved to '{DB_DIR}'.")

if __name__ == "__main__":
    main()