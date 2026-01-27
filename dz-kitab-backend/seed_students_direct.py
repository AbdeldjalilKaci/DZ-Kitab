# seed_students_direct.py
import os
from sqlalchemy import create_engine, text

# Configuration
PROD_DB_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

def seed():
    print(f"Connecting to production database...")
    try:
        engine = create_engine(PROD_DB_URL)
        password = "User.com2026"
        
        users = [
            {"email": "djalil_st@estin.dz", "username": "djalil_st", "first": "Djalil", "last": "Student"},
            {"email": "meriem_dz@estin.dz", "username": "meriem_dz", "first": "Meriem", "last": "Lounis"},
            {"email": "aniss_bk@estin.dz", "username": "aniss_bk", "first": "Aniss", "last": "Belkadi"},
            {"email": "lynda_kh@estin.dz", "username": "lynda_kh", "first": "Lynda", "last": "Khelifi"},
            {"email": "amine_hb@estin.dz", "username": "amine_hb", "first": "Amine", "last": "Habibi"},
            {"email": "sarah_hm@estin.dz", "username": "sarah_hm", "first": "Sarah", "last_name": "Hamidi"},
            {"email": "omar_fr@estin.dz", "username": "omar_fr", "first": "Omar", "last_name": "Farah"},
            {"email": "ryad_nc@estin.dz", "username": "ryad_nc", "first": "Ryad", "last_name": "Nacer"},
            {"email": "imene_ik@estin.dz", "username": "imene_ik", "first": "Imene", "last_name": "Ikhlef"},
            {"email": "sofiane_fk@estin.dz", "username": "sofiane_fk", "first": "Sofiane", "last_name": "Fekir"}
        ]
        
        with engine.connect() as conn:
            for u in users:
                print(f"Processing {u['email']}...")
                # 1. Clean existing
                conn.execute(text("DELETE FROM users WHERE email = :email OR username = :uname"), {"email": u["email"], "uname": u["username"]})
                
                # 2. Insert
                query = text("""
                    INSERT INTO users (email, username, hashed_password, first_name, last_name, is_admin, is_active, university)
                    VALUES (:email, :username, :hashed_password, :first_name, :last_name, :is_admin, :is_active, :university)
                """)
                
                conn.execute(query, {
                    "email": u["email"],
                    "username": u["username"],
                    "hashed_password": password,
                    "first_name": u["first"],
                    "last_name": u.get("last", u.get("last_name", "Student")),
                    "is_admin": False,
                    "is_active": True,
                    "university": "ESTIN"
                })
            conn.commit()
            print(f"SUCCESS! {len(users)} student accounts injected into production.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    seed()
