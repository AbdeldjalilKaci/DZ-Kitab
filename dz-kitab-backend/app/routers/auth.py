# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate
from app.middleware.auth import security
from app.services.auth import create_user_token, verify_password, get_password_hash
from app.services.jwt import verify_token

router = APIRouter()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **password**: Strong password (min 8 characters)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    - **university**: Optional university (ESTIN, ESI, EPAU, USTHB)
    - **phone_number**: Optional phone number
    """
    try:
        print(f"📧 Registration attempt: {user_data.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cet email est déjà utilisé"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce nom d'utilisateur est déjà pris"
                )
        
        # Validate password strength
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le mot de passe doit contenir au moins 8 caractères"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create new user
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
        
        print(f"✅ User created: {user.id} - {user.email}")
        
        return {
            "message": "Utilisateur créé avec succès",
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'inscription: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and get access token
    
    - **email**: User's email
    - **password**: User's password
    
    Returns JWT access token and user information
    """
    try:
        print(f"🔐 Login attempt: {credentials.email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé. Contactez l'administrateur."
            )
        
        # Create access token
        access_token = create_user_token(user.id, user.email)
        
        print(f"✅ Login successful: {user.email}")
        
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
                "updated_at": str(user.updated_at) if user.updated_at else None,
                "role": "admin" if user.is_admin else "user"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la connexion"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)):
    """
    Get current authenticated user information
    
    Requires valid JWT token in Authorization header
    """
    try:
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide ou expiré"
            )
        
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
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
            "updated_at": str(user.updated_at) if user.updated_at else None,
            "role": "admin" if user.is_admin else "user"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur"
        )

@router.get("/test")
def test_auth():
    """Test endpoint to verify auth router is working"""
    return {
        "message": "Auth router is working!",
        "endpoints": [
            "POST /auth/register",
            "POST /auth/login",
            "GET /auth/me"
        ]
    }
@router.put("/me", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate, 
    db: Session = Depends(get_db),
    # This uses your existing security dependency to get the token
    token: str = Depends(security) 
):
    """Update current user profile info and photo"""
    
    # 1. Verify token and get user (same logic as your get_current_user)
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )
        
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # 2. Update fields ONLY if they are sent (not None)
    if user_update.first_name is not None:
        user.first_name = user_update.first_name
    if user_update.last_name is not None:
        user.last_name = user_update.last_name
    if user_update.university is not None:
        user.university = user_update.university
    if user_update.phone_number is not None:
        user.phone_number = user_update.phone_number
        
    # HERE IS THE PHOTO UPDATE
    if user_update.profile_picture_url is not None:
        user.profile_picture_url = user_update.profile_picture_url

    # [cite_start]3. Save to DB [cite: 321]
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du profil"
        )
