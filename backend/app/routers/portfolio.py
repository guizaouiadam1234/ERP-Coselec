from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.project.project import Project, ProjectStatus
from app.models.project.budget import ProjectBudget
from app.models.project.expense import ProjectExpense

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/kpis")
def get_portfolio_kpis(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    ongoing_projects = db.query(Project).filter(Project.status == ProjectStatus.ONGOING).count()
    
    total_budget = db.query(func.sum(ProjectBudget.allocated_amount)).scalar() or 0.0
    total_consumed = db.query(func.sum(ProjectExpense.amount)).scalar() or 0.0
    
    return {
        "total_projects": total_projects,
        "ongoing_projects": ongoing_projects,
        "total_budget_allocated": total_budget,
        "total_budget_consumed": total_consumed,
        "budget_consumption_rate": round((total_consumed / total_budget * 100), 2) if total_budget > 0 else 0
    }
