import sqlite3

conn = sqlite3.connect("erp.db")
conn.execute("ALTER TABLE tasks ADD COLUMN start_date DATE;")
conn.close()
print("Column added successfully.")