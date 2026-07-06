import pandas as pd

from app.database import SessionLocal

from app.models.stock.product import Product
from app.models.stock.partner import Partner
from app.models.stock.warehouse import Warehouse
from app.models.stock.stock import Stock
from app.models.stock.stockmovement import StockMovement

from app.enums.movement_type import MovementType


FILE_PATH = "Inventaire Exercice 2025mk.xlsx"


db = SessionLocal()

try:

    df = pd.read_excel(
        FILE_PATH,
        engine="openpyxl"
    )

    warehouses = {
        "BARGNY": db.query(Warehouse)
        .filter(Warehouse.code == "BAR")
        .first(),

        "COSELEC": db.query(Warehouse)
        .filter(Warehouse.code == "COS")
        .first()
    }

    partners = {
        "SENELEC": db.query(Partner)
        .filter(Partner.code == "SEN")
        .first(),

        "PROQUELEC": db.query(Partner)
        .filter(Partner.code == "PRO")
        .first(),

        "BRT": db.query(Partner)
        .filter(Partner.code == "BRT")
        .first(),

        "AEE": db.query(Partner)
        .filter(Partner.code == "AEE")
        .first(),
    }

    for _, row in df.iterrows():

        designation = row.get("DESIGNATION")

        if pd.isna(designation):
            continue

        unit = row.get("Unité")
        price = row.get("Prix Unit")

        product = (
            db.query(Product)
            .filter(Product.name == designation)
            .first()
        )

        if not product:

            product = Product(
                code=f"P{str(_).zfill(6)}",
                name=str(designation),
                unit=str(unit),
                unit_price=float(price or 0),
                minimum_stock=0,
            )

            db.add(product)
            db.flush()

        mappings = [

            (
                "Stock SENELEC au Dépôt BARGNY",
                partners["SENELEC"],
                warehouses["BARGNY"]
            ),

            (
                "Stock SENELEC au Dépôt COSELEC",
                partners["SENELEC"],
                warehouses["COSELEC"]
            ),

            (
                "STOCK PROQUELEC au Dépôt BARGNY",
                partners["PROQUELEC"],
                warehouses["BARGNY"]
            ),

            (
                "STOCK PROQUELEC Dépôt COSELEC",
                partners["PROQUELEC"],
                warehouses["COSELEC"]
            ),

            (
                "STOCK BRT au Dépôt BARGNY",
                partners["BRT"],
                warehouses["BARGNY"]
            ),

            (
                "STOCK BRT Dépôt COSELEC",
                partners["BRT"],
                warehouses["COSELEC"]
            ),

            (
                "STOCK AEE Power au Dépôt BARGNY",
                partners["AEE"],
                warehouses["BARGNY"]
            ),

            (
                "STOCK AEE Power Dépôt COSELEC",
                partners["AEE"],
                warehouses["COSELEC"]
            ),
        ]

        for col, partner, warehouse in mappings:

            quantity = row.get(col)

            if pd.isna(quantity):
                continue

            try:
                quantity = float(quantity)
            except:
                quantity = 0

            if quantity <= 0:
                continue

            stock = (
                db.query(Stock)
                .filter(
                    Stock.product_id == product.id,
                    Stock.partner_id == partner.id,
                    Stock.warehouse_id == warehouse.id,
                )
                .first()
            )

            if not stock:

                stock = Stock(
                    product_id=product.id,
                    partner_id=partner.id,
                    warehouse_id=warehouse.id,
                    quantity=0
                )

                db.add(stock)

            stock.quantity += quantity

            movement = StockMovement(
                product_id=product.id,
                partner_id=partner.id,
                warehouse_id=warehouse.id,
                quantity=quantity,
                type=MovementType.ENTRY
            )

            db.add(movement)

    db.commit()

    print("✅ Inventory imported successfully")

except Exception as e:
    db.rollback()
    print(e)

finally:
    db.close()