import os
import sys
from sqlalchemy import create_engine, text

# Add app directory to path
sys.path.append('c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend')

from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print("--- LATEST 10 NOTIFICATIONS ---")
    result = conn.execute(text("SELECT id, user_id, type, title, is_read, created_at FROM notifications ORDER BY created_at DESC LIMIT 10"))
    rows = result.fetchall()
    if not rows:
        print("No notifications found.")
    for row in rows:
        print(f"ID: {row[0]} | UserID: {row[1]} | Type: {row[2]} | Title: {row[3]} | Read: {row[4]} | Created: {row[5]}")
