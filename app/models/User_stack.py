from sqlalchemy import Column, ForeignKey, Boolean

from app.db.base import Base

#CLASE DE LA BASE DE DATOS
class UserStack(Base):
    __tablename__ = "User_stack"
    Base.metadata,
    user_id = Column("user_id", ForeignKey("User.id"), primary_key= True)
    stack_id = Column("stack_id", ForeignKey("Stack.id"), primary_key= True)
    status= Column(Boolean, default=True)
