from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.core.database import Base
from datetime import datetime

class CaisseVoucher(Base):
    __tablename__ = "caisse_vouchers"
    
    id = Column(Integer, primary_key=True, index=True)
    num = Column(String(50), nullable=True)
    affaire = Column(String(255), nullable=True)
    cia = Column(String(255), nullable=True)
    
    depenses = Column(JSON, default=list)
    recettes = Column(JSON, default=list)
    
    pdf_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
