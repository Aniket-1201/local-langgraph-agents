import os
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

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
        "You are an intelligent routing supervisor. Route the user's question to the correct expert system.\n"
        "If the question is about corporate policies, tools, or whitepapers, reply strictly with 'RAG'.\n"
        "If the question is about active employees, salaries, departments, or database metrics, reply strictly with 'SQL'.\n\n"
        "Question: {question}\n"
        "Route:"
    )
    
    # Ask the LLM to make a routing decision
    response = llm.invoke(prompt.format(question=question))
    decision = response.content.strip().upper()
    
    # Clean up the output to ensure exact routing match
    if "RAG" in decision:
        route = "RAG"
    elif "SQL" in decision:
        route = "SQL"
    else:
        route = "RAG" # Fallback if it gets confused
        
    print(f"Decision Made: Sending to -> {route}")
    return {"route": route}

def rag_node(state: GraphState):
    print("--- 📄 ROUTED TO RAG ---")
    # This is a "Mock Node". We will swap this with your query.py logic later!
    return {"final_answer": "I am the RAG node. I will search the PDFs for your answer."}

def sql_node(state: GraphState):
    print("--- 📊 ROUTED TO SQL ---")
    # This is a "Mock Node". We will swap this with Aniket's sql_agent.py logic later!
    return {"final_answer": "I am the SQL node. I will search the SQLite DB for your answer."}

# 3. Define the Conditional Routing Logic
def route_question(state: GraphState):
    # LangGraph uses this function to read the state and choose the next node
    return state["route"]

# 4. Build the State Machine Graph
def build_graph():
    workflow = StateGraph(GraphState)
    
    # Add our three nodes to the graph
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("sql", sql_node)
    
    # Draw the edges (how the data flows)
    workflow.add_edge(START, "supervisor")
    
    # The conditional edge reads the 'route_question' function and branches accordingly
    workflow.add_conditional_edges(
        "supervisor",
        route_question,
        {
            "RAG": "rag",
            "SQL": "sql"
        }
    )
    
    # End the graph after the experts respond
    workflow.add_edge("rag", END)
    workflow.add_edge("sql", END)
    
    return workflow.compile()

def main():
    app = build_graph()
    
    # Test 1: A question meant for Aniket's database
    print("\n=== TEST 1: SQL Routing ===")
    result1 = app.invoke({"question": "How many active employees do we have in the Eng_Sys_Ops department?"})
    print(f"Final Answer: {result1.get('final_answer')}")
    
    # Test 2: A question meant for your RAG PDFs
    print("\n=== TEST 2: RAG Routing ===")
    result2 = app.invoke({"question": "What are the three primary tool types?"})
    print(f"Final Answer: {result2.get('final_answer')}")

if __name__ == "__main__":
    main()