from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.relations import user_roles

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    created_tickets = relationship(
        "Ticket",
        back_populates="creator"
    )

    notifications = relationship(
        "Notification",
        back_populates="user"
    )
    roles = relationship("Role", secondary=user_roles, back_populates="users")