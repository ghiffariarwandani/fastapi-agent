from sqlmodel import Session, select

from app.models.database import ChatSession


def create_session(db: Session):
    new_session = ChatSession()
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_session_by_id(db: Session, session_id):
    stmt = select(ChatSession).where(ChatSession.id == session_id)
    result = db.exec(stmt).first()

    if result:
        return True

    return False
