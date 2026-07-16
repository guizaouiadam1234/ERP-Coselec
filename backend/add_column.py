import sqlite3

conn = sqlite3.connect("erp.db")
try:
    conn.execute("""
        CREATE TABLE leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type VARCHAR NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            reason VARCHAR,
            status VARCHAR DEFAULT 'Pending',
            pdf_url VARCHAR,
            justificatif_url VARCHAR,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        );
    """)
    print("Created table leave_requests")
except Exception as e:
    print(f"Error for leave_requests: {e}")
conn.close()