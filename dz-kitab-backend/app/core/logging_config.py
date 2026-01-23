# app/core/logging_config.py

import logging
import sys
from datetime import datetime
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import time
import json

# ============================================
# CONFIGURATION DU LOGGER
# ============================================

def setup_logging():
    """
    Configurer le système de logging
    """
    # Créer le dossier logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Format du log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configuration du logger racine
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler - tous les logs
            logging.FileHandler(
                log_dir / f"dzkitab_{datetime.now().strftime('%Y%m%d')}.log"
            ),
            # File handler - erreurs seulement
            logging.FileHandler(
                log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
            )
        ]
    )
    
    # Configurer le niveau pour le handler d'erreurs
    error_handler = logging.getLogger().handlers[2]
    error_handler.setLevel(logging.ERROR)
    
    # Logger spécifiques
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    print(f"✅ Logging configuré - Dossier: {log_dir.absolute()}")

# ============================================
# MIDDLEWARE DE LOGGING
# ============================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour logger toutes les requêtes et réponses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Générer un ID de requête unique
        request_id = f"{int(time.time() * 1000)}"
        request.state.request_id = request_id
        
        # Enregistrer le début de la requête
        start_time = time.time()
        
        # Logs de la requête
        logger = logging.getLogger("api.requests")
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        # Logs des headers (en développement seulement)
        import os
        if os.getenv("ENVIRONMENT") == "development":
            logger.debug(f"[{request_id}] Headers: {dict(request.headers)}")
        
        try:
            response = await call_next(request)
            
            # Calculer le temps de traitement
            process_time = time.time() - start_time
            
            # Logs de la réponse
            logger.info(
                f"[{request_id}] Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Ajouter des headers de tracking
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as exc:
            # Logger l'erreur
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Error: {type(exc).__name__} - "
                f"Message: {str(exc)} - Time: {process_time:.3f}s",
                exc_info=True
            )
            raise

# ============================================
# LOGGER D'ERREURS STRUCTURÉ
# ============================================

class ErrorLogger:
    """
    Logger d'erreurs structuré pour une meilleure analyse
    """
    
    def __init__(self):
        self.logger = logging.getLogger("api.errors")
        self.error_log_file = Path("logs") / "errors_structured.jsonl"
    
    def log_error(
        self,
        error_type: str,
        message: str,
        request: Request = None,
        status_code: int = 500,
        stack_trace: str = None,
        extra_data: dict = None
    ):
        """
        Logger une erreur de manière structurée
        """
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type,
            "message": message,
            "status_code": status_code,
        }
        
        # Informations sur la requête
        if request:
            error_data["request"] = {
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_id": getattr(request.state, "request_id", None)
            }
        
        # Stack trace
        if stack_trace:
            error_data["stack_trace"] = stack_trace
        
        # Données supplémentaires
        if extra_data:
            error_data["extra"] = extra_data
        
        # Logger en JSON pour une analyse facile
        self.logger.error(json.dumps(error_data, ensure_ascii=False))
        
        # Écrire aussi dans un fichier JSON Lines
        try:
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_data, ensure_ascii=False) + "\n")
        except Exception as e:
            self.logger.error(f"Impossible d'écrire dans le fichier de log: {e}")

# Instance globale
error_logger = ErrorLogger()

# ============================================
# DECORATEUR POUR LOGGER LES EXCEPTIONS
# ============================================

from functools import wraps
import traceback

def log_exceptions(func):
    """
    Décorateur pour logger automatiquement les exceptions
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            # Logger l'exception
            logger = logging.getLogger(func.__module__)
            logger.error(
                f"Exception in {func.__name__}: {type(exc).__name__} - {str(exc)}",
                exc_info=True
            )
            
            # Logger de manière structurée
            error_logger.log_error(
                error_type=type(exc).__name__,
                message=str(exc),
                stack_trace=traceback.format_exc(),
                extra_data={
                    "function": func.__name__,
                    "module": func.__module__
                }
            )
            
            raise
    
    return wrapper
