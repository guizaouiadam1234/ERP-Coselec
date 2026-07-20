import random
from datetime import timedelta, date
from faker import Faker
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base

# Importation de vos modèles
from app.modules.users.models.department import Department
from app.modules.users.models.employee import Employee
from app.models.stock.category import Category
from app.models.stock.product import Product
from app.models.stock.partner import Partner
from app.models.stock.warehouse import Warehouse
from app.models.stock.stock import Stock
from app.models.hr.attendance import Attendance
from app.models.hr.document import EmployeeDocument
from app.modules.users.models.permission import Permission
from app.modules.users.models.role import Role
from app.modules.users.models.user import User
from app.models.it_request import ITRequest
from app.models.facility_request import FacilityRequest
from app.models.hr.hr_request import HRRequest
from app.models.hr.leave_request import LeaveRequest
from app.modules.requests.models.fuel_request import FuelRequest

# Nouveaux modèles ajoutés
from app.models.project.client import Client
from app.models.project.project import Project, ProjectStatus
from app.models.project.task import Task, TaskStatus, TaskPriority

# Initialisation de Faker (noms génériques/internationaux)
fake = Faker('fr_FR')

def seed_database():
    import app.main # Load all models
    print("⏳ Création des tables si elles n'existent pas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🧹 Nettoyage des anciennes données...")
        db.query(LeaveRequest).delete()
        db.query(Attendance).delete()
        db.query(EmployeeDocument).delete()
        db.query(FuelRequest).delete()
        db.query(ITRequest).delete()
        db.query(FacilityRequest).delete()
        db.query(HRRequest).delete()
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Client).delete()
        db.query(Stock).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.query(Partner).delete()
        db.query(Warehouse).delete()
        db.query(Employee).delete()
        db.query(Department).delete()
        db.commit()

        print("🔑 Vérification des rôles et permissions...")

        def get_or_create_perm(code, name):
            perm = db.query(Permission).filter_by(code=code).first()
            if not perm:
                perm = Permission(code=code, name=name)
                db.add(perm)
            return perm

        perm_stock_read = get_or_create_perm("stock.read", "Voir les stocks")
        perm_stock_write = get_or_create_perm("stock.edit", "Modifier les stocks")
        perm_emp_read = get_or_create_perm("employee.read", "Voir les employés")
        perm_it_read = get_or_create_perm("it_requests.read", "Voir les demandes IT")
        perm_it_manage = get_or_create_perm("it_requests.create", "Créer des demandes IT")
        perm_facility_read = get_or_create_perm("facility_requests.read", "Voir les demandes logistiques")
        perm_facility_manage = get_or_create_perm("facility_requests.create", "Créer des demandes logistiques")
        perm_hr_read = get_or_create_perm("hr_requests.read", "Voir les demandes RH")
        perm_hr_manage = get_or_create_perm("hr_requests.create", "Créer des demandes RH")
        perm_projects_read = get_or_create_perm("projects.read", "Voir les projets")

        db.commit()

        def get_or_create_role(name, description):
            role = db.query(Role).filter_by(name=name).first()
            if not role:
                role = Role(name=name, description=description)
                db.add(role)
            return role

        role_admin = get_or_create_role("Admin", "Accès total")
        role_tech = get_or_create_role("Technicien", "Accès limité aux stocks")

        role_admin.permissions = [perm_stock_read, perm_stock_write, perm_emp_read, perm_projects_read]
        role_tech.permissions = [perm_stock_read]

        db.commit()
        
        # ---------------------------------------------------------
        # 1. CRÉATION DES DÉPARTEMENTS
        # ---------------------------------------------------------
        print("🏢 Création des départements...")
        dept_rh = Department(name="Ressources Humaines", code="RH")
        dept_it = Department(name="Informatique", code="IT")
        dept_ops = Department(name="Opérations", code="OPS")
        dept_tech = Department(name="Technique & Chantier", code="TECH")
        
        db.add_all([dept_rh, dept_it, dept_ops, dept_tech])
        db.commit()
        
        departments = [dept_rh, dept_it, dept_ops, dept_tech]

        # ---------------------------------------------------------
        # 2. CRÉATION DES EMPLOYÉS (Faker)
        # ---------------------------------------------------------
        print("🧑‍💼 Création des employés...")
        statuses = ["Sur site", "Sur chantier", "En congé"]
        
        employees = []
        for _ in range(30):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@coselec.sn"
            
            emp = Employee(
                matricule=fake.unique.bothify(text='MAT-####'),
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=fake.phone_number(),
                position=fake.job(),
                status=random.choice(statuses),
                department_id=random.choice(departments).id
            )
            db.add(emp)
            employees.append(emp)
        db.commit()

        # Add an admin user explicitly attached to an employee if needed? The user already has one, but we shouldn't delete users here so admin login isn't broken.
        
        # ---------------------------------------------------------
        # 3. CRÉATION DES CLIENTS
        # ---------------------------------------------------------
        print("🤝 Création des clients...")
        clients = []
        for _ in range(10):
            client = Client(
                code=fake.unique.bothify(text='CLI-####'),
                name=fake.company(),
                email=fake.company_email(),
                phone=fake.phone_number(),
                address=fake.address()
            )
            db.add(client)
            clients.append(client)
        db.commit()

        # ---------------------------------------------------------
        # 4. CRÉATION DES PROJETS
        # ---------------------------------------------------------
        print("🏗️ Création des projets...")
        project_types = ["Construction Electrique", "Maintenance", "Etude & Conception", "Réseau MT/BT"]
        
        projects = []
        for i in range(15):
            start_date = fake.date_between(start_date='-1y', end_date='+1m')
            end_date_est = start_date + timedelta(days=random.randint(60, 365))
            
            proj = Project(
                code=f"PRJ26-{i+1:03d}",
                nom=fake.catch_phrase()[:100],
                status=random.choice(list(ProjectStatus)),
                project_type=random.choice(project_types),
                description=fake.text(),
                client_id=random.choice(clients).id,
                chef_projet_id=random.choice(employees).id,
                date_debut_estimee=start_date,
                date_fin_estimee=end_date_est,
                date_fin_prevue=end_date_est,
                budget_estime=random.uniform(5000000, 150000000),
                budget_engage=random.uniform(0, 5000000)
            )
            db.add(proj)
            projects.append(proj)
        db.commit()

        # ---------------------------------------------------------
        # 5. CRÉATION DES TÂCHES
        # ---------------------------------------------------------
        print("📝 Création des tâches...")
        
        # Assuming there is at least one user for author_id. We fetch the first user, or default to 1.
        first_user = db.query(User).first()
        author_id = first_user.id if first_user else 1

        for _ in range(60):
            proj = random.choice(projects)
            due = proj.date_fin_estimee - timedelta(days=random.randint(0, 30))
            
            task = Task(
                title=fake.sentence(nb_words=6),
                description=fake.paragraph(),
                status=random.choice(list(TaskStatus)),
                priority=random.choice(list(TaskPriority)),
                due_date=due,
                start_date=due - timedelta(days=random.randint(2, 10)),
                author_id=author_id,
                assignee_id=random.choice(employees).id,
                project_id=proj.id
            )
            db.add(task)
        db.commit()

        # ---------------------------------------------------------
        # 6. CRÉATION DES PARTENAIRES, CATÉGORIES & DÉPÔTS
        # ---------------------------------------------------------
        print("📦 Création des référentiels de Stock...")
        
        p_sen = Partner(code="SEN", name="SENELEC")
        p_pro = Partner(code="PRO", name="PROQUELEC")
        p_brt = Partner(code="BRT", name="BRT")
        p_aee = Partner(code="AEE", name="AEE Power")
        db.add_all([p_sen, p_pro, p_brt, p_aee])
        
        cat_elec = Category(code="ELEC", name="Matériel Électrique")
        cat_cabl = Category(code="CABL", name="Câbles et Conducteurs")
        cat_quin = Category(code="QUIN", name="Quincaillerie")
        cat_outils = Category(code="OUTIL", name="Outillage Chantier")
        db.add_all([cat_elec, cat_cabl, cat_quin, cat_outils])
        
        w_bar = Warehouse(code="DEP-BAR", name="Dépôt BARGNY")
        w_cos = Warehouse(code="DEP-COS", name="Dépôt COSELEC")
        db.add_all([w_bar, w_cos])
        
        db.commit()

        # ---------------------------------------------------------
        # 7. CRÉATION DES PRODUITS ET STOCKS (Enrichis avec Faker)
        # ---------------------------------------------------------
        print("🛒 Création des produits et de l'inventaire des stocks...")
        
        products_data = [
            {"ref": "P001", "des": "AFFICHE ALLU CONSIGNES GNRLE AM18", "unit": "u", "price": 7200, "cat": cat_quin, "qty": 15},
            {"ref": "P002", "des": "ARMEMENT TRIANGLE", "unit": "u", "price": 55000, "cat": cat_elec, "qty": 13},
            {"ref": "P003", "des": "CABLE ALMELEC 75,5", "unit": "m", "price": 300, "cat": cat_cabl, "qty": 66000},
            {"ref": "P004", "des": "BATTERIE ONDULEUR 12V 150", "unit": "u", "price": 40000, "cat": cat_elec, "qty": 5},
            {"ref": "P005", "des": "ISOLATEUR COMPOSITE 3 JUPES", "unit": "u", "price": 17000, "cat": cat_elec, "qty": 54},
            {"ref": "P006", "des": "FUSIBLE GARDE", "unit": "u", "price": 12000, "cat": cat_elec, "qty": 124},
            {"ref": "P007", "des": "BOULON GALVA A CHAUD BH 12X70", "unit": "u", "price": 150, "cat": cat_quin, "qty": 160},
            {"ref": "P008", "des": "LANTERNE LED 50W", "unit": "u", "price": 27000, "cat": cat_elec, "qty": 22},
            {"ref": "P009", "des": "CONNECTEUR CT 25", "unit": "u", "price": 1284, "cat": cat_elec, "qty": 300},
            {"ref": "P010", "des": "CABLE ALU PREAS 3 X 35+54.6+16mm²", "unit": "m", "price": 1830, "cat": cat_cabl, "qty": 6243},
        ]

        # Add some more fake products
        for i in range(11, 40):
            cat = random.choice([cat_elec, cat_cabl, cat_quin, cat_outils])
            products_data.append({
                "ref": f"P{i:03d}",
                "des": f"{fake.word().upper()} {fake.word().upper()} {random.randint(10, 500)}",
                "unit": random.choice(["u", "m", "kg", "boite"]),
                "price": random.randint(100, 150000),
                "cat": cat,
                "qty": random.randint(0, 500)
            })

        for p_data in products_data:
            prod = Product(
                code=p_data["ref"],
                designation=p_data["des"],
                category_id=p_data["cat"].id,
                unit=p_data["unit"],
                unit_price=p_data["price"],
                minimum_stock=random.randint(5, 50)
            )
            db.add(prod)
            db.commit() 
            
            stock = Stock(
                product_id=prod.id,
                warehouse_id=random.choice([w_bar.id, w_cos.id]),
                partner_id=random.choice([p_sen.id, p_pro.id, p_brt.id, p_aee.id]),
                quantity=p_data["qty"]
            )
            db.add(stock)

        db.commit()
        print("✅ Base de données initialisée avec succès ! Les données factices ont été générées.")

    except Exception as e:
        print(f"❌ Une erreur s'est produite : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()