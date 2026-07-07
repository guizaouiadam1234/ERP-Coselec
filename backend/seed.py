import random
from faker import Faker
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base

# Importation de vos modèles
from app.models.department import Department
from app.models.employee import Employee
from app.models.stock.category import Category
from app.models.stock.product import Product
from app.models.stock.partner import Partner
from app.models.stock.warehouse import Warehouse
from app.models.stock.stock import Stock
from app.models.hr.attendance import Attendance
from app.models.hr.document import EmployeeDocument

# Initialisation de Faker (noms génériques/internationaux)
fake = Faker()

def seed_database():
    print("⏳ Création des tables si elles n'existent pas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🧹 Nettoyage des anciennes données...")
        db.query(Stock).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.query(Partner).delete()
        db.query(Warehouse).delete()
        db.query(Employee).delete()
        db.query(Department).delete()
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
        # 2. CRÉATION DES EMPLOYÉS (Anonymisés)
        # ---------------------------------------------------------
        print("🧑‍💼 Création des employés (Génération de données anonymes)...")
        statuses = ["Sur site", "Sur chantier", "En congé"]
        
        for _ in range(25):
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
                status=random.choice(statuses), # Distribution: Sur site, Chantier, Congé
                department_id=random.choice(departments).id
            )
            db.add(emp)
        db.commit()

        # ---------------------------------------------------------
        # 3. CRÉATION DES PARTENAIRES, CATÉGORIES & DÉPÔTS
        # ---------------------------------------------------------
        print("📦 Création des référentiels de Stock...")
        
        # Partenaires extraits de l'inventaire
        p_sen = Partner(code="SEN", name="SENELEC")
        p_pro = Partner(code="PRO", name="PROQUELEC")
        p_brt = Partner(code="BRT", name="BRT")
        p_aee = Partner(code="AEE", name="AEE Power")
        db.add_all([p_sen, p_pro, p_brt, p_aee])
        
        # Catégories
        cat_elec = Category(code="ELEC", name="Matériel Électrique")
        cat_cabl = Category(code="CABL", name="Câbles et Conducteurs")
        cat_quin = Category(code="QUIN", name="Quincaillerie")
        db.add_all([cat_elec, cat_cabl, cat_quin])
        
        # Dépôts
        w_bar = Warehouse(code="DEP-BAR", name="Dépôt BARGNY")
        w_cos = Warehouse(code="DEP-COS", name="Dépôt COSELEC")
        db.add_all([w_bar, w_cos])
        
        db.commit()

        # ---------------------------------------------------------
        # 4. CRÉATION DES PRODUITS ET STOCKS (Depuis l'inventaire 2025)
        # ---------------------------------------------------------
        print("🛒 Importation d'un échantillon du fichier d'inventaire...")
        
        # Échantillon tiré directement de votre document CSV
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

        for p_data in products_data:
            # 1. Création du produit
            prod = Product(
                code=p_data["ref"],
                designation=p_data["des"],
                category_id=p_data["cat"].id,
                unit=p_data["unit"],
                unit_price=p_data["price"],
                minimum_stock=10
            )
            db.add(prod)
            db.commit() # Validation pour récupérer l'ID
            
            # 2. Assignation aléatoire du stock à un partenaire et un dépôt
            stock = Stock(
                product_id=prod.id,
                warehouse_id=random.choice([w_bar.id, w_cos.id]),
                partner_id=random.choice([p_sen.id, p_pro.id, p_brt.id, p_aee.id]),
                quantity=p_data["qty"]
            )
            db.add(stock)

        db.commit()
        print("✅ Base de données initialisée avec succès ! Les employés, dépôts et l'inventaire sont prêts.")

    except Exception as e:
        print(f"❌ Une erreur s'est produite : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()