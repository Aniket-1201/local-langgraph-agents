#!/bin/bash
set -e
echo "--- DEBUG: Current directory ---"
pwd
echo "--- DEBUG: Files present ---"
ls -lh
echo "--- DEBUG: Modelfile contents ---"
cat Modelfile

echo "Starting Ollama server..."
ollama serve &

echo "Waiting for Ollama to initialize..."
sleep 15

# ✅ ADD THIS BLOCK - Download gguf from HF Model Hub
echo "Downloading fine-tuned model from HF Hub..."
hf download AniketDeshpande1201/corporate-sql-brain \
  qwen2.5-coder-3b-instruct.Q4_K_M.gguf \
  --local-dir .

echo "Pulling llama3.2:3b for the Supervisor Node..."
ollama pull llama3.2:3b

echo "Pulling all-minilm embedding model..."
ollama pull all-minilm

echo "Creating custom-sql-brain from Modelfile..."
ollama create custom-sql-brain -f Modelfile

echo "Setting up SQLite database..."
python setup_db.py

echo "Building vector database..."
python ingest.py

echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 7860