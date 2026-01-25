import os
import sys
from sqlalchemy import create_engine, inspect

# Add app directory to path
sys.path.append('c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend')

# DATABASE_URL from user's neon string
DATABASE_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("--- TABLES IN NEON ---")
    if not tables:
        print("No tables found!")
    else:
        for table in tables:
            print(f"- {table}")
except Exception as e:
    print(f"Error connecting to database: {e}")
