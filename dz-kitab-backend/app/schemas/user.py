# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    university: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v:
            raise ValueError('Le nom d\'utilisateur est requis')
        
        # Alphanumeric and underscores only
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et underscores')
        
        # Cannot start with number
        if v[0].isdigit():
            raise ValueError('Le nom d\'utilisateur ne peut pas commencer par un chiffre')
        
        return v.lower()  # Store in lowercase
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        
        # Check for at least one uppercase, one lowercase, one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        
        if not re.search(r'\d', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate Algerian phone number format"""
        if v is None:
            return v
        
        # Remove spaces and dashes
        clean_phone = re.sub(r'[\s\-]', '', v)
        
        # Algerian phone patterns:
        # +213XXXXXXXXX or 0XXXXXXXXX
        patterns = [
            r'^\+213[5-7]\d{8}$',  # +213 followed by 5/6/7 and 8 digits
            r'^0[5-7]\d{8}$'       # 0 followed by 5/6/7 and 8 digits
        ]
        
        if not any(re.match(pattern, clean_phone) for pattern in patterns):
            raise ValueError(
                'Numéro de téléphone invalide. Format attendu: +213XXXXXXXXX ou 0XXXXXXXXX'
            )
        
        # Normalize to +213 format
        if clean_phone.startswith('0'):
            clean_phone = '+213' + clean_phone[1:]
        
        return clean_phone
    
    @validator('university')
    def validate_university(cls, v):
        """Validate university enum"""
        if v is None:
            return v
        
        valid_universities = ['ESTIN', 'ESI', 'EPAU', 'USTHB']
        if v.upper() not in valid_universities:
            raise ValueError(f'Université invalide. Choisissez parmi: {", ".join(valid_universities)}')
        
        return v.upper()
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate names"""
        if v is None:
            return v
        
        # Remove extra spaces
        v = ' '.join(v.split())
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\']+$', v):
            raise ValueError('Le nom ne peut contenir que des lettres, espaces, traits d\'union et apostrophes')
        
        return v.strip()

class UserCreateSimple(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    university: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    
