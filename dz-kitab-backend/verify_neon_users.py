# verify_neon_users.py
import os
from sqlalchemy import create_engine, text

# The Neon DB URL used in the apps fallback and my injection script
PROD_DB_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

def verify():
    print(f"Connecting to Neon DB...")
    try:
        engine = create_engine(PROD_DB_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, email, username, is_admin FROM users"))
            users = result.fetchall()
            
            print(f"\n=== Users in Neon DB ({len(users)}) ===")
            for u in users:
                print(f"ID: {u.id} | Email: {u.email} | Username: {u.username} | Admin: {u.is_admin}")
                
            if not any(u.email == "admin@dz-kitab.com" for u in users):
                print("\n❌ MISSING: admin@dz-kitab.com not found in this DB.")
            else:
                print("\n✅ FOUND: admin@dz-kitab.com exists in this DB.")
                
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify()
