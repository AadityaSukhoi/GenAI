"""
Authentication module for LLMRouter

Features:
- JWT-based authentication
- Password hashing (bcrypt)
- Secure token generation
"""

import os
import bcrypt
import jwt

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from dotenv import load_dotenv

from database import get_db
from models import UserCreate, UserLogin, Token

# -------------------------------
# LOAD ENV
# -------------------------------
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment variables")

# -------------------------------
# ROUTER
# -------------------------------
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ============================================================
# TOKEN CREATION
# ============================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT access token
    """

    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# ============================================================
# TOKEN VALIDATION
# ============================================================
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validates JWT token and extracts username
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    return username


# ============================================================
# REGISTER
# ============================================================
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db=Depends(get_db)):
    """
    Register a new user
    """

    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already registered")

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt)

    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (user.username, hashed_password.decode("utf-8")),
    )

    db.commit()

    return {"message": "User created successfully"}


# ============================================================
# LOGIN
# ============================================================
@router.post("/login", response_model=Token)
def login(user: UserLogin, db=Depends(get_db)):
    """
    Authenticate user and return JWT token
    """

    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()

    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not bcrypt.checkpw(
        user.password.encode("utf-8"),
        db_user["password_hash"].encode("utf-8"),
    ):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}