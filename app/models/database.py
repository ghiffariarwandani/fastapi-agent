from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChatSession(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    title: str | None = None


class ChatMessage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chatsession.id")
    role: str
    content: str
    created_at: datetime = Field(default_factory=utc_now)
    message_type: str
    tool_name: str | None = None
    tool_call_id: str | None = None
