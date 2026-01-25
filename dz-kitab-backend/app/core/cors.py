# app/core/cors.py

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from typing import List

def get_allowed_origins() -> List[str]:
    """
    Rcuprer les origines autorises selon l'environnement
    """
    environment = os.getenv("ENVIRONMENT", "development")
    allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "")
    
    # Base origins toujours autorisables (Vercel Frontend)
    base_origins = [
        "https://dz-kitab-frontend.vercel.app",
        "https://dz-kitab-frontend-abdeldjalil-kacis-projects.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ]
    
    if environment == "production":
        # En production, utiliser les domaines configurs + base_origins
        origins = allowed_origins_raw.split(",")
        result = [origin.strip() for origin in origins if origin.strip()]
        
        # Ajouter les domaines Vercel par dfaut si non prsents
        for bo in base_origins:
            if bo not in result:
                result.append(bo)
        
        return result
    else:
        # En dveloppement, autoriser localhost ET les domaines de prod pour faciliter les tests
        return base_origins + [
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]


def configure_cors(app: FastAPI) -> None:
    """
    Configurer CORS pour l'application FastAPI
    
    Configuration adapte selon l'environnement:
    - Development: Permissif pour faciliter le dveloppement
    - Production: Restrictif pour la scurit
    """
    
    allowed_origins = get_allowed_origins()
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Configuration CORS
    cors_config = {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
        ],
        "expose_headers": [
            "Content-Length",
            "Content-Range",
            "X-Total-Count",
        ],
        "max_age": 600,  # 10 minutes de cache pour les preflight
    }
    
    # En production, ajouter des headers de scurit supplmentaires
    if environment == "production":
        cors_config["expose_headers"].extend([
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ])
    
    app.add_middleware(CORSMiddleware, **cors_config)
    
    print(f" CORS configur pour l'environnement: {environment}")
    print(f" Origines autorises: {allowed_origins}")

# ============================================
# MIDDLEWARE PERSONNALIS POUR DEBUG CORS
# ============================================

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour debugger les problmes CORS en dveloppement
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log des requtes OPTIONS (preflight)
        if request.method == "OPTIONS":
            origin = request.headers.get("origin", "No origin")
            print(f" CORS Preflight: {request.method} {request.url.path}")
            print(f"   Origin: {origin}")
            print(f"   Headers: {dict(request.headers)}")
        
        response = await call_next(request)
        
        # En dveloppement, log des headers CORS dans la rponse
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "development" and request.method == "OPTIONS":
            print(f" CORS Response headers:")
            cors_headers = {k: v for k, v in response.headers.items() if "access-control" in k.lower()}
            for key, value in cors_headers.items():
                print(f"   {key}: {value}")
        
        return response

def add_cors_debug_middleware(app: FastAPI) -> None:
    """
    Ajouter le middleware de debug CORS en dveloppement
    """
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development":
        app.add_middleware(CORSDebugMiddleware)
        print(" CORS Debug Middleware activ")
