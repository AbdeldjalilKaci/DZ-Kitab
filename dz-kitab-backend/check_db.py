# check_db.py
import os
from sqlalchemy import create_url, create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check():
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not found!")
        return

    print(f"Checking database...")
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\n=== Database Report ===")
        print(f"Tables found: {len(tables)}")
        for t in tables:
            count = 0
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT count(*) FROM {t}"))
                    count = result.scalar()
            except:
                pass
            print(f"- {t}: {count} rows")
            
        if "users" not in tables:
            print("\nWARNING: 'users' table is missing!")
        else:
            with engine.connect() as conn:
                user_count = conn.execute(text("SELECT count(*) FROM users")).scalar()
                if user_count == 0:
                    print("WARNING: 'users' table is empty!")
                else:
                    print(f"SUCCESS: Found {user_count} users.")
                    
    except Exception as e:
        print(f"ERROR: Could not connect or inspect: {e}")

if __name__ == "__main__":
    check()
