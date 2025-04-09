from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = f"postgresql://postgres:postgres@localhost:5440/crypkit_db"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
