import os
import sys
from sqlalchemy import create_engine, MetaData, Table, select, text, DateTime, Boolean
from sqlalchemy.engine import reflection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate():
    # 1. Setup connections
    sqlite_url = os.getenv("DATABASE_URL", "sqlite:///./erp.db")
    if not sqlite_url.startswith("sqlite"):
        # If the user has already changed DATABASE_URL to postgres, try to read fallback/default
        sqlite_url = "sqlite:///./erp.db"
    
    postgres_url = os.getenv("POSTGRES_DATABASE_URL")
    if not postgres_url:
        print("Error: POSTGRES_DATABASE_URL environment variable is not set.")
        print("Please set it in your backend/.env file, e.g.:")
        print("POSTGRES_DATABASE_URL=postgresql://postgres:password@localhost:5432/erp_db")
        sys.exit(1)

    print(f"Connecting to Source Database (SQLite): {sqlite_url}")
    src_engine = create_engine(sqlite_url)
    
    print(f"Connecting to Destination Database (PostgreSQL): {postgres_url}")
    tgt_engine = create_engine(postgres_url)

    # 2. Reflect source schema
    print("Reflecting source database schema...")
    src_metadata = MetaData()
    src_metadata.reflect(bind=src_engine)

    # Adjust types and default values for PostgreSQL compatibility
    for table in src_metadata.tables.values():
        for column in table.columns:
            # Convert custom/SQLite DATETIME to standard DateTime
            if 'DATETIME' in str(column.type).upper():
                column.type = DateTime()
            
            # Convert SQLite boolean integer defaults (0/1) to Postgres boolean defaults (false/true)
            if isinstance(column.type, Boolean) and column.server_default is not None:
                default_val = str(column.server_default.arg).strip().replace("'", "").replace('"', '')
                if default_val == '1':
                    column.server_default = text('true')
                elif default_val == '0':
                    column.server_default = text('false')

    # 3. Create schema in target database
    print("Creating tables in PostgreSQL...")
    src_metadata.create_all(bind=tgt_engine)

    # 4. Migrate data
    src_conn = src_engine.connect()
    tgt_conn = tgt_engine.connect()

    # Disable foreign key checks / triggers during import on Postgres
    print("Temporarily disabling foreign key constraints on target database...")
    tgt_conn.execute(text("SET session_replication_role = 'replica';"))
    tgt_conn.commit()

    try:
        # Loop through tables and copy
        for table_name in src_metadata.tables:
            table = Table(table_name, src_metadata, autoload_with=src_engine)
            print(f"Migrating table: {table_name}...")
            
            # Fetch all rows from SQLite
            rows = src_conn.execute(table.select()).fetchall()
            if not rows:
                print(f"  No data for table {table_name}.")
                continue
            
            # Prepare rows for insertion
            insert_data = [dict(row._mapping) for row in rows]
            
            # Insert rows into Postgres
            tgt_table = Table(table_name, src_metadata, autoload_with=tgt_engine)
            tgt_conn.execute(tgt_table.insert(), insert_data)
            tgt_conn.commit()
            print(f"  Successfully migrated {len(insert_data)} rows.")
            
        print("Data migration completed successfully!")

        # 5. Reset sequence values in PostgreSQL for serial keys
        print("Resetting PostgreSQL sequences...")
        inspector = reflection.Inspector.from_engine(tgt_engine)
        for table_name in src_metadata.tables:
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_cols = pk_constraint.get('constrained_columns', []) if pk_constraint else []
            for col in pk_cols:
                # Typically, auto-increment fields are integer primary keys named 'id'
                col_info = next((c for c in inspector.get_columns(table_name) if c['name'] == col), None)
                if col_info and 'INT' in str(col_info['type']).upper():
                    try:
                        seq_query = text(f"SELECT setval(pg_get_serial_sequence('{table_name}', '{col}'), coalesce(max({col}), 1)) FROM {table_name};")
                        tgt_conn.execute(seq_query)
                        tgt_conn.commit()
                        print(f"  Reset sequence for {table_name}.{col}")
                    except Exception as e:
                        # Some tables might not use a serial sequence for their primary key (e.g. association tables)
                        pass

    except Exception as e:
        print(f"\nMigration failed: {e}")
        tgt_conn.rollback()
        raise e
    finally:
        # Restore foreign key checks / triggers
        print("Re-enabling foreign key constraints on target database...")
        tgt_conn.execute(text("SET session_replication_role = 'origin';"))
        tgt_conn.commit()
        
        src_conn.close()
        tgt_conn.close()
        src_engine.dispose()
        tgt_engine.dispose()

if __name__ == "__main__":
    migrate()
