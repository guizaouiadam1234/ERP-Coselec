
from sqlalchemy import Column, Integer, String

from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)

    code = Column(String, unique=True)
    name = Column(String)
    description = Column(String)
