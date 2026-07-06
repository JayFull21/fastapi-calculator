

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# In Docker Compose, the Postgres service is reachable at hostname "db"
# (the service name). Locally outside Docker, fall back to localhost.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/fastapi_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
