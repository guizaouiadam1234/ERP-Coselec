import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app.main
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.project.project import Project
from app.models.project.milestone import ProjectMilestone, MilestoneStatus
from app.models.project.task import Task
from datetime import date, timedelta

def migrate_data():
    db: Session = SessionLocal()
    try:
        projects = db.query(Project).all()
        for project in projects:
            # Check if project has milestones
            milestone = db.query(ProjectMilestone).filter(ProjectMilestone.project_id == project.id).order_by(ProjectMilestone.order_index).first()
            if not milestone:
                milestone = ProjectMilestone(
                    project_id=project.id,
                    title="Jalon Initial",
                    order_index=1,
                    due_date=project.date_fin_estimee or date.today() + timedelta(days=30),
                    status=MilestoneStatus.ACTIVE
                )
                db.add(milestone)
                db.flush()
            
            # Associate tasks to the first milestone if they don't have one
            tasks = db.query(Task).filter(Task.project_id == project.id, Task.milestone_id == None).all()
            for task in tasks:
                task.milestone_id = milestone.id
                task.weight = 1

        db.commit()
        print("Data migration completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()
