from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cryptocurrency(Base):
    __tablename__ = "cryptocurrency"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    platform = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('symbol', 'platform', name='uq_symbol_platform'),
    )