from sqlalchemy import Column,String, DateTime
from app.db.base import Base

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