from app.database import SessionLocal

from app.models.department import Department
from app.models.employee import Employee

db = SessionLocal()

# -------------------------
# DEPARTMENTS
# -------------------------

departments_data = [
    ("RH", "RH"),
    ("Direction", "DIR"),
    ("Commercial", "COM"),
    ("Logistique", "LOG"),
    ("Maintenance", "MNT"),
    ("Finance", "FIN"),
    ("Projets", "PRJ"),
]

department_ids = {}

for name, code in departments_data:
    department = (
        db.query(Department)
        .filter(Department.code == code)
        .first()
    )

    if not department:
        department = Department(
            name=name,
            code=code
        )

        db.add(department)
        db.commit()
        db.refresh(department)

    department_ids[code] = department.id

# -------------------------
# EMPLOYEES
# -------------------------

employees_data = [
    {
        "matricule": "EMP001",
        "first_name": "A",
        "last_name": "A",
        "email": "a@coselec.ma",
        "phone": "770000001",
        "position": "Responsable RH",
        "status": "CDI",
        "department_code": "RH",
    },
    {
        "matricule": "EMP002",
        "first_name": "B",
        "last_name": "B",
        "email": "b@coselec.ma",
        "phone": "770000002",
        "position": "Directeur",
        "status": "CDI",
        "department_code": "DIR",
    },
    {
        "matricule": "EMP003",
        "first_name": "C",
        "last_name": "C",
        "email": "c@coselec.ma",
        "phone": "770000003",
        "position": "Commercial",
        "status": "CDI",
        "department_code": "COM",
    },
    {
        "matricule": "EMP004",
        "first_name": "D",
        "last_name": "D",
        "email": "d@coselec.ma",
        "phone": "770000004",
        "position": "Chef Projet",
        "status": "CDI",
        "department_code": "PRJ",
    },
    {
        "matricule": "EMP005",
        "first_name": "E",
        "last_name": "E",
        "email": "e@coselec.ma",
        "phone": "770000005",
        "position": "Technicien",
        "status": "CDD",
        "department_code": "MNT",
    },
    {
        "matricule": "EMP006",
        "first_name": "F",
        "last_name": "F",
        "email": "f@coselec.ma",
        "phone": "770000006",
        "position": "Logisticien",
        "status": "CDI",
        "department_code": "LOG",
    },
    {
        "matricule": "EMP007",
        "first_name": "G",
        "last_name": "G",
        "email": "g@coselec.ma",
        "phone": "770000007",
        "position": "Comptable",
        "status": "CDI",
        "department_code": "FIN",
    }
]

for emp in employees_data:
    existing = (
        db.query(Employee)
        .filter(Employee.matricule == emp["matricule"])
        .first()
    )

    if existing:
        continue

    employee = Employee(
        matricule=emp["matricule"],
        first_name=emp["first_name"],
        last_name=emp["last_name"],
        email=emp["email"],
        phone=emp["phone"],
        position=emp["position"],
        status=emp["status"],
        department_id=department_ids[
            emp["department_code"]
        ]
    )

    db.add(employee)

db.commit()

print("✅ Départements et employés créés avec succès")