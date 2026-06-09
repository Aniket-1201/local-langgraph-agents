import os
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from sql_agent import execute_sql_query
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
# Load the LangSmith API keys from your .env file
load_dotenv()

# 1. Define the Graph State
# This dictionary tracks variables as they move through our node pipeline
class GraphState(TypedDict):
    question: str
    route: str
    final_answer: str

# 2. Define the Nodes
def supervisor_node(state: GraphState):
    print("\n--- 🧠 SUPERVISOR THINKING ---")
    question = state["question"]
    
    # We use your lightweight Mac-friendly model for routing
    llm = ChatOllama(model="llama3.2:3b", temperature=0)
    
    # We give the LLM strict instructions on how to categorize questions
    prompt = PromptTemplate.from_template(
        "You are an intelligent routing supervisor. Your job is to classify the user's question into one of three categories: 'SQL', 'RAG', or 'CHAT'.\n\n"
        "Rules:\n"
        "1. Reply strictly with 'SQL' if the question asks about active employees, salaries, departments, or database metrics.\n"
        "2. Reply strictly with 'RAG' if the question asks about corporate policies, company tools, GenAI whitepapers, or document summaries.\n"
        "3. Reply strictly with 'CHAT' if the question is a standard greeting (e.g., 'hello'), general conversation, or a question completely unrelated to company data.\n\n"
        "Question: {question}\n"
        "Route:"
    )
    
    # Ask the LLM to make a routing decision
    response = llm.invoke(prompt.format(question=question))
    decision = response.content.strip().upper()
    
    # Clean up the output to ensure exact routing match
    # Clean up the output to ensure exact routing match
    if "RAG" in decision:
        route = "RAG"
    elif "SQL" in decision:
        route = "SQL"
    else:
        route = "CHAT" # Fallback to normal conversation if confused
        
    print(f"Decision Made: Sending to -> {route}")
    return {"route": route}

def rag_node(state: GraphState):
    print("--- 📄 ROUTED TO RAG ---")
    question = state["question"]
    
    # 1. Connect to your existing ChromaDB
    embeddings = OllamaEmbeddings(model="all-minilm")
    vector_store = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings,
        collection_name="corporate_policies"
    )
    
    # 2. Search for the relevant PDF chunks
    retrieved_docs = vector_store.similarity_search(question, k=3)
    context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # 3. Ask Llama 3.2 to answer based on the PDF
    llm = ChatOllama(model="llama3.2:3b", temperature=0)
    prompt_template = PromptTemplate.from_template(
        "You are a helpful enterprise AI assistant. Answer the user's question using ONLY the context provided below.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    
    final_prompt = prompt_template.format(context=context_text, question=question)
    response = llm.invoke(final_prompt)
    
    return {"final_answer": response.content}

def sql_node(state: GraphState):
    print("--- 📊 ROUTED TO SQL ---")
    question = state["question"]
    
    # Run Aniket's Qwen Database logic!
    answer = execute_sql_query(question) 
    
    return {"final_answer": answer}

def chat_node(state: GraphState):
    print("--- 💬 ROUTED TO CHAT ---")
    question = state["question"]
    
    # Use the lightweight model for general conversation
    llm = ChatOllama(model="llama3.2:3b", temperature=0.7)
    response = llm.invoke(question)
    
    return {"final_answer": response.content}

# 3. Define the Conditional Routing Logic
def route_question(state: GraphState):
    # LangGraph uses this function to read the state and choose the next node
    return state["route"]

# 4. Build the State Machine Graph
def build_graph():
    workflow = StateGraph(GraphState)
    
    # Add our FOUR nodes to the graph
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("sql", sql_node)
    workflow.add_node("chat", chat_node) # <-- New node registered
    
    # Draw the edges
    workflow.add_edge(START, "supervisor")
    
    # Update the conditional edge mapping
    workflow.add_conditional_edges(
        "supervisor",
        route_question,
        {
            "RAG": "rag",
            "SQL": "sql",
            "CHAT": "chat" # <-- New route mapped
        }
    )
    
    # End the graph after any expert responds
    workflow.add_edge("rag", END)
    workflow.add_edge("sql", END)
    workflow.add_edge("chat", END) # <-- Close the new route
    
    return workflow.compile()

def main():
    app = build_graph()
    
    # Test A: Checking for complex casing and fuzzy matching
    print("\n=== STRESS TEST A ===")
    result_a = app.invoke({"question": "Give me a list of anyone whose status is listed as 'ACTIVE' but write their names in all uppercase."})
    print(f"Final Answer: {result_a.get('final_answer')}") # <-- Added print
    
    # Test B: Requesting columns or concepts that don't exist in the schema
    print("\n=== STRESS TEST B ===")
    result_b = app.invoke({"question": "Who is the highest-paid manager in the Eng_Sys_Ops division?"}) 
    print(f"Final Answer: {result_b.get('final_answer')}") # <-- Added print

    # Test C: Ambiguous routing request
    print("\n=== STRESS TEST C ===")
    result_c = app.invoke({"question": "Can you check the company policy PDF to see how we calculate employee salaries, and then check the database to see who matches that criteria?"})
    print(f"Final Answer: {result_c.get('final_answer')}") # <-- Added print
    
if __name__ == "__main__":
    main()