from sqlalchemy import Column,String, DateTime
from sqlalchemy.orm import Relationship
from app.db.base import Base
from app.models.User_language import UserLanguage

#CLASE DE LA BASE DE DATOS
class Language(Base):
    __tablename__ = "Language"

    id = Column(String, primary_key= True)
    name = Column(String)
    create_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=True)

    #Relaciones
    users = Relationship(
        "User",
        secondary= UserLanguage,
        back_populates="Language"
    )