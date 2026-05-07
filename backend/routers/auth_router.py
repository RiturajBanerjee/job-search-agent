# backend/routers/auth_router.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from auth import verify_password, create_token, get_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login(req: LoginRequest):
    user = get_user(req.email)
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")
    return {"access_token": create_token(req.email), "token_type": "bearer"}

@router.post("/register")
def register(req: RegisterRequest):
    if get_user(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    create_user(req.email, req.password)
    return {"access_token": create_token(req.email), "token_type": "bearer"}