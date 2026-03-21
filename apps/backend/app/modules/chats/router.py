import json
from pathlib import Path

from agents import Agent, RawResponsesStreamEvent, RunItemStreamEvent, Runner
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from openai.types.responses import ResponseFunctionToolCall, ResponseTextDeltaEvent
from sqlmodel import Session

from app.core.settings import settings
from app.models.database import ChatMessage
from app.models.engine import get_db
from app.modules.agents.model import llm_model
from app.modules.agents.prompt import SYSTEM_PROMPT
from app.modules.agents.tools import search_web
from app.modules.sessions.services import create_session, get_session_by_id

from .schema import ChatRequest
from .services import create_message, get_messages

chat_router = APIRouter(prefix="/chat")

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@chat_router.post("/")
async def generate_answer(request: ChatRequest, db: Session = Depends(get_db)):
  if len(request.message.strip()) == 0:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message is required")

  session_id = request.session_id
  if session_id == 0:
    session = create_session(db)
    session_id = session.id

  is_session_id = get_session_by_id(db, session_id)

  if not is_session_id:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


  history_messages = get_messages(db, session_id)

  messages = [
    {
      "role": row.role,
      "content": row.content,
    }
    for row in history_messages
    if row.message_type == "text"
  ]

  user_content = request.message
  if request.file_path:
    base_dir = UPLOAD_DIR.resolve()
    target = Path(request.file_path).resolve()
    if not str(target).startswith(str(base_dir)):
      raise HTTPException(status_code=400, detail="Invalid file_path")
    if not target.exists() or not target.is_file():
      raise HTTPException(status_code=404, detail="Uploaded file not found")
    try:
      file_text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
      raise HTTPException(status_code=400, detail="Uploaded file must be UTF-8 text")
    user_content = f"{request.message}\n\nAttached file contents:\n{file_text}"

  messages.append({"role": "user", "content": user_content})

  create_message(db, {
    "session_id": session_id,
    "role": "user",
    "content": request.message,
    "message_type": "text"
  })

  agent = Agent(
    "Assistant",
    instructions=SYSTEM_PROMPT,
    model=llm_model,
    tools=[search_web],
  )

  runner = Runner.run_streamed(agent, input=messages)

  async def event_generator():
    chunks: list[str] = []

    async for event in runner.stream_events():
      if (
        isinstance(event, RawResponsesStreamEvent)
        and isinstance(event.data, ResponseTextDeltaEvent)
      ):
        if event.data.delta:
          chunks.append(event.data.delta)
          payload = {
            "type": "text_delta",
            "delta": event.data.delta,
            "session_id": session_id,
          }
          yield f"data: {json.dumps(payload)}\n\n"

      elif (
        isinstance(event, RunItemStreamEvent)
        and event.name == "tool_called"
        and isinstance(event.item.raw_item, ResponseFunctionToolCall)
      ):
        raw_item = event.item.raw_item
        db.add(
          ChatMessage(
            session_id=session_id,
            role="assistant",
            content=raw_item.arguments,
            message_type="tool_call",
            tool_name=raw_item.name,
            tool_call_id=raw_item.call_id,
          )
        )
        db.commit()

        payload = {
          "type": "tool_call",
          "tool_name": raw_item.name,
          "argument": raw_item.arguments,
          "tool_call_id": raw_item.call_id,
          "session_id": session_id,
        }
        yield f"data: {json.dumps(payload)}\n\n"

    final_text = "".join(chunks).strip()

    if final_text:
      db.add(
        ChatMessage(
          session_id=session_id,
          role="assistant",
          content=final_text,
          message_type="text",
        )
      )
      db.commit()

      yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

  return StreamingResponse(event_generator(), media_type="text/event-stream")
