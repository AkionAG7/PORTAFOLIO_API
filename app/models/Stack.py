from sqlalchemy import Column,String, DateTime
from app.db.base import Base

#CLASE DE LA BASE DE DATOS
class Stack(Base):
    __tablename__ = "Stack"

    id = Column(String, primary_key= True)
    name = Column(String)
    create_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=True)