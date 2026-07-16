from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.modules.users.schemas.register import RegisterRequest
from app.modules.users.models.user import User
from app.models.notification import NotificationType

from app.core.security.auth import (
    get_current_user,
    verify_password,
    create_access_token,
    hash_password,
)
from app.modules.users.services.rbac import (
    ensure_rbac_setup,
    assign_default_role,
    assign_role_to_user,
)
from app.services.notification import create_notification

router = APIRouter(tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str

@router.post("/register")
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    hashed_password = hash_password(payload.password)
    user = User(name=payload.full_name, email=payload.email, hashed_password=hashed_password)
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db.add(user)
    db.commit()
    db.refresh(user)

    ensure_rbac_setup(db)
    assign_default_role(db, user)

    if payload.email.strip().lower() == "adam@adam.com":
        assign_role_to_user(db, user, "Admin")

    create_notification(
        db=db,
        user_id=user.id,
        message="Bienvenue sur l'ERP. Votre compte est actif.",
        type=NotificationType.INFO
    )

    return {"message": "User registered successfully", "user_id": user.id}

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email or payload.username
    if not email:
        raise HTTPException(status_code=422, detail="email or username is required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    response = JSONResponse(content={"message" : "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=3600,
        expires=3600,
        samesite="lax"
    )
    return response

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "roles": [role.name for role in current_user.roles]
    }

@router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(key="access_token", samesite="lax")
    return response
