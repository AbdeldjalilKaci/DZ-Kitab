import os
import sys
import traceback
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal, engine, Base
from app.models.book import Book, Announcement, BookCategoryEnum, BookConditionEnum, AnnouncementStatusEnum
from app.models.user import User, UniversityEnum
from app.services.auth import get_password_hash
from sqlalchemy import text

def refresh():
    # Ensure tables exist
    print("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # 1. NUCLEAR CLEANUP
        print("Starting Nuclear Database Cleanup...")
        tables_to_clear = [
            "wishlist", "favorites", "ratings", "book_condition_scores", 
            "notifications", "notification_preferences", "messages", 
            "announcements", "books", "seller_stats", "rating_alerts",
            "user_suspensions", "users"
        ]
        for table in tables_to_clear:
            try:
                print(f"Clearing table: {table}")
                session.execute(text(f"DELETE FROM {table}"))
                session.commit() # Commit each table deletion to avoid rollback issues
            except Exception as e:
                print(f"Warning: Could not clear table {table}: {e}")
                session.rollback()
                continue
        
        print("Database cleared successfully.")

        # 2. CREATE REQUESTED USERS
        print("Creating requested users (1 Admin + 10 Students)...")
        # Admin Password: Admin.com2026
        admin_pw = get_password_hash("Admin.com2026")
        # Normal User Password: User.com2026
        user_pw = get_password_hash("User.com2026")
        
        user_data = [
            # The requested Admin account
            {"email": "admin@dz-kitab.com", "username": "admin", "first_name": "DZ-Kitab", "last_name": "Admin", "university": UniversityEnum.ESTIN, "is_admin": True, "pw": admin_pw},
            
            # 10 Normal users
            {"email": "djalil_st@estin.dz", "username": "djalil_st", "first_name": "Djalil", "last_name": "Student", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "meriem_dz@estin.dz", "username": "meriem", "first_name": "Meriem", "last_name": "Lounis", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "aniss_bk@estin.dz", "username": "aniss", "first_name": "Aniss", "last_name": "Belkadi", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "lynda_kh@estin.dz", "username": "lynda", "first_name": "Lynda", "last_name": "Khelifi", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "amine_hb@estin.dz", "username": "amine", "first_name": "Amine", "last_name": "Habibi", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "sarah_hm@estin.dz", "username": "sarah", "first_name": "Sarah", "last_name": "Hamidi", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "omar_fr@estin.dz", "username": "omar", "first_name": "Omar", "last_name": "Farah", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "ryad_nc@estin.dz", "username": "ryad", "first_name": "Ryad", "last_name": "Nacer", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "imene_ik@estin.dz", "username": "imene", "first_name": "Imene", "last_name": "Ikhlef", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw},
            {"email": "sofiane_fk@estin.dz", "username": "sofiane", "first_name": "Sofiane", "last_name": "Fekir", "university": UniversityEnum.ESTIN, "is_admin": False, "pw": user_pw}
        ]

        created_users = []
        for u_info in user_data:
            user = User(
                email=u_info["email"],
                username=u_info["username"],
                hashed_password=u_info["pw"],
                first_name=u_info["first_name"],
                last_name=u_info["last_name"],
                university=u_info["university"],
                is_admin=u_info["is_admin"],
                is_active=True
            )
            session.add(user)
            session.flush()
            created_users.append(user)
            print(f"Created user: {u_info['email']}")

        # 3. SEED PROFESSIONAL ANNOUNCEMENTS
        print("Seeding announcements...")
        seed_data = {
            BookCategoryEnum.INFORMATIQUE: [
                {"title": "Clean Code", "isbn": "9780132350884", "authors": "Robert C. Martin", "description": "A Handbook of Agile Software Craftsmanship", "price": 4500},
                {"title": "Introduction to Algorithms", "isbn": "9780262033848", "authors": "Thomas H. Cormen", "description": "The standard reference for algorithms.", "price": 8500},
                {"title": "The Pragmatic Programmer", "isbn": "9780135957059", "authors": "Andrew Hunt, David Thomas", "description": "Your journey to mastery.", "price": 5000}
            ],
            BookCategoryEnum.PHYSIQUE: [
                {"title": "The Feynman Lectures on Physics", "isbn": "9780465024147", "authors": "Richard Feynman", "description": "The most famous textbook in physics.", "price": 12000},
                {"title": "University Physics", "isbn": "9780321973610", "authors": "Young and Freedman", "description": "Comprehensive physics textbook.", "price": 9500}
            ],
            BookCategoryEnum.MATHEMATIQUES: [
                {"title": "Calculus", "isbn": "9781285740621", "authors": "James Stewart", "description": "Standard calculus text.", "price": 7500},
                {"title": "Linear Algebra Done Right", "isbn": "9783319110790", "authors": "Sheldon Axler", "description": "Deep dive into linear algebra.", "price": 4000}
            ],
            BookCategoryEnum.MEDECINE: [
                {"title": "Gray's Anatomy", "isbn": "9780702052309", "authors": "Susan Standring", "description": "The anatomical basis of clinical practice.", "price": 15000},
                {"title": "Harrison's Principles of Internal Medicine", "isbn": "9781259644030", "authors": "Dennis Kasper", "description": "Leading internal medicine guide.", "price": 18000}
            ],
            BookCategoryEnum.ECONOMIE: [
                {"title": "Capital in the Twenty-First Century", "isbn": "9780674430006", "authors": "Thomas Piketty", "description": "Analysis of wealth and income inequality.", "price": 3500},
                {"title": "Economics", "isbn": "9781260225587", "authors": "Paul Samuelson", "description": "Foundation of modern economics.", "price": 6000}
            ]
        }

        # Distribute books among created users
        user_idx = 0
        for category, books_list in seed_data.items():
            for item in books_list:
                # Create Book
                book = Book(
                    isbn=item["isbn"],
                    title=item["title"],
                    authors=item["authors"],
                    description=item["description"],
                    cover_image_url=f"https://covers.openlibrary.org/b/isbn/{item['isbn']}-L.jpg",
                    language="fr",
                    categories=category.value
                )
                session.add(book)
                session.flush()

                # Pick a user
                owner = created_users[user_idx % len(created_users)]
                user_idx += 1

                # Create Announcement
                ann = Announcement(
                    book_id=book.id,
                    user_id=owner.id,
                    price=item["price"],
                    market_price=item["price"] + 1000,
                    condition=BookConditionEnum.BON_ETAT,
                    category=category,
                    status=AnnouncementStatusEnum.ACTIVE,
                    description=f"Authentic copy of {item['title']} - perfect for ESTIN students.",
                    location="Sidi Abdellah, Alger"
                )
                session.add(ann)

        session.commit()
        print("Professional data refresh complete!")

    except Exception as e:
        print(f"Error during refresh: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    refresh()
