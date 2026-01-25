# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pathlib import Path
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, IntegrityError
from jose import JWTError
from app.core.cors import configure_cors, add_cors_debug_middleware

from app.routers import (
    upload, books, condition, ratings, notifications, auth, 
    wishlist, admin, recommendations, dashboard, messages, 
    curriculum  # NOUVEAU
)
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

add_cors_debug_middleware(app)  # optional, just for debugging
configure_cors(app)  # this applies your CORS settings

import app.models

# ===============================
# STARTUP
# ===============================

# Setup logging
setup_logging()

# Create all tables (one time, non-blocking if possible)
try:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
except Exception as e:
    print(f"Warning: Database initialization error: {e}")
    # Don't raise here, allow the app to try and start

# ===============================
# CREATE FASTAPI APP

# ===============================
app = FastAPI(
    title="DZ-Kitab API",
    version="2.1.2",  # Global cleaning fix
    description="API pour la plateforme d'change de livres universitaires avec systme de recommandations par cursus",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===============================
# ADD MIDDLEWARES
# ===============================
app.add_middleware(RequestLoggingMiddleware)

# ===============================
# CONFIGURE CORS (Must be added last to run first)
# ===============================
configure_cors(app)
add_cors_debug_middleware(app)

# ===============================
# REGISTER EXCEPTION HANDLERS
# ===============================

app.add_exception_handler(DZKitabException, dzkitab_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, operational_error_handler)
app.add_exception_handler(JWTError, jwt_error_handler)
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
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["User Dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(curriculum.router, prefix="/api/curriculum", tags=["Curriculum"])  # NOUVEAU

# ===============================
# ROOT ENDPOINTS
# ===============================

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur DZ-Kitab API!",
        "version": "2.1.0",
        "documentation": "/docs",
        "status": "operational",
        "features": [
            " Authentification JWT",
            " Upload d'images",
            " Intgration Google Books API",
            " Systme d'valuation de condition",
            " Systme de notation vendeurs",
            " Notifications en temps rel",
            " Suspension automatique",
            " Recommandations par domaine",
            " Web Scraping & Badges Cursus",  # NOUVEAU
            " Gestion d'erreurs avance",
            " CORS configur"
        ],
        "endpoints": {
            "auth": "/auth/*",
            "books": "/api/books/*",
            "images": "/api/images/*",
            "condition": "/api/condition/*",
            "ratings": "/api/ratings/*",
            "notifications": "/api/notifications/*",
            "wishlist": "/api/wishlist/*",
            "admin": "/api/admin/*", 
            "recommendations": "/api/recommendations/*",
            "curriculum": "/api/curriculum/*"  # NOUVEAU
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    from app.database import SessionLocal
    
    db_status = "connected"
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "version": "2.1.2",
        "timestamp": time.time()
    }

@app.get("/stats")
def get_stats():
    """Get API statistics (public)"""
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.book import Announcement
    from app.models.rating import Rating
    from app.models.curriculum import Curriculum
    
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_announcements = db.query(Announcement).count()
        active_announcements = db.query(Announcement).filter(
            Announcement.status == "Active"
        ).count()
        total_ratings = db.query(Rating).count()
        total_curriculums = db.query(Curriculum).count()
        
        return {
            "total_users": total_users,
            "total_announcements": total_announcements,
            "active_announcements": active_announcements,
            "total_ratings": total_ratings,
            "total_curriculums": total_curriculums
        }
    finally:
        db.close()

# ===============================
# STARTUP/SHUTDOWN EVENTS
# ===============================

@app.on_event("startup")
async def startup_event():
    """Actions au dmarrage de l'application"""
    print("=" * 60)
    print("DZ-Kitab API Started Successfully!")
    print("=" * 60)
    print(f"Documentation: http://localhost:8000/docs")
    print(f"Health Check: http://localhost:8000/health")
    print(f"Statistics: http://localhost:8000/stats")
    print(f"Recommendations: http://localhost:8000/api/recommendations/test")
    print(f"Curriculum: http://localhost:8000/api/curriculum/test")  # NOUVEAU
    print("=" * 60)
    
@app.on_event("shutdown")
async def shutdown_event():
    """Actions  l'arrt de l'application"""
    print("\n" + "=" * 60)
    print("DZ-Kitab API Shutting Down...")
    print("=" * 60)

print("Application ready! Access: http://localhost:8000/docs")
