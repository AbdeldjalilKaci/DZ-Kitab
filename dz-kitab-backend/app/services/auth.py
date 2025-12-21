from passlib.context import CryptContext
from .jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches the hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash the password using bcrypt (max 72 bytes)"""
    # Bcrypt only supports passwords up to 72 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_user_token(user_id: int, email: str) -> str:
    """Generate JWT access token for the user"""
    access_token = create_access_token(
        data={"sub": email, "user_id": user_id}
    )
    return access_token
