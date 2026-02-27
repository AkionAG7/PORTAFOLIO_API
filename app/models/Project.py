from sqlalchemy import Column,String, DateTime, ARRAY, Boolean
from sqlalchemy.orm import Relationship
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


#CLASE DE LA BASE DE DATOS
class Project(Base):
    __tablename__ = "Project"

    id = Column(UUID(as_uuid=True), primary_key= True, default= uuid.uuid4)
    name = Column(String)
    description = Column(String)
    repository_link = Column(String, nullable=True)
    deploy_link = Column(String, nullable=True)
    image_link = Column(ARRAY(String), nullable=True)
    status= Column(Boolean, default=True)
    create_at = Column(DateTime, nullable=True)
    update_at = Column(DateTime, nullable=True)
    #Relaciones
    user = Relationship("User", back_populates="Project")
