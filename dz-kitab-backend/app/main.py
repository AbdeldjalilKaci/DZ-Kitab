 # app/main.py

import os
import sys
from pathlib import Path
import time

# ===============================
# Ensure BASE_DIR is in sys.path
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ===============================
# FastAPI Imports
# ===============================
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from jose import JWTError

# ===============================
# App-specific imports
# ===============================
from app.database import engine, Base, SessionLocal
from app.core.errors import (
    dzkitab_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    operational_error_handler,
    jwt_error_handler,
    general_exception_handler,
    DZKitabException
)
from app.routers import (
    books, condition, ratings, notifications, auth,
    wishlist, admin, recommendations, dashboard, messages, curriculum, users
)

# ===============================
# CREATE FASTAPI APP
# ===============================
app = FastAPI(
    title="DZ-Kitab API",
    version="2.1.21",
    description="API for DZ-Kitab - Production Fix 2.1.21 (Vercel)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===============================
# CORS CONFIGURATION
# ===============================
origins = [
    "https://dz-kitab-frontend.vercel.app",  # production frontend
    "https://dz-kitab-frontend-production.up.railway.app", # Railway production frontend
    "https://dz-backend-fix.vercel.app",     # production backend (self)
    "http://localhost:3000",                 # optional dev frontend
    "http://localhost:5173",                 # Vite default
    "http://127.0.0.1:5173",                 # Vite default (IP)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
if Path("uploads").exists():
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ===============================
# INCLUDE ROUTERS
# ===============================
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(books.router, prefix="/api/books", tags=["Books & Announcements"])
app.include_router(condition.router, prefix="/api/condition", tags=["Book Condition"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(wishlist.router, prefix="/api/wishlist", tags=["Wishlist"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["User Dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(curriculum.router, prefix="/api/curriculum", tags=["Curriculum"])
app.include_router(users.router, prefix="/api/public/users", tags=["Public Users"])

# ===============================
# ROOT & HEALTH ENDPOINTS
# ===============================
@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur DZ-Kitab API!",
        "version": "2.1.20",
        "target": "production"
    }

@app.get("/health")
def health_check():
    db_status = "connected"
    tables = {}
    db_host = "unknown"
    try:
        db_host = engine.url.host
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        # Check critical tables
        for table in ["users", "announcements", "books"]:
            try:
                db.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                tables[table] = "exists"
            except Exception:
                tables[table] = "missing"
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" and all(v == "exists" for v in tables.values()) else "unhealthy",
        "database": db_status,
        "database_host": db_host,
        "tables": tables,
        "timestamp": time.time(),
        "version": "2.1.24"
    }

@app.get("/api/debug/create-admin")
def create_admin_debug():
    from app.models.user import User
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        email = "admin@dz-kitab.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Creation if it really doesn't exist
            user = User(
                email=email,
                username="admin",
                hashed_password="Admin.com2026",
                is_admin=True,
                is_active=True,
                first_name="Admin",
                last_name="DZ-Kitab"
            )
            db.add(user)
            db.commit()
            return {"status": "created", "email": email}
        else:
            # Promotion if it exists
            user.is_admin = True
            user.hashed_password = "Admin.com2026"
            db.commit()
            return {"status": "updated_to_admin", "email": email}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

# ===============================
# STARTUP LOG
# ===============================
print("INFO: Startup complete (v2.1.20).")
