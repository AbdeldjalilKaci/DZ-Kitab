import os
import sys
from sqlalchemy import create_engine

# Add app directory to path
sys.path.append('c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend')

from app.database import Base
from app.models.user import User
from app.models.book import Book, Announcement
from app.models.message import Message, Conversation
from app.models.notification import Notification
from app.models.rating import Rating
from app.models.wishlist import Wishlist

# DATABASE_URL from user's neon string
DATABASE_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

try:
    print(f"Connecting to Neon and creating tables...")
    engine = create_engine(DATABASE_URL)
    # Import all models to ensure they are registered with Base.metadata
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: All tables created in Neon!")
except Exception as e:
    print(f"FAILED: Could not create tables: {e}")
