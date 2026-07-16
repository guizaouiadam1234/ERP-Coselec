import sqlite3

conn = sqlite3.connect("erp.db")
try:
    conn.execute("ALTER TABLE fuel_requests ADD COLUMN employee_id INTEGER;")
    print("Added employee_id to fuel_requests")
except Exception as e:
    print(f"Error: {e}")
conn.close()
