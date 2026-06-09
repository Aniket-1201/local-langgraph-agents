# Graph-Routed Multi-Agent RAG System

**Tech Stack:** Python | LangGraph | ChromaDB | Ollama | Streamlit | FastAPI | Hugging Face

## 📌 Project Overview
This repository contains a full-stack, decoupled AI microservice that implements a stateful, multi-agent routing architecture. The system acts as an enterprise copilot, utilizing a zero-shot local LLM to dynamically classify user intent and route execution to specialized nodes (Retrieval-Augmented Generation, Text-to-SQL, or General Chat). 

Designed to operate entirely on localized and open-source models, this architecture handles complex hardware constraints (RAM swapping on CPU tiers) through asynchronous frontend protocols and strict containerization.

---

## 🚀 Core Architecture & Features

### 1. Multi-Agent Routing Engine (LangGraph)
* **Stateful Orchestration**: Engineered a directed acyclic graph (DAG) using `LangGraph` (`StateGraph` and `TypedDict`) to manage conversational state and variable passing across distinct execution layers.
* **Zero-Shot Intent Classification**: Utilized a quantized **Llama 3.2 (3B)** model as the primary supervisor node, strictly prompting it to categorize raw user queries into one of three isolated execution paths: `RAG`, `SQL`, or `CHAT`.

### 2. Retrieval-Augmented Generation (RAG) Pipeline
* **Document Ingestion**: Built a local ingestion pipeline utilizing `PyPDFLoader` to process exactly 42 pages of highly dense enterprise whitepapers.
* **Optimized Vector Search**: Applied strict recursive text chunking (500-character size, 50-character overlap) to prevent context window overflow, embedding the chunks via the `all-minilm` model into a local `ChromaDB` instance. 
* **Contextual Retrieval**: Configured the vector store to perform similarity searches retrieving the top 3 most relevant chunks (`k=3`) to ground the generation model.

### 3. Text-to-SQL Agent Integration
* **Database Analytics**: Integrated a custom text-to-SQL pipeline designed to query a local `SQLite` database containing corporate employee metrics.
* **Custom Fine-Tuning**: Orchestrated the routing of quantitative database questions to a custom QLoRA fine-tuned `Qwen` model (`custom-sql-brain`) capable of parsing natural language into executable SQL syntax.

### 4. Cloud Deployment & Resilient UI
* **Decoupled Microservices**: Containerized the backend inference engine via a `FastAPI` REST wrapper (`@app.post("/api/chat")`) and deployed it as a headless backend on Hugging Face Spaces.
* **Fault-Tolerant Frontend**: Developed an interactive web interface using `Streamlit` with stateful chat memory. 
* **Latency Management**: Engineered asynchronous REST API requests with a custom 500-second timeout protocol to gracefully handle ~74-second compute bottlenecks caused by swapping heavy 3B parameter models in and out of limited CPU RAM.

---

## 🛠️ Repository Structure

```text
├── app.py                 # Streamlit frontend UI & asynchronous POST logic
├── main.py                # FastAPI microservice wrapper for the AI backend
├── supervisor.py          # LangGraph state machine, nodes, and routing edges
├── ingest.py              # ChromaDB vector embedding and PDF chunking pipeline
├── sql_agent.py           # Text-to-SQL generation and SQLite execution logic
├── setup_db.py            # SQLite database initialization script
├── start.sh               # Hugging Face Spaces startup & model downloading script
├── requirements.txt       # Python dependencies
└── data/                  # Directory containing 42 pages of target PDFs
