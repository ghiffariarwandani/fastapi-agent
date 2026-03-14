from sqlmodel import Session, select

from app.models.database import ChatMessage


def get_messages(db: Session, session_id: int):
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return db.exec(stmt).all()

def create_message(db: Session, payload: dict) -> None:
    db.add(
        ChatMessage(
            session_id=payload["session_id"],
            role=payload["role"],
            content=payload["content"],
            message_type=payload["message_type"],
            tool_name=payload.get("tool_name"),
            tool_call_id=payload.get("tool_call_id"),
        )
    )
    db.commit()
