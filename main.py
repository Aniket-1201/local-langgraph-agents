import os
from fastapi import FastAPI
from pydantic import BaseModel
from supervisor import build_graph

# 1. Initialize the API
app = FastAPI(title="Corporate Brain AI Backend")

# 2. Build your LangGraph once when the server starts
agent_graph = build_graph()

# 3. Define the expected incoming JSON format
class ChatRequest(BaseModel):
    question: str

# 4. Create a health check endpoint (Good for Hugging Face Spaces)
@app.get("/")
def health_check():
    return {"status": "online", "message": "Dual-Agent LangGraph is active."}

# 5. Create the main Chat Endpoint
@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        # Run the question through your LangGraph routing engine!
        result = agent_graph.invoke({"question": request.question})
        
        # Extract the final string and send it back to Streamlit
        final_answer = result.get("final_answer", "Error: No answer generated.")
        return {"response": final_answer}
        
    except Exception as e:
        return {"response": f"Backend Error: {str(e)}"}

# 6. Server launch configuration
if __name__ == "__main__":
    import uvicorn
    # Hugging Face Spaces requires apps to run on port 7860
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)