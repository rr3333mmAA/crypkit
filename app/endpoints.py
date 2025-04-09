from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cryptocurrency

router = APIRouter()

@router.get("/")
def read_root(db: Session = Depends(get_db)):
    cryptocurrencies = db.query(Cryptocurrency).all()
    return cryptocurrencies