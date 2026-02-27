from sqlalchemy import Column,String, DateTime, Boolean
from sqlalchemy.orm import Relationship
from app.db.base import Base
from app.models.User_language import UserLanguage
from sqlalchemy.dialects.postgresql import UUID
import uuid

#CLASE DE LA BASE DE DATOS
class Language(Base):
    __tablename__ = "Language"

    id = Column(UUID(as_uuid=True), primary_key= True, default= uuid.uuid4)
    name = Column(String)
    status= Column(Boolean, default=True)
    create_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=True)

    #Relaciones
    users = Relationship(
        "User",
        secondary= UserLanguage,
        back_populates="Language"
    )