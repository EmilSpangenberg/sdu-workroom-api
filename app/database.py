from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import DATABASE_URL

# Connection pool: Handles many concurrent connections
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # 10 ready-to-use connections
    max_overflow=20,       # Up to 20 extra at peak load
    pool_pre_ping=True,    # Check connection health before use
    pool_recycle=3600,     # Recreate connections every hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Creates one database session per request.
    Closes the session automatically when the request is complete.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
