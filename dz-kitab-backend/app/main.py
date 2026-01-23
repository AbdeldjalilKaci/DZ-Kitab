# app/main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pathlib import Path
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, IntegrityError
from jose import JWTError

from app.routers import upload, books, condition, ratings, notifications, auth, wishlist
from app.database import engine, Base, DATABASE_URL
from app.core.errors import (
    dzkitab_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    operational_error_handler,
    jwt_error_handler,
    general_exception_handler,
    DZKitabException
)
from app.core.cors import configure_cors, add_cors_debug_middleware
from app.core.logging_config import setup_logging, RequestLoggingMiddleware
import app.models

# ===============================
# WAIT FOR DATABASE
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

# Wait for database
wait_for_db(DATABASE_URL)

print("🚀 Starting application...")

# Setup logging
setup_logging()

# Create all tables
Base.metadata.create_all(bind=engine)

# ===============================
# CREATE FASTAPI APP
# ===============================
app = FastAPI(
    title="DZ-Kitab API",
    version="2.0.0",
    description="API pour la plateforme d'échange de livres universitaires",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===============================
# CONFIGURE CORS
# ===============================
configure_cors(app)
add_cors_debug_middleware(app)

# ===============================
# ADD MIDDLEWARES
# ===============================
app.add_middleware(RequestLoggingMiddleware)

# ===============================
# REGISTER EXCEPTION HANDLERS
# ===============================

# Nos exceptions personnalisées
app.add_exception_handler(DZKitabException, dzkitab_exception_handler)

# Exceptions FastAPI/Pydantic
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Exceptions SQLAlchemy
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, operational_error_handler)

# Exceptions JWT
app.add_exception_handler(JWTError, jwt_error_handler)

# Exception générale (catch-all)
app.add_exception_handler(Exception, general_exception_handler)

# ===============================
# STATIC FILES
# ===============================
Path("uploads/books").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ===============================
# INCLUDE ROUTERS
# ===============================
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/images", tags=["Images"])
app.include_router(books.router, prefix="/api/books", tags=["Books & Announcements"])
app.include_router(condition.router, prefix="/api/condition", tags=["Book Condition"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(wishlist.router, prefix="/api/wishlist", tags=["Wishlist"])

# ===============================
# ROOT ENDPOINTS
# ===============================

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur DZ-Kitab API!",
        "version": "2.0.0",
        "documentation": "/docs",
        "status": "operational",
        "features": [
            "✅ Authentification JWT",
            "✅ Upload d'images",
            "✅ Intégration Google Books API",
            "✅ Système d'évaluation de condition",
            "✅ Système de notation vendeurs",
            "✅ Notifications en temps réel",
            "✅ Suspension automatique",
            "✅ Gestion d'erreurs avancée",
            "✅ CORS configuré"
        ],
        "endpoints": {
            "auth": "/auth/*",
            "books": "/api/books/*",
            "images": "/api/images/*",
            "condition": "/api/condition/*",
            "ratings": "/api/ratings/*",
            "notifications": "/api/notifications/*",
            "wishlist": "/api/wishlist/*"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    from app.database import SessionLocal
    
    db_status = "connected"
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.get("/stats")
def get_stats():
    """Get API statistics (public)"""
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.book import Announcement
    from app.models.rating import Rating
    
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_announcements = db.query(Announcement).count()
        active_announcements = db.query(Announcement).filter(
            Announcement.status == "Active"
        ).count()
        total_ratings = db.query(Rating).count()
        
        return {
            "total_users": total_users,
            "total_announcements": total_announcements,
            "active_announcements": active_announcements,
            "total_ratings": total_ratings
        }
    finally:
        db.close()

# ===============================
# STARTUP/SHUTDOWN EVENTS
# ===============================

@app.on_event("startup")
async def startup_event():
    """Actions au démarrage de l'application"""
    print("=" * 60)
    print("🎉 DZ-Kitab API Started Successfully!")
    print("=" * 60)
    print(f"📝 Documentation: http://localhost:8000/docs")
    print(f"🔍 Health Check: http://localhost:8000/health")
    print(f"📊 Statistics: http://localhost:8000/stats")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Actions à l'arrêt de l'application"""
    print("\n" + "=" * 60)
    print("👋 DZ-Kitab API Shutting Down...")
    print("=" * 60)

print("✅ Application ready! Access: http://localhost:8000/docs")
