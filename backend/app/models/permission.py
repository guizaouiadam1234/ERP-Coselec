from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.relations import role_permissions

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)

    code = Column(String, unique=True)
    name = Column(String)
    description = Column(String)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
