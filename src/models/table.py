from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.core.db import Base


class TableModel(Base):
    __tablename__ = "tables"

    description = Column(Text, nullable=True)
    seats_number = Column(Integer, nullable=False)
    cafe = Column(Integer, ForeignKey("cafes.id"), nullable=False)
