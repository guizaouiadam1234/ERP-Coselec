from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks.hr_alerts import check_document_expirations

#schemas
from app.schemas.register import RegisterRequest

#hr routers
from app.routers.employees import router as employees_router
from app.routers.planning import router as planning_router
from app.routers.contracts import router as contracts_router
from app.routers.leaverequests import router as leave_requests_router
from app.routers.documents import router as documents_router
## stock routers
from app.routers.stock.stocks import router as stocks_router
from app.routers.stock.stockoperations import router as stock_operations_router
from app.routers.stock.dashboard import router as dashboard_router
from app.routers.stock.stockmovements import router as stock_movements_router
from app.routers.stock.products import router as products_router
from app.routers.stock.warehouses import router as warehouses_router
from app.routers.stock.partners import router as partners_router
from app.routers.stock.categories import router as categories_router
#ticket router
from app.routers.tickets import router as tickets_router
#notifications router
from app.routers.notifications import router as notifications_router
#projects router
from app.routers.projects import router as projects_router

from app.auth import (
    get_current_user,
    verify_password,
    create_access_token,
    hash_password,
)
from app.database import Base, engine, get_db, SessionLocal

from app.models.user import User
from app.models.role import Role
from app.models.employee import Employee
from app.models.department import Department
from app.models.permission import Permission
from app.models.stock.category import Category
from app.models.stock.partner import Partner
from app.models.stock.product import Product
from app.models.stock.stock import Stock
from app.models.stock.stockmovement import StockMovement
from app.models.stock.warehouse import Warehouse
from app.models.notification import NotificationType

from app.services.notification import create_notification
from app.services.rbac import (
    ensure_rbac_setup,
    assign_default_role,
    ensure_admin_role_for_email,
    assign_role_to_user,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        ensure_rbac_setup(db)
        ensure_admin_role_for_email(db, "adam@adam.com")
    finally:
        db.close()

    scheduler = BackgroundScheduler()
    scheduler.add_job(check_document_expirations, 'cron', hour=8, minute=0) 
    scheduler.start()
    yield
    scheduler.shutdown()





app = FastAPI(lifespan=lifespan)

app.include_router(employees_router)
app.include_router(stocks_router)
app.include_router(stock_operations_router)
app.include_router(dashboard_router)
app.include_router(stock_movements_router)
app.include_router(products_router)
app.include_router(warehouses_router)
app.include_router(partners_router)
app.include_router(categories_router)
app.include_router(planning_router)
app.include_router(tickets_router)
app.include_router(notifications_router)
app.include_router(contracts_router)
app.include_router(leave_requests_router)
app.include_router(documents_router)
app.include_router(projects_router)

class LoginRequest(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Welcome to the ERP API!"}

@app.post("/register")
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

@app.post("/login")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    email = payload.email or payload.username
    if not email:
        raise HTTPException(
            status_code=422,
            detail="email or username is required"
        )

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        payload.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"sub": str(user.id)}
    )

    response = JSONResponse(
        content = {"message" : "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=3600,
        expires=3600,
        samesite="lax"
    )
    return response
    

@app.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "roles": [role.name for role in current_user.roles]
    }


@app.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(key="access_token", samesite="lax")
    return response