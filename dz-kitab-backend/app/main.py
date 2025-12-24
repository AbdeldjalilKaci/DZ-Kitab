# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.routers import upload, books, condition, ratings, notifications, auth
from app.database import engine, Base, DATABASE_URL

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

# Create all tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="DZ-Kitab API",
    version="2.0.0",
    description="API pour la plateforme d'échange de livres universitaires",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
Path("uploads/books").mkdir(parents=True, exist_ok=True)

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers - IMPORTANT: auth router is included here!
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/images", tags=["Images"])
app.include_router(books.router, prefix="/api/books", tags=["Books & Announcements"])
app.include_router(condition.router, prefix="/api/condition", tags=["Book Condition"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur DZ-Kitab API!",
        "version": "2.0.0",
        "documentation": "/docs",
        "features": [
            "✅ Authentification JWT",
            "✅ Upload d'images",
            "✅ Intégration Google Books API",
            "✅ Système d'évaluation de condition",
            "✅ Système de notation vendeurs",
            "✅ Notifications en temps réel",
            "✅ Suspension automatique",
            "✅ Multi-critères de recherche"
        ],
        "endpoints": {
            "auth": "/auth/*",
            "books": "/api/books/*",
            "images": "/api/images/*",
            "condition": "/api/condition/*",
            "ratings": "/api/ratings/*",
            "notifications": "/api/notifications/*"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "2.0.0"
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

print("✅ Application ready! Access: http://localhost:8000/docs")
