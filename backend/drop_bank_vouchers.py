from app.core.database.session import engine
from app.models.bank_voucher import BankVoucher, AnalyticalAllocation

try:
    print("Dropping analytical_allocations table...")
    AnalyticalAllocation.__table__.drop(engine, checkfirst=True)
    print("Dropping bank_vouchers table...")
    BankVoucher.__table__.drop(engine, checkfirst=True)
    print("Tables dropped successfully. Restarting the server will recreate them with the correct schema.")
except Exception as e:
    print(f"Error dropping tables: {e}")
