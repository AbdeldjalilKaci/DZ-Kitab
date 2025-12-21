import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

def wait_for_db(database_url: str, retries: int = 10, delay: int = 3):
    engine = create_engine(database_url)
    for i in range(retries):
        try:
            with engine.connect():
                print("✅ Database is ready!")
                return
        except OperationalError:
            print(f"Waiting for DB... attempt {i + 1}/{retries}")
            time.sleep(delay)
    raise Exception("❌ Database not available after several retries.")
