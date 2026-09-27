from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from sql_agent import execute_sql_query

load_dotenv()

# UPGRADE 1: Singleton Pattern (Initialize AI once at startup)
ROUTING_LLM = ChatOllama(model="llama3.2:3b", temperature=0)
CHAT_LLM = ChatOllama(model="llama3.2:3b", temperature=0.7)
EMBEDDINGS = OllamaEmbeddings(model="all-minilm")

try:
    VECTOR_STORE = Chroma(
        persist_directory="chroma_db",
        embedding_function=EMBEDDINGS,
        collection_name="corporate_policies"
    )
except Exception as e:  # noqa: BLE001
    print(f"Warning: Could not connect to ChromaDB: {e}")
    VECTOR_STORE = None

# UPGRADE 2: Add Conversation Memory to GraphState
class GraphState(TypedDict):
    question: str
    history: list[dict[str, Any]] # Stores past conversation turns
    route: str
    final_answer: str

# UPGRADE 3: Graceful Error Handling inside Nodes
def supervisor_node(state: GraphState):
    print("\n--- 🧠 SUPERVISOR THINKING ---")
    question = state["question"]
    
    try:
        prompt = PromptTemplate.from_template(
            "You are an intelligent routing supervisor. Your job is to classify the user's question into one of three categories: 'SQL', 'RAG', or 'CHAT'.\n\n"
            "Rules:\n"
            "1. Reply strictly with 'SQL' if the question asks about active employees, salaries, departments, or database metrics.\n"
            "2. Reply strictly with 'RAG' if the question asks about corporate policies, company tools, GenAI whitepapers, or document summaries.\n"
            "3. Reply strictly with 'CHAT' if the question is a standard greeting (e.g., 'hello'), general conversation, or a question completely unrelated to company data.\n\n"
            "Question: {question}\n"
            "Route:"
        )
        
        response = ROUTING_LLM.invoke(prompt.format(question=question))
        decision = response.content.strip().upper()
        
        if "RAG" in decision:
            route = "RAG"
        elif "SQL" in decision:
            route = "SQL"
        else:
            route = "CHAT"
            
    except Exception as e:  # noqa: BLE001
        print(f"Supervisor Error: {e}")
        route = "CHAT" # Safe fallback if the LLM crashes
        
    print(f"Decision Made: Sending to -> {route}")
    return {"route": route}

def rag_node(state: GraphState):
    print("--- 📄 ROUTED TO RAG ---")
    question = state["question"]
    
    try:
        if not VECTOR_STORE:
            return {"final_answer": "⚠️ Error: The Document Database is currently offline."}
            
        retrieved_docs = VECTOR_STORE.similarity_search(question, k=3)
        context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        prompt_template = PromptTemplate.from_template(
            "You are a helpful enterprise AI assistant. Answer the user's question using ONLY the context provided below.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )
        
        final_prompt = prompt_template.format(context=context_text, question=question)
        response = ROUTING_LLM.invoke(final_prompt)
        return {"final_answer": response.content}
        
    except Exception as e:  # noqa: BLE001
        return {"final_answer": f"⚠️ RAG Pipeline Error: {e!s}"}

def sql_node(state: GraphState):
    print("--- 📊 ROUTED TO SQL ---")
    question = state["question"]
    
    try:
        answer = execute_sql_query(question) 
        return {"final_answer": answer}
    except Exception as e:  # noqa: BLE001
        return {"final_answer": f"⚠️ SQL Pipeline Error: {e!s}"}

def chat_node(state: GraphState):
    print("--- 💬 ROUTED TO CHAT ---")
    question = state["question"]
    history = state.get("history", [])
    
    try:
        # Extract the last 3 messages to give the LLM basic context
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-3:]])
        context_prompt = f"Previous conversation:\n{history_text}\n\nUser: {question}\nAI:" if history else question
        
        response = CHAT_LLM.invoke(context_prompt)
        return {"final_answer": response.content}
        
    except Exception as e:  # noqa: BLE001
        return {"final_answer": f"⚠️ Chat Pipeline Error: {e!s}"}

def route_question(state: GraphState):
    return state["route"]

def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("sql", sql_node)
    workflow.add_node("chat", chat_node) 
    
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        route_question,
        {"RAG": "rag", "SQL": "sql", "CHAT": "chat"}
    )
    
    workflow.add_edge("rag", END)
    workflow.add_edge("sql", END)
    workflow.add_edge("chat", END) 
    
    return workflow.compile()

def main():
    app = build_graph()
    test_state = {"question": "Hello! How are you?", "history": []}
    result = app.invoke(test_state)
    print(f"Final Answer: {result.get('final_answer')}")

if __name__ == "__main__":
    main()