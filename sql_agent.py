from langchain_community.utilities import SQLDatabase
from langchain_classic.chains import create_sql_query_chain
from langchain_ollama import ChatOllama

def main():
    # 1. Connect to our local SQLite database
    db_uri = "sqlite:///db/corporate.db"
    db = SQLDatabase.from_uri(db_uri)
    print(f"Connected to database! Found tables: {db.get_usable_table_names()}")

    # 2. Initialize the Local Qwen Coding Model
    # Temperature 0 makes the model deterministic (less creative = better at math/code)
    llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0)

    # 3. Create the LangChain SQL Pipeline
    # This automatically injects our table schemas into the prompt behind the scenes
    chain = create_sql_query_chain(llm, db)

    # 4. Ask a natural language question testing our weird corporate jargon
    question = "How many active employees do we have in the Eng_Sys_Ops department?"
    print(f"\nUser Question: {question}")
    
    # Generate the SQL
    response = chain.invoke({"question": question})
    
    clean_query = response.replace("```sql", "").replace("```SQL", "").replace("```", "").strip()
    
    # Force SQLite to only look at the first statement by splitting at the semicolon
    if ";" in clean_query:
        clean_query = clean_query.split(";")[0]
        
    print("\n--- QWEN GENERATED SQL ---")
    print(clean_query)
    
    try:
        # Run the raw SQL query directly against the SQLite file
        result = db.run(clean_query)
        print("\n--- SQLITE EXECUTION RESULT ---")
        print(result)
    except Exception as e:
        print(f"\nError executing SQL: {e}")    # This is where we will eventually capture failures for our fine-tuning dataset!

if __name__ == "__main__":
    main()