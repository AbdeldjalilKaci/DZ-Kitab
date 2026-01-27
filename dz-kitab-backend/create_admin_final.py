# create_admin_final.py
import os
from sqlalchemy import create_engine, text

# Configuration
PROD_DB_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

def create():
    print(f"Connecting to production database...")
    try:
        engine = create_engine(PROD_DB_URL)
        email = "admin@dz-kitab.com"
        username = "admin"
        # Using plain text password because the backend has a fallback:
        # if hashed_password does not start with '$2', it compares directly.
        password = "Admin.com2026"
        
        with engine.connect() as conn:
            # 1. Clean existing
            conn.execute(text("DELETE FROM users WHERE email = :email OR username = :uname"), {"email": email, "uname": username})
            
            # 2. Insert
            query = text("""
                INSERT INTO users (email, username, hashed_password, first_name, last_name, is_admin, is_active, university)
                VALUES (:email, :username, :hashed_password, :first_name, :last_name, :is_admin, :is_active, :university)
            """)
            
            conn.execute(query, {
                "email": email,
                "username": username,
                "hashed_password": password, # PLAIN TEXT
                "first_name": "Admin",
                "last_name": "User",
                "is_admin": True,
                "is_active": True,
                "university": "ESTIN"
            })
            conn.commit()
            print(f"SUCCESS! Admin account injected into production.")
            print(f"Email: {email}")
            print(f"Password: {password}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create()
