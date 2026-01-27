# promote_admin.py
import os
from sqlalchemy import create_engine, text

# Configuration
PROD_DB_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

def promote():
    print(f"Connecting to production database...")
    try:
        engine = create_engine(PROD_DB_URL)
        email = "admin@dz-kitab.com"
        
        with engine.connect() as conn:
            # Check if user exists
            result = conn.execute(text("SELECT id, username, is_admin FROM users WHERE email = :email"), {"email": email})
            user = result.fetchone()
            
            if not user:
                print(f"User '{email}' not found. Please register this account on the website first!")
                return
            
            print(f"Found user: {user.username} (ID: {user.id}, Is Admin: {user.is_admin})")
            
            if user.is_admin:
                print("User is already an admin. No action needed.")
                return
                
            print(f"Promoting '{email}' to admin...")
            conn.execute(text("UPDATE users SET is_admin = TRUE WHERE email = :email"), {"email": email})
            conn.commit()
            print("SUCCESS! User is now an administrator.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    promote()
