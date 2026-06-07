import os
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from sql_agent import execute_sql_query
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
    question = state["question"]
    
    # Run Aniket's Qwen Database logic!
    answer = execute_sql_query(question) 
    
    return {"final_answer": answer}

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