from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    matricule = Column(String, unique=True)

    first_name = Column(String)

    last_name = Column(String)

    email = Column(String)

    phone = Column(String)

    position = Column(String)

    status = Column(String)

    department_id = Column(
        Integer,
        ForeignKey("departments.id")
    )