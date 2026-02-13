from sqlalchemy import Column,String, DateTime
from app.db.base import Base

#CLASE DE LA BASE DE DATOS
class Language(Base):
    __tablename__ = "Language"

    id = Column(String, primary_key= True)
    name = Column(String)
    create_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=True)