from sqlalchemy import create_engine,event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.config import setting
import logging


logger = logging.getLogger(__name__)

engine = create_engine(
    setting.DATABASE_URL,
    pool_size=setting.DB_POOL_SIZE,
    max_overflow=setting.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, connection_record):
    logger.info("Database connection established")

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
