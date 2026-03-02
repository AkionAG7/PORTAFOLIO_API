from sqlalchemy import Column, ForeignKey, Boolean, Table

from app.db.base import Base

#CLASE DE LA BASE DE DATOS
UserStack = Table (
    "User_stack",
    Base.metadata,
    Column("user_id", ForeignKey("User.id"), primary_key=True),
    Column("stack_id", ForeignKey("Stack.id"), primary_key=True),
    Column("status", Boolean, default=True),
)