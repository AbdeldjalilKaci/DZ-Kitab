# # app/database.py

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# import os
# from dotenv import load_dotenv

# # Charger les variables d'environnement
# load_dotenv()

# # URL de connexion - Support SQLite par dfaut pour le dveloppement local facile
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dzkitab.db")

# # Crer le moteur SQLAlchemy
# if DATABASE_URL.startswith("sqlite"):
#     engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# else:
#     engine = create_engine(DATABASE_URL)


# # Crer une session locale
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base pour les modles
# Base = declarative_base()

# # Dpendance pour obtenir la session DB
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

# Charger les variables d'environnement seulement en dveloppement
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

# URL de connexion - Priorit absolue  la variable d'environnement
# URL de connexion - Priorit absolue  la variable d'environnement
DATABASE_URL = os.getenv("DATABASE_URL")

# Nettoyage prventif de l'URL (suppression des \r et espaces)
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip().replace("\r", "").replace("\n", "")

# Fallback ULTIME pour la production si les variables d'environnement chouent
if not DATABASE_URL and os.getenv("ENVIRONMENT") == "production":
    DATABASE_URL = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
    print("WARNING: Using hardcoded production fallback for DATABASE_URL")

# Fallback pour le dveloppement local seulement
if not DATABASE_URL:
    # MySQL connection details (InfinityFree) - Backup defaults
    DB_USER = "if0_40781999"
    DB_PASSWORD = "ZElY0rtAdL"
    DB_NAME = "if0_40781999_dz_kitab"
    DB_HOST = "sql312.infinityfree.com"
    DB_PORT = "3306"
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"DEBUG: STARTUP DATABASE CONFIG")
print(f"DEBUG: Environment: {os.getenv('ENVIRONMENT')}")
print(f"DEBUG: Has DATABASE_URL env var: {bool(os.getenv('DATABASE_URL'))}")
print(f"DEBUG: Final DATABASE_URL type: {'Postgres' if 'postgres' in DATABASE_URL.lower() else 'Other'}")




# Crer le moteur SQLAlchemy
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Crer une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modles
Base = declarative_base()

# Dpendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

