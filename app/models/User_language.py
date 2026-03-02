from sqlalchemy import Column, ForeignKey, Boolean, Table
from app.db.base import Base

#CLASE DE LA BASE DE DATOS
UserLanguage = Table(
    "User_language",
    Base.metadata,
    Column("user_id", ForeignKey("User.id"), primary_key=True),
    Column("language_id", ForeignKey("Language.id"), primary_key=True),
    Column("status", Boolean, default=True),
)