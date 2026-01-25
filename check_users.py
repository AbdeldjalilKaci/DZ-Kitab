import os
import sys
from sqlalchemy import create_engine, text

# Add app directory to path
sys.path.append('c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend')

from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print("--- ALL USERS ---")
    result = conn.execute(text("SELECT id, username, email FROM users"))
    for row in result.fetchall():
        print(f"ID: {row[0]} | Username: {row[1]} | Email: {row[2]}")
