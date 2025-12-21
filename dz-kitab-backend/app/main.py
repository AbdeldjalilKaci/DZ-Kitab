# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pathlib import Path
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.database import engine, Base, get_db, DATABASE_URL
from app.models.user import User
from app.models.book import Book, Announcement
from app.models.book_condition import BookConditionScore  # Nouveau modèle
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.middleware.auth import security
from app.services.auth import create_user_token, verify_password, get_password_hash
from app.routers import upload, books, condition  # Nouveau router

# ===============================
# ATTENDRE QUE LA DB SOIT PRÊTE
# ===============================
def wait_for_db(database_url: str, retries: int = 10, delay: int = 3):
    temp_engine = create_engine(database_url)
    for i in range(retries):
        try:
            with temp_engine.connect():
                print("✅ Database is ready!")
                return
        except OperationalError:
            print(f"⏳ Waiting for DB... attempt {i + 1}/{retries}")
            time.sleep(delay)
    raise Exception("❌ Database not available after several retries.")

# Appel de la fonction avant de créer les tables
wait_for_db(DATABASE_URL)

print("🚀 Démarrage de l'application...")

# Créer toutes les tables (users, books, announcements)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DZ-Kitab API",
    version="1.0.0",
    description="API pour la plateforme d'échange de livres universitaires"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Créer le dossier uploads s'il n'existe pas
Path("uploads/books").mkdir(parents=True, exist_ok=True)

# Servir les fichiers statiques
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Inclure les routers
app.include_router(upload.router, prefix="/api/images", tags=["Images"])
app.include_router(books.router, prefix="/api/books", tags=["Books & Announcements"])
app.include_router(condition.router, prefix="/api/condition", tags=["Book Condition Evaluation"])

# ============================================
# ROUTES PUBLIQUES
# ============================================

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur DZ-Kitab API!",
        "version": "1.0.0",
        "features": [
            "Authentification JWT",
            "Upload d'images",
            "Intégration Google Books API",
            "Gestion des annonces de livres"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

@app.post("/auth/register", response_model=dict)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    try:
        print(f"📧 Tentative d'inscription: {user_data.email}")
        
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email ou nom d'utilisateur déjà utilisé"
            )
        
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            university=user_data.university,
            phone_number=user_data.phone_number
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Utilisateur créé: {user.id}")
        return {
            "message": "Utilisateur créé avec succès",
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erreur serveur: {str(e)}"
        )

@app.post("/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Connexion utilisateur"""
    try:
        print(f"🔐 Tentative de connexion: {credentials.email}")
        
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )
        
        access_token = create_user_token(user.id, user.email)
        
        print(f"✅ Connexion réussie: {user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "university": user.university.value if user.university else None,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "created_at": str(user.created_at),
                "updated_at": str(user.updated_at) if user.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la connexion"
        )

# ============================================
# ROUTES PROTÉGÉES
# ============================================

@app.get("/auth/me", response_model=UserResponse)
def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    """Récupérer les informations de l'utilisateur connecté"""
    try:
        from app.services.jwt import verify_token
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
        
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "university": user.university.value if user.university else None,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "created_at": str(user.created_at),
            "updated_at": str(user.updated_at) if user.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        )

@app.get("/profile")
def get_profile(token: str = Depends(security), db: Session = Depends(get_db)):
    """Profil utilisateur"""
    from app.services.jwt import verify_token
    payload = verify_token(token)
    user = db.query(User).filter(User.email == payload.get("sub")).first()
    
    return {
        "message": "Profil utilisateur",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "university": user.university.value if user.university else None,
            "phone_number": user.phone_number
        }
    }

print("✅ Application prête! Accédez à: http://localhost:8000/docs")