"""
Seed script – populates the PostgreSQL database with realistic
project expenses, budgets, tasks, phases and milestones.

Run from the backend folder:
    python seed_projects_dashboard.py
"""

import sys, os
from datetime import datetime, date, timedelta

# ── Bootstrap: import the FastAPI app so ALL models are registered ──
# This avoids every circular-import / mapper-not-found issue.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app.main  # noqa – triggers all model imports

from app.core.database import SessionLocal
from app.models.project.project import Project, ProjectStatus
from app.models.project.budget import ProjectBudget
from app.models.project.expense import ProjectExpense, ExpenseStatus
from app.models.project.task import Task, TaskStatus, TaskPriority
from app.models.project.phase import ProjectPhase, PhaseStatus
from app.models.project.milestone import ProjectMilestone, MilestoneStatus
from app.modules.users.models.user import User


def seed():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("❌ Aucun utilisateur trouvé. Créez-en un d'abord.")
            return
        author_id = user.id

        projects = db.query(Project).all()
        if not projects:
            print("❌ Aucun projet trouvé. Créez-en un d'abord.")
            return

        print(f"🔧 {len(projects)} projet(s) trouvé(s) – seeding en cours…")

        for project in projects:
            print(f"   → Projet '{project.nom}' (id={project.id})")

            # ── 1. Dates & statut ─────────────────────────────────
            project.date_debut_estimee = date.today() - timedelta(days=45)
            project.date_debut_reelle  = date.today() - timedelta(days=40)
            project.date_fin_estimee   = date.today() + timedelta(days=120)
            project.date_fin_prevue    = date.today() + timedelta(days=130)
            project.status = ProjectStatus.ONGOING

            # ── 2. Budget global ──────────────────────────────────
            project.budget_estime = 15_000_000.0  # 15 M FCFA

            # Budget lines
            budget_lines = [
                ("Main d'œuvre",    5_000_000),
                ("Matériaux",       4_000_000),
                ("Sous-traitance",  3_000_000),
                ("Logistique",      2_000_000),
                ("Divers",          1_000_000),
            ]
            budget_map = {}
            for cat, amount in budget_lines:
                existing = (
                    db.query(ProjectBudget)
                    .filter(ProjectBudget.project_id == project.id, ProjectBudget.category == cat)
                    .first()
                )
                if not existing:
                    existing = ProjectBudget(
                        project_id=project.id,
                        category=cat,
                        allocated_amount=amount,
                    )
                    db.add(existing)
                    db.flush()
                budget_map[cat] = existing

            # ── 3. Dépenses (nettoyage puis recréation) ───────────
            db.query(ProjectExpense).filter(ProjectExpense.project_id == project.id).delete()

            expense_data = [
                # (montant, jours_passés, description, catégorie_budget)
                (  450_000,  90, "Étude géotechnique",          "Divers"),
                (  800_000,  75, "Salaires équipe chantier M1", "Main d'œuvre"),
                (1_200_000,  60, "Achat ciment & ferraille",    "Matériaux"),
                (  950_000,  55, "Salaires équipe chantier M2", "Main d'œuvre"),
                (  600_000,  45, "Location engins TP",          "Logistique"),
                (1_500_000,  35, "Sous-traitance électricité",  "Sous-traitance"),
                (  350_000,  30, "Carburant véhicules",         "Logistique"),
                (  700_000,  20, "Menuiserie aluminium",        "Matériaux"),
                (  400_000,  10, "Salaires équipe chantier M3", "Main d'œuvre"),
                (  250_000,   3, "Fournitures de bureau",       "Divers"),
            ]

            total_expense = 0
            for amt, days_ago, desc, cat in expense_data:
                budget_ref = budget_map.get(cat)
                exp = ProjectExpense(
                    project_id=project.id,
                    budget_id=budget_ref.id if budget_ref else None,
                    amount=amt,
                    date_incurred=date.today() - timedelta(days=days_ago),
                    description=desc,
                    status=ExpenseStatus.APPROVED,
                )
                db.add(exp)
                total_expense += amt

            project.budget_engage = total_expense
            print(f"     💰 Budget engagé: {total_expense:,.0f} FCFA / {project.budget_estime:,.0f}")

            # ── 4. Phases ─────────────────────────────────────────
            db.query(ProjectPhase).filter(ProjectPhase.project_id == project.id).delete()
            phases_data = [
                ("Études préliminaires",  -45, -30, 100.0, PhaseStatus.COMPLETED),
                ("Travaux de fondation",  -30, -10,  80.0, PhaseStatus.IN_PROGRESS),
                ("Gros œuvre",            -10,  30,  35.0, PhaseStatus.IN_PROGRESS),
                ("Second œuvre",           30,  80,   0.0, PhaseStatus.PENDING),
                ("Finitions & réception",  80, 120,   0.0, PhaseStatus.PENDING),
            ]
            for i, (name, start_offset, end_offset, pct, status) in enumerate(phases_data):
                phase = ProjectPhase(
                    project_id=project.id,
                    name=name,
                    order_index=i,
                    date_debut=date.today() + timedelta(days=start_offset),
                    date_fin=date.today() + timedelta(days=end_offset),
                    completion_percent=pct,
                    status=status,
                )
                db.add(phase)

            # ── 5. Jalons ─────────────────────────────────────────
            db.query(ProjectMilestone).filter(ProjectMilestone.project_id == project.id).delete()
            milestones_data = [
                ("Validation études",        -25, MilestoneStatus.ACHIEVED, date.today() + timedelta(days=-25)),
                ("Fin fondations",            -5, MilestoneStatus.ACHIEVED, date.today() + timedelta(days=-5)),
                ("Réception provisoire GO",   40, MilestoneStatus.PENDING,  None),
                ("Réception définitive",     120, MilestoneStatus.PENDING,  None),
            ]
            for title, offset, ms_status, achieved in milestones_data:
                ms = ProjectMilestone(
                    project_id=project.id,
                    title=title,
                    due_date=date.today() + timedelta(days=offset),
                    status=ms_status,
                    achieved_date=achieved,
                )
                db.add(ms)

            # ── 6. Tâches ────────────────────────────────────────
            existing_task_count = db.query(Task).filter(Task.project_id == project.id).count()
            if existing_task_count < 6:
                tasks_data = [
                    ("Relevé topographique",          TaskStatus.DONE,        TaskPriority.HIGH,   -30),
                    ("Étude de sol",                   TaskStatus.DONE,        TaskPriority.HIGH,   -20),
                    ("Plan d'exécution fondations",    TaskStatus.DONE,        TaskPriority.MEDIUM, -10),
                    ("Coulage dalle RDC",              TaskStatus.IN_PROGRESS, TaskPriority.URGENT,  5),
                    ("Commande menuiseries",           TaskStatus.TODO,        TaskPriority.MEDIUM, 25),
                    ("Installation réseau électrique", TaskStatus.TODO,        TaskPriority.HIGH,   45),
                    ("Peinture intérieure",            TaskStatus.TODO,        TaskPriority.LOW,    70),
                    ("Tests & mise en service",        TaskStatus.TODO,        TaskPriority.URGENT, 100),
                ]
                for title, status, priority, due_offset in tasks_data:
                    task = Task(
                        title=f"[{project.code}] {title}",
                        description=f"Tâche du projet {project.nom}",
                        status=status,
                        priority=priority,
                        due_date=date.today() + timedelta(days=due_offset),
                        start_date=date.today() - timedelta(days=5) if status != TaskStatus.TODO else None,
                        author_id=author_id,
                        project_id=project.id,
                    )
                    db.add(task)
                print(f"     📋 {len(tasks_data)} tâches ajoutées")
            else:
                print(f"     📋 {existing_task_count} tâches existantes – skip")

        db.commit()
        print("\n✅ Seeding terminé avec succès !")
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        print(f"\n❌ Erreur : {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
