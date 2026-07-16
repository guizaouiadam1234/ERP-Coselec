from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.relations import user_roles

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    created_it_requests = relationship("ITRequest", foreign_keys="ITRequest.creator_id", back_populates="creator")
    assigned_it_requests = relationship("ITRequest", foreign_keys="ITRequest.assigned_to_id", back_populates="assigned_to")
    created_facility_requests = relationship("FacilityRequest", foreign_keys="FacilityRequest.creator_id", back_populates="creator")
    assigned_facility_requests = relationship("FacilityRequest", foreign_keys="FacilityRequest.assigned_to_id", back_populates="assigned_to")

    notifications = relationship(
        "Notification",
        back_populates="user"
    )
    roles = relationship("Role", secondary=user_roles, back_populates="users")