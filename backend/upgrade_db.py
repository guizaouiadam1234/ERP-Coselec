import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "erp.db")

def upgrade():
    print(f"Upgrading database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add columns to users table
    columns_to_add = [
        ("is_active", "BOOLEAN DEFAULT 1"),
        ("last_login", "DATETIME"),
        ("failed_login_attempts", "INTEGER DEFAULT 0"),
        ("locked_until", "DATETIME"),
        ("requires_password_change", "BOOLEAN DEFAULT 0")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists")
            else:
                print(f"Error adding {col_name}: {e}")

    # Create audit_logs table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER,
                target_user_id INTEGER,
                action_type VARCHAR,
                old_value VARCHAR,
                new_value VARCHAR,
                timestamp DATETIME,
                FOREIGN KEY(actor_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY(target_user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        print("Created table audit_logs")
    except sqlite3.OperationalError as e:
        print(f"Error creating audit_logs: {e}")

    conn.commit()
    conn.close()
    print("Upgrade completed.")

if __name__ == "__main__":
    upgrade()
