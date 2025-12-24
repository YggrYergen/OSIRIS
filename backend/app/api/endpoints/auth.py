from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import os

from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas import user as user_schema
from app.schemas import token as token_schema
from app.models.user import User

router = APIRouter()

# Setup Logging
logger = logging.getLogger("auth_debugger")

@router.post("/login/access-token", response_model=token_schema.Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, retrieve an access token for future requests
    """
    logger.info(f"START LOGIN REQUEST: {form_data.username}")
    
    # Find user by email or username
    try:
        result = await db.execute(
            select(User).where(
                (User.email == form_data.username) | (User.username == form_data.username)
            )
        )
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"DB QUERY ERROR: {e}")
        raise HTTPException(status_code=500, detail="Database Error")

    is_valid = False
    if user:
        logger.info(f"User FOUND: {user.email}")
        is_valid = security.verify_password(form_data.password, user.hashed_password)
        logger.info(f"Password verification: {is_valid}")
    else:
        logger.info("User NOT FOUND in DB.")

    if not user or not is_valid:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    access_token_expires = timedelta(minutes=60 * 24)
    logger.info("Login SUCCESS. Issuing token.")
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=user_schema.User)
async def register_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: user_schema.UserCreate
) -> Any:
    """
    Create new user.
    """
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    db_obj = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=security.get_password_hash(user_in.password),
        role=user_in.role or "agent",
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.post("/login/google", response_model=token_schema.Token)
async def login_google(
    *,
    db: AsyncSession = Depends(deps.get_db),
    token_in: str # Expecting ID Token from Google
) -> Any:
    """
    Google OAuth2 login
    """
    from app.core.auth import verify_google_token
    idinfo = verify_google_token(token_in)
    if not idinfo:
        raise HTTPException(status_code=400, detail="Invalid Google Token")
    
    result = await db.execute(select(User).where(User.email == idinfo["email"]))
    user = result.scalar_one_or_none()
    
    if not user:
        # Auto-register Google users
        user = User(
            email=idinfo["email"],
            username=idinfo["email"].split("@")[0],
            full_name=idinfo.get("name"),
            google_id=idinfo["sub"],
            is_active=True,
            role="agent"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    access_token_expires = timedelta(minutes=60 * 24)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
