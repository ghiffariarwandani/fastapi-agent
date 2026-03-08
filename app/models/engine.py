from sqlmodel import Session, create_engine

from app.core.settings import settings

engine = create_engine(url=settings.database_url)

def get_db():
  with Session(engine) as session:
    yield session
