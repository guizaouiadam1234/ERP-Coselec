from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.project.budget import ProjectBudget
from app.models.project.expense import ProjectExpense
from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime, date
from typing import List

router = APIRouter(prefix="/projects/{project_id}/budgets", tags=["Project Budgets"])

class BudgetCreate(BaseModel):
    category: str
    allocated_amount: float
    currency: str = "XOF"

class BudgetResponse(BudgetCreate):
    id: int
    project_id: int
    created_at: datetime
    
    consumed: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class ExpenseCreate(BaseModel):
    budget_id: int | None = None
    amount: float
    date_incurred: date
    description: str | None = None

class ExpenseResponse(ExpenseCreate):
    id: int
    project_id: int
    status: str
    proof_document_url: str | None = None
    model_config = ConfigDict(from_attributes=True)

class ExpenseUpdate(BaseModel):
    status: str

@router.get("/", response_model=List[BudgetResponse])
def get_budgets(project_id: int, db: Session = Depends(get_db)):
    return db.query(ProjectBudget).options(joinedload(ProjectBudget.expenses)).filter(ProjectBudget.project_id == project_id).all()

@router.post("/", response_model=BudgetResponse)
def create_budget(project_id: int, budget: BudgetCreate, db: Session = Depends(get_db)):
    db_budget = ProjectBudget(
        project_id=project_id,
        category=budget.category,
        allocated_amount=budget.allocated_amount,
        currency=budget.currency
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/expenses", response_model=List[ExpenseResponse])
def get_expenses(project_id: int, db: Session = Depends(get_db)):
    return db.query(ProjectExpense).filter(ProjectExpense.project_id == project_id).all()

@router.post("/expenses", response_model=ExpenseResponse)
def add_expense(project_id: int, expense: ExpenseCreate, db: Session = Depends(get_db)):
    if expense.budget_id:
        budget = db.query(ProjectBudget).filter(ProjectBudget.id == expense.budget_id, ProjectBudget.project_id == project_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found for this project")
            
    db_expense = ProjectExpense(
        project_id=project_id,
        budget_id=expense.budget_id,
        amount=expense.amount,
        date_incurred=expense.date_incurred,
        description=expense.description
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.patch("/expenses/{expense_id}/status", response_model=ExpenseResponse)
def update_expense_status(project_id: int, expense_id: int, update_data: ExpenseUpdate, db: Session = Depends(get_db)):
    db_expense = db.query(ProjectExpense).filter(ProjectExpense.id == expense_id, ProjectExpense.project_id == project_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db_expense.status = update_data.status
    db.commit()
    db.refresh(db_expense)
    return db_expense
