import sqlite3
import os

# Ensure the db folder exists
os.makedirs("db", exist_ok=True)
DB_PATH = "db/corporate.db"

def create_database():
    print("Connecting to local SQLite database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create an Employees table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        salary INTEGER,
        status TEXT NOT NULL
    )
    """)

    # Insert fake corporate data with intentionally weird department names
    employees = [
        (1, "Alice Smith", "Eng_Sys_Ops", 120000, "Active"),
        (2, "Bob Jones", "Human_Capital_Matrix", 75000, "Active"),
        (3, "Charlie Brown", "Eng_Sys_Ops", 110000, "On_Leave"),
        (4, "Diana Prince", "Exec_Command", 150000, "Active")
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO Employees VALUES (?, ?, ?, ?, ?)", employees)
    conn.commit()
    conn.close()
    
    print(f"Success! Mock database created at {DB_PATH}")

if __name__ == "__main__":
    create_database()