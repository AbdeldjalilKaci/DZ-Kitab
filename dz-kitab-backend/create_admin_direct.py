# create_admin_direct.py
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Configuration
# This is the hardcoded production URL from app/database.py to ensure we hit the right target
PROD_DB_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_admin():
    print(f"Connecting to production database...")
    try:
        engine = create_engine(PROD_DB_URL)
        
        # Admin Details
        email = "admin@dz-kitab.com"
        username = "admin"
        password = "Admin.com2026"
        hashed_pw = get_password_hash(password)
        
        with engine.connect() as conn:
            # 1. Clean existing admin if any (to avoid duplicate errors)
            print(f"Cleaning up existing admin '{email}'...")
            conn.execute(text("DELETE FROM users WHERE email = :email OR username = :uname"), {"email": email, "uname": username})
            
            # 2. Insert new admin
            print(f"Injecting new admin account...")
            query = text("""
                INSERT INTO users (email, username, hashed_password, first_name, last_name, is_admin, is_active, university)
                VALUES (:email, :username, :hashed_password, :first_name, :last_name, :is_admin, :is_active, :university)
            """)
            
            conn.execute(query, {
                "email": email,
                "username": username,
                "hashed_password": hashed_pw,
                "first_name": "DZ-Kitab",
                "last_name": "Admin",
                "is_admin": True,
                "is_active": True,
                "university": "ESTIN"
            })
            conn.commit()
            print(f"\nSUCCESS! Admin account created on production.")
            print(f"Email: {email}")
            print(f"Password: {password}")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    create_admin()
