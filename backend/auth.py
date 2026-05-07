# backend/auth.py
import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import SessionLocal
from models import User
from config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Password helpers ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# --- JWT helpers ---
def create_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": email, "exp": expire},
        settings.secret_key, algorithm="HS256"
    )

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        return None

# --- DB helpers ---
def get_user(email: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

def create_user(email: str, password: str):
    db = SessionLocal()
    try:
        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        logger.info(f"Created user: {email}")
        return user
    finally:
        db.close()

# --- FastAPI dependency — use in protected routes ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")
    user = get_user(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    return user