from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cryptocurrency as CryptocurrencyModel
from app.schemas import *
from app.coingecko import CoinGeckoService
from typing import List, Dict, Any

router = APIRouter()
coingecko_service = CoinGeckoService()

async def validate_cryptocurrency_platform(symbol: str, platform: str) -> None:
    """Validate that the platform exists for the given cryptocurrency symbol"""
    platforms_data = await coingecko_service.get_coins_platforms(symbol)
    
    if not platforms_data:
        raise HTTPException(
            status_code=400, 
            detail=f"No cryptocurrency with symbol {symbol} found on CoinGecko"
        )
        
    valid_platform = False
    for coin_id, platforms in platforms_data.items():
        if platform in platforms:
            valid_platform = True
            break
            
    if not valid_platform:
        raise HTTPException(
            status_code=400, 
            detail=f"Platform '{platform}' is not valid for cryptocurrency with symbol '{symbol}'"
        )

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

@router.get("/{cryptocurrency_id}/price")
async def get_cryptocurrency_price(
    cryptocurrency_id: int, 
    currency: str = "usd", 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get price for a specific cryptocurrency"""
    cryptocurrency = db.query(CryptocurrencyModel).filter(CryptocurrencyModel.id == cryptocurrency_id).first()
    if cryptocurrency is None:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    
    # Get price data
    coin_id = await coingecko_service.get_coin_id(
        cryptocurrency.symbol, cryptocurrency.platform
    )
    price_data = await coingecko_service.get_price(coin_id, currency)
    
    if not price_data or coin_id not in price_data:
        return {"symbol": cryptocurrency.symbol, "price": "N/A", "currency": currency}
    
    return {
        "symbol": cryptocurrency.symbol,
        "price": price_data[coin_id][currency],
        "currency": currency
    }

@router.post("/", response_model=Cryptocurrency)
async def create_cryptocurrency(
    cryptocurrency: CryptocurrencyCreate,
    db: Session = Depends(get_db)
) -> Cryptocurrency:
    """Create a new cryptocurrency"""
    db_cryptocurrency = db.query(CryptocurrencyModel).filter(
        CryptocurrencyModel.symbol == cryptocurrency.symbol,
        CryptocurrencyModel.platform == cryptocurrency.platform
    ).first()
    if db_cryptocurrency:
        raise HTTPException(status_code=400, detail="Cryptocurrency already registered")
    
    await validate_cryptocurrency_platform(cryptocurrency.symbol, cryptocurrency.platform)
    
    db_cryptocurrency = CryptocurrencyModel(**cryptocurrency.model_dump())

    db.add(db_cryptocurrency)
    db.commit()
    db.refresh(db_cryptocurrency)
    return db_cryptocurrency

@router.put("/{cryptocurrency_id}", response_model=Cryptocurrency)
async def update_cryptocurrency(
    cryptocurrency_id: int,
    cryptocurrency: CryptocurrencyUpdate,
    db: Session = Depends(get_db)
) -> Cryptocurrency:
    """Update a cryptocurrency"""
    db_cryptocurrency = db.query(CryptocurrencyModel).filter(CryptocurrencyModel.id == cryptocurrency_id).first()
    if db_cryptocurrency is None:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    
    await validate_cryptocurrency_platform(cryptocurrency.symbol, cryptocurrency.platform)
    
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