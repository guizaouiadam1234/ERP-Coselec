from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.models.caisse_voucher import VoucherStatus
from app.core.database import Base

class BankVoucher(Base):
    __tablename__ = "bank_vouchers"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String(100), nullable=False)
    check_number = Column(String(50), nullable=False, unique=True)
    date = Column(Date, nullable=False)
    period_num = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False)
    
    status = Column(SQLEnum(VoucherStatus), default=VoucherStatus.DRAFT)
    finalized_at = Column(DateTime, nullable=True)
    
    amount_in_numbers = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(10), default="FCFA")
    amount_in_letters = Column(String(500), nullable=False)
    
    pdf_url = Column(String(500), nullable=True)

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    expense_id = Column(Integer, ForeignKey("project_expenses.id", ondelete="SET NULL"), nullable=True)
    reservation_id = Column(Integer, ForeignKey("project_stock_reservations.id", ondelete="SET NULL"), nullable=True)

    project = relationship("Project")
    expense = relationship("ProjectExpense")
    reservation = relationship("ProjectStockReservation")

    allocations = relationship("AnalyticalAllocation", back_populates="bank_voucher", cascade="all, delete-orphan")


class AnalyticalAllocation(Base):
    __tablename__ = "analytical_allocations"

    id = Column(Integer, primary_key=True, index=True)
    bank_voucher_id = Column(Integer, ForeignKey("bank_vouchers.id"), nullable=False)
    
    cost_center_code = Column(String(50), nullable=False)
    cost_center_name = Column(String(255), nullable=False)
    client = Column(String(255), nullable=True)
    analytical_account = Column(String(50), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)

    bank_voucher = relationship("BankVoucher", back_populates="allocations")
