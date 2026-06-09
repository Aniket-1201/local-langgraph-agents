import re
from langchain_community.utilities import SQLDatabase
from langchain_classic.chains import create_sql_query_chain
from langchain_ollama import ChatOllama

def extract_sql(llm_text: str) -> str:
    # First try the SQLQuery: marker
    if "SQLQuery:" in llm_text:
        extracted = llm_text.split("SQLQuery:")[-1].strip()
        if "SQLResult" in extracted:
            extracted = extracted.split("SQLResult")[0].strip()
        return extracted
    
    # Fallback: find SELECT statement directly using regex
    match = re.search(r"(SELECT\s+.+?)(?:;|$)", llm_text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return llm_text

def execute_sql_query(user_question: str) -> str:
    db_uri = "sqlite:///db/corporate.db"
    db = SQLDatabase.from_uri(db_uri)
    llm = ChatOllama(model="custom-sql-brain", temperature=0)
    chain = create_sql_query_chain(llm, db)
    
    # 1. Run the model chain
    response = chain.invoke({"question": user_question})
    llm_text = str(response)
    
    # 2. Extract ONLY the actual SQL query
    extracted_query = extract_sql(llm_text)

    # 3. Apply markdown and syntax cleanups
    clean_query = extracted_query.replace("```sql", "").replace("```", "").replace("`", "").strip()
    clean_query = clean_query.rstrip("*").strip()
    
    if ";" in clean_query:
        clean_query = clean_query.split(";")[0]
        
    # 4. Attempt to run the fully isolated query against SQLite
    try:
        result = db.run(clean_query)
        return f"Database Result: {result}"
    except Exception as e:
        return f"Error executing SQL: {e}"
    
def main():
    db_uri = "sqlite:///db/corporate.db"
    db = SQLDatabase.from_uri(db_uri)
    print(f"Connected to database! Found tables: {db.get_usable_table_names()}")

    llm = ChatOllama(model="custom-sql-brain", temperature=0)
    chain = create_sql_query_chain(llm, db)

    question = "How many active employees do we have in the Eng_Sys_Ops department?"
    print(f"\nUser Question: {question}")
    
    response = chain.invoke({"question": question})
    clean_query = extract_sql(str(response))
    clean_query = clean_query.replace("```sql", "").replace("```SQL", "").replace("```", "").strip()
    
    if ";" in clean_query:
        clean_query = clean_query.split(";")[0]
        
    print("\n--- QWEN GENERATED SQL ---")
    print(clean_query)
    
    try:
        result = db.run(clean_query)
        print("\n--- SQLITE EXECUTION RESULT ---")
        print(result)
    except Exception as e:
        print(f"\nError executing SQL: {e}")

if __name__ == "__main__":
    main()