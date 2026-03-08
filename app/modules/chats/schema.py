from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: int
