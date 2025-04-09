from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cryptocurrency as CryptocurrencyModel
from app.schemas import *
from typing import List

router = APIRouter()

@router.get("/")
async def list_cryptocurrencies(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Cryptocurrency]:
    """List all cryptocurrencies"""
    cryptocurrencies = db.query(CryptocurrencyModel).offset(offset).limit(limit).all()
    return cryptocurrencies

@router.get("/{cryptocurrency_id}", response_model=Cryptocurrency)
async def get_cryptocurrency(
    cryptocurrency_id: int,
    db: Session = Depends(get_db)
) -> Cryptocurrency:
    """Get a cryptocurrency by ID"""
    cryptocurrency = db.query(CryptocurrencyModel).filter(CryptocurrencyModel.id == cryptocurrency_id).first()
    if cryptocurrency is None:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    return cryptocurrency

@router.post("/", response_model=Cryptocurrency)
async def create_cryptocurrency(
    cryptocurrency: CryptocurrencyCreate,
    db: Session = Depends(get_db)
) -> Cryptocurrency:
    """Create a new cryptocurrency"""
    db_cryptocurrency = db.query(CryptocurrencyModel).filter(CryptocurrencyModel.symbol == cryptocurrency.symbol).first()
    if db_cryptocurrency:
        raise HTTPException(status_code=400, detail="Cryptocurrency already registered")
    
    db_cryptocurrency = CryptocurrencyModel(**cryptocurrency.model_dump())

    db.add(db_cryptocurrency)
    db.commit()
    db.refresh(db_cryptocurrency)
    return db_cryptocurrency

@router.put("/{cryptocurrency_id}", response_model=Cryptocurrency)
async def update_cryptocurrency(
    cryptocurrency_id: int,
    cryptocurrency: CryptocurrencyCreate,
    db: Session = Depends(get_db)
) -> Cryptocurrency:
    """Update a cryptocurrency"""
    db_cryptocurrency = db.query(CryptocurrencyModel).filter(CryptocurrencyModel.id == cryptocurrency_id).first()
    if db_cryptocurrency is None:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    
    for key, value in cryptocurrency.model_dump().items():
        setattr(db_cryptocurrency, key, value)
    
    db.commit()
    db.refresh(db_cryptocurrency)
    return db_cryptocurrency

@router.delete("/{cryptocurrency_id}", response_model=Cryptocurrency)
async def delete_cryptocurrency(
    cryptocurrency_id: int,
    db: Session = Depends(get_db)
) -> Cryptocurrency:
    """Delete a cryptocurrency"""
    db_cryptocurrency = db.query(CryptocurrencyModel).filter(CryptocurrencyModel.id == cryptocurrency_id).first()
    if db_cryptocurrency is None:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    
    db.delete(db_cryptocurrency)
    db.commit()
    return db_cryptocurrency