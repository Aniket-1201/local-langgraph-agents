#!/bin/bash

# 1. Start the Ollama daemon in the background
echo "Starting Ollama server..."
ollama serve &

# 2. Wait for the Ollama server to boot up before sending commands
echo "Waiting for Ollama to initialize..."
sleep 10

# 3. Pull the Llama 3.2 router model
echo "Pulling llama3.2:3b for the Supervisor Node..."
ollama pull llama3.2:3b

# 4. Ingest your fine-tuned Qwen model using the Modelfile
echo "Creating custom-sql-brain..."
ollama create custom-sql-brain -f Modelfile

# 5. Start the FastAPI server on Hugging Face's required port (7860)
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 7860