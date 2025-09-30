from sqlalchemy.orm import declarative_base
from app.db.session import SessionLocal

Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()