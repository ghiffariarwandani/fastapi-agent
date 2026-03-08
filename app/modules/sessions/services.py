from fastapi import Depends

from app.models.database import ChatSession
from app.models.engine import get_db


def create_session(db = Depends(get_db)):
    new_session = ChatSession()
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session
