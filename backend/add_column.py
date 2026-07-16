import sqlite3

conn = sqlite3.connect("erp.db")
tables = ["it_requests", "facility_requests", "hr_requests"]
for table in tables:
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN rejection_comment TEXT;")
        print(f"Added to {table}")
    except Exception as e:
        print(f"Error for {table}: {e}")
conn.close()