from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class ChatSession(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)


class ChatMessage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chatsession.id")
    role: str
    content: str
    created_at: datetime = datetime.now(timezone.utc)
