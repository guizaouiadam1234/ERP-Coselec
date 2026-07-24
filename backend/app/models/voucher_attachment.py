from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class VoucherAttachment(Base):
    __tablename__ = "voucher_attachments"

    id = Column(Integer, primary_key=True, index=True)
    bank_voucher_id = Column(Integer, ForeignKey("bank_vouchers.id", ondelete="CASCADE"), nullable=True)
    caisse_voucher_id = Column(Integer, ForeignKey("caisse_vouchers.id", ondelete="CASCADE"), nullable=True)
    
    file_name = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
