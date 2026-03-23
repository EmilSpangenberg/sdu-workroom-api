from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import DATABASE_URL

# Connection pool: Håndterer mange samtidige forbindelser
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # 10 forbindelser klar til brug
    max_overflow=20,       # Op til 20 ekstra ved spidsbelastning
    pool_pre_ping=True,    # Tjek om forbindelse virker før brug
    pool_recycle=3600,     # Genopret forbindelser hver time
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Opretter en database session per request.
    Lukker automatisk når request er færdig.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
