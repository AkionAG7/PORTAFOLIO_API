from sqlalchemy import Column,String, DateTime
from sqlalchemy.orm import Relationship
from app.db.base import Base
from app.models.User_language import UserLanguage
from app.models.User_stack import UserStack

#CLASE DE LA BASE DE DATOS
class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key= True)
    name = Column(String)
    last_name1 = Column(String)
    last_name2 = Column(String, nullable= True)
    email = Column(String, unique=True)
    password = Column(String)
    rol = Column(String)
    title = Column(String)
    create_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=True)
    #relaciones
    projects = Relationship("Project", back_populates="User")
    contacts = Relationship("Contact", back_populates="User")
    languages = Relationship(
        "Language",
        secondary= UserLanguage,
        back_populates="User"
    )
    stacks = Relationship(
        "Stack",
        secondary= UserStack,
        back_populates="User"
    )