from sqlalchemy import Column,String, DateTime, ARRAY
from app.db.base import Base

#CLASE DE LA BASE DE DATOS
class Contact(Base):
    __tablename__ = "Contact"

    id = Column(String, primary_key= True)
    name = Column(String)
    description = Column(String)
    repository_link = Column(String, nullable=True)
    deploy_link = Column(String, nullable=True)
    image_link = Column(ARRAY(String), nullable=True)
    create_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=True)
