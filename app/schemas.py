from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CryptocurrencyBase(BaseModel):
    symbol: str

class CryptocurrencyCreate(CryptocurrencyBase):
    pass

class CryptocurrencyUpdate(BaseModel):
    symbol: Optional[str] = None

class CryptocurrencyInDB(CryptocurrencyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Cryptocurrency(CryptocurrencyInDB):
    pass