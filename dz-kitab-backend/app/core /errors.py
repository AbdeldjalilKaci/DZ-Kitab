# app/core/errors.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
from jose import JWTError
import traceback
from typing import Union
from app.core.logging_config import error_logger
# ============================================
# CUSTOM EXCEPTIONS
# ============================================

class DZKitabException(Exception):
    """Base exception pour DZ-Kitab"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFoundError(DZKitabException):
    """Ressource non trouvée"""
    def __init__(self, resource: str, resource_id: Union[int, str]):
        message = f"{resource} avec l'ID {resource_id} non trouvé(e)"
        super().__init__(message, status_code=404)

class UnauthorizedError(DZKitabException):
    """Non autorisé"""
    def __init__(self, message: str = "Non autorisé"):
        super().__init__(message, status_code=401)

class ForbiddenError(DZKitabException):
    """Accès interdit"""
    def __init__(self, message: str = "Accès interdit"):
        super().__init__(message, status_code=403)

class ValidationError(DZKitabException):
    """Erreur de validation"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class DatabaseError(DZKitabException):
    """Erreur de base de données"""
    def __init__(self, message: str = "Erreur de base de données"):
        super().__init__(message, status_code=500)

class ExternalServiceError(DZKitabException):
    """Erreur de service externe (Google Books, etc.)"""
    def __init__(self, service: str, message: str = None):
        default_message = f"Le service {service} est temporairement indisponible"
        super().__init__(message or default_message, status_code=503)

# ============================================
# ERROR HANDLERS
# ============================================

async def dzkitab_exception_handler(request: Request, exc: DZKitabException):
    """Gestionnaire pour nos exceptions personnalisées"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": exc.__class__.__name__,
                "message": exc.message,
                "path": str(request.url.path),
                "method": request.method
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gestionnaire pour les erreurs de validation Pydantic"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "type": "ValidationError",
                "message": "Erreur de validation des données",
                "details": errors,
                "path": str(request.url.path)
            }
        }
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Gestionnaire pour les erreurs d'intégrité SQL"""
    error_msg = str(exc.orig)
    
    # Détecter les types d'erreurs courants
    if "unique constraint" in error_msg.lower():
        message = "Cette valeur existe déjà dans la base de données"
        if "email" in error_msg.lower():
            message = "Cet email est déjà utilisé"
        elif "username" in error_msg.lower():
            message = "Ce nom d'utilisateur est déjà pris"
    elif "foreign key constraint" in error_msg.lower():
        message = "Référence invalide vers une ressource inexistante"
    elif "not null constraint" in error_msg.lower():
        message = "Champ requis manquant"
    else:
        message = "Erreur de contrainte de base de données"
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": {
                "type": "IntegrityError",
                "message": message,
                "path": str(request.url.path)
            }
        }
    )

async def operational_error_handler(request: Request, exc: OperationalError):
    """Gestionnaire pour les erreurs opérationnelles SQL"""
    print(f"❌ Database operational error: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "error": {
                "type": "DatabaseError",
                "message": "Service de base de données temporairement indisponible",
                "path": str(request.url.path)
            }
        }
    )

async def jwt_error_handler(request: Request, exc: JWTError):
    """Gestionnaire pour les erreurs JWT"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "error": {
                "type": "AuthenticationError",
                "message": "Token invalide ou expiré",
                "path": str(request.url.path)
            }
        },
        headers={"WWW-Authenticate": "Bearer"}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Gestionnaire pour toutes les autres exceptions"""
    # Log complet de l'erreur
    error_traceback = traceback.format_exc()
    try:
        error_logger.log_error(
            error_type=type(exc).__name__,
            message=str(exc),
            stack_trace=error_traceback,
            extra_data={
                "path": str(request.url.path),
                "method": request.method,
                "client": request.client.host if request.client else "unknown"
            }
        )
    except Exception as log_error:
        print(f"⚠️ Erreur lors de l'écriture du log: {log_error}")
    print(f"❌ Unhandled exception: {type(exc).__name__}")
    print(f"Message: {str(exc)}")
    print(f"Traceback:\n{error_traceback}")
    
    # En production, ne pas exposer les détails
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "Une erreur interne s'est produite",
                "path": str(request.url.path)
            }
        }
    )

# ============================================
# RESPONSE HELPERS
# ============================================

def success_response(data: any, message: str = None, status_code: int = 200):
    """Générer une réponse de succès standardisée"""
    response = {
        "success": True,
        "data": data
    }
    if message:
        response["message"] = message
    
    return JSONResponse(
        status_code=status_code,
        content=response
    )

def error_response(message: str, status_code: int = 400, details: any = None):
    """Générer une réponse d'erreur standardisée"""
    response = {
        "success": False,
        "error": {
            "message": message
        }
    }
    if details:
        response["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=response
    )
