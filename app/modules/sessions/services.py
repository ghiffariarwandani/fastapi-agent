from sqlmodel import Session

from app.models.database import ChatSession


def create_session(db: Session):
    new_session = ChatSession()
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session
