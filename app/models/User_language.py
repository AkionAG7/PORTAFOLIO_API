from sqlalchemy import Column, ForeignKey, Boolean, Table, String,Date
from app.db.base import Base

#CLASE DE LA BASE DE DATOS
UserLanguage = Table(
    "User_language",
    Base.metadata,
    Column("user_id", ForeignKey("User.id"), primary_key=True),
    Column("language_id", ForeignKey("Language.id"), primary_key=True),
    Column("level",String ),
    Column("status", Boolean, default=True),
    Column("created_at", Date, nullable=True),
    Column("updated_at", Date, nullable=True),

)