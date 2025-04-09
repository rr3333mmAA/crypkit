from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cryptocurrency as CryptocurrencyModel
from app.schemas import Cryptocurrency
from typing import List

router = APIRouter()

@router.get("/")
async def read_cryptocurrencies(
    db: Session = Depends(get_db)
) -> List[Cryptocurrency]:
    """Get all cryptocurrencies."""
    cryptocurrencies = db.query(CryptocurrencyModel).all()
    return cryptocurrencies