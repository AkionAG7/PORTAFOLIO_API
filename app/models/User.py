from sqlalchemy import Column,String, DateTime, Boolean
from sqlalchemy.orm import Relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base
from app.models.User_language import UserLanguage
from app.models.User_stack import UserStack
from app.enums.Rol import RolEnum

#CLASE DE LA BASE DE DATOS
class User(Base):
    __tablename__ = "User"
    id = Column(UUID(as_uuid=True), primary_key= True, default= uuid.uuid4)
    name = Column(String)
    last_name1 = Column(String)
    last_name2 = Column(String, nullable= True)
    email = Column(String, unique=True)
    phone_number = Column(String, nullable=True)
    password = Column(String)
    rol = Column(String, default= RolEnum.user)
    description = Column(String, nullable= True)
    user_image = Column(String, nullable= True)
    title = Column(String, nullable= True)
    status= Column(Boolean, default=True)
    create_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=True)
    #relaciones
    projects = Relationship("Project", back_populates="user")
    contacts = Relationship("Contact", back_populates="user")
    languages = Relationship(
        "Language",
        secondary= UserLanguage,
        back_populates="users"
    )
    stacks = Relationship(
        "Stack",
        secondary= UserStack,
        back_populates="users"
    )