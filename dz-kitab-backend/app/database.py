# # app/database.py

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# import os
# from dotenv import load_dotenv

# # Charger les variables d'environnement
# load_dotenv()

# # URL de connexion - Support SQLite par défaut pour le développement local facile
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dzkitab.db")

# # Créer le moteur SQLAlchemy
# if DATABASE_URL.startswith("sqlite"):
#     engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# else:
#     engine = create_engine(DATABASE_URL)


# # Créer une session locale
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base pour les modèles
# Base = declarative_base()

# # Dépendance pour obtenir la session DB
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

# Charger les variables d'environnement
load_dotenv()

# MySQL connection details (InfinityFree)
DB_USER = "if0_40781999"
DB_PASSWORD = "ZElY0rtAdL"
DB_NAME = "if0_40781999_dz_kitab"  # Replace XXX with your actual DB name
DB_HOST = "sql312.infinityfree.com"
DB_PORT = "3306"

# URL de connexion MySQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Créer le moteur SQLAlchemy
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Créer une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

