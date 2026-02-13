from sqlalchemy import Column,String, DateTime
from app.db.base import Base

#CLASE DE LA BASE DE DATOS
class Contact(Base):
    __tablename__ = "Contact"

    id = Column(String, primary_key= True)
    name = Column(String)
    link = Column(String)
    image = Column(String, nullable=True)
    create_at = Column(DateTime, nullable=True)
    create_at = Column(DateTime, nullable=True)