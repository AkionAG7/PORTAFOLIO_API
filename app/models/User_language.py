from sqlalchemy import Column, ForeignKey, Boolean
from app.db.base import Base

#CLASE DE LA BASE DE DATOS
class UserLanguage(Base):
    __tablename__ = "User_language"
    Base.metadata,
    user_id =Column("user_id", ForeignKey("User.id"), primary_key= True)
    language_id = Column("language_id", ForeignKey("Language.id"), primary_key= True)
    status= Column(Boolean, default=True)
