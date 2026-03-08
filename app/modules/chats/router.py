from agents import Agent, Runner
from fastapi import APIRouter, Depends
from sqlmodel import select

from app.models.database import ChatMessage
from app.models.engine import get_db
from app.modules.agents.model import llm_model
from app.modules.agents.prompt import SYSTEM_PROMPT
from app.modules.sessions.services import create_session

from .schema import ChatRequest

chat_router = APIRouter(prefix="/chat")

@chat_router.post("/")
def generate_answer(request: ChatRequest, db =  Depends(get_db)):
  if request.session_id != 0:
    agent = Agent("Assistant", instructions=SYSTEM_PROMPT, model=llm_model)

    stmt = (
      select(ChatMessage)
      .where(ChatMessage.session_id == request.session_id)
      .order_by(ChatMessage.created_at.asc())
    )
    result = db.exec(stmt).all()

    runner = Runner.run_streamed(agent, input=result)

  else:
    create_session(db)


