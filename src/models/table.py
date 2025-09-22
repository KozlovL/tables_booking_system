from sqlalchemy import Column, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.core.db import Base 


class TableModel(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    seats_number = Column(Integer, nullable=False)
    seats = Column(Integer, nullable=False)
    acive = Column(Boolean, default=True)
    cafe = Column(Integer, ForeignKey("cafes.id"), nullable=False)
