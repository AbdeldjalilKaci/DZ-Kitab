# app/core/cors.py

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from typing import List

def get_allowed_origins() -> List[str]:
    """
    Récupérer les origines autorisées selon l'environnement
    """
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        # En production, utiliser uniquement les domaines configurés
        origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
        return [origin.strip() for origin in origins if origin.strip()]
    else:
        # En développement, autoriser localhost et 127.0.0.1
        return [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://0.0.0.0:3000",
            "http://0.0.0.0:5173",
        ]

def configure_cors(app: FastAPI) -> None:
    """
    Configurer CORS pour l'application FastAPI
    
    Configuration adaptée selon l'environnement:
    - Development: Permissif pour faciliter le développement
    - Production: Restrictif pour la sécurité
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
    
    # En production, ajouter des headers de sécurité supplémentaires
    if environment == "production":
        cors_config["expose_headers"].extend([
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ])
    
    app.add_middleware(CORSMiddleware, **cors_config)
    
    print(f"✅ CORS configuré pour l'environnement: {environment}")
    print(f"📋 Origines autorisées: {allowed_origins}")

# ============================================
# MIDDLEWARE PERSONNALISÉ POUR DEBUG CORS
# ============================================

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour debugger les problèmes CORS en développement
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log des requêtes OPTIONS (preflight)
        if request.method == "OPTIONS":
            origin = request.headers.get("origin", "No origin")
            print(f"🔍 CORS Preflight: {request.method} {request.url.path}")
            print(f"   Origin: {origin}")
            print(f"   Headers: {dict(request.headers)}")
        
        response = await call_next(request)
        
        # En développement, log des headers CORS dans la réponse
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "development" and request.method == "OPTIONS":
            print(f"✅ CORS Response headers:")
            cors_headers = {k: v for k, v in response.headers.items() if "access-control" in k.lower()}
            for key, value in cors_headers.items():
                print(f"   {key}: {value}")
        
        return response

def add_cors_debug_middleware(app: FastAPI) -> None:
    """
    Ajouter le middleware de debug CORS en développement
    """
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development":
        app.add_middleware(CORSDebugMiddleware)
        print("🔍 CORS Debug Middleware activé")
