import bcrypt
from .jwt import create_access_token

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches the hashed password"""
    try:
        # Bcrypt strictly limits to 72 bytes.
        pw_encoded = plain_password.encode('utf-8')[:72]
        
        # Check if it's already a bcrypt hash (starts with $2b$ or $2a$)
        if hashed_password.startswith('$2'):
            return bcrypt.checkpw(pw_encoded, hashed_password.encode('utf-8'))
        
        # Fallback for plain text passwords (detected in database)
        return plain_password == hashed_password
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash the password using bcrypt (max 72 bytes)"""
    # Bcrypt strictly limits to 72 bytes.
    pw_encoded = password.encode('utf-8')[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_encoded, salt)
    return hashed.decode('utf-8')



def create_user_token(user_id: int, email: str) -> str:
    """Generate JWT access token for the user"""
    access_token = create_access_token(
        data={"sub": email, "user_id": user_id}
    )
    return access_token
