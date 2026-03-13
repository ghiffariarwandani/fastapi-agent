import json

from agents import Agent, RawResponsesStreamEvent, RunItemStreamEvent, Runner
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai.types.responses import ResponseFunctionToolCall, ResponseTextDeltaEvent
from sqlmodel import Session, select

from app.models.database import ChatMessage
from app.models.engine import get_db
from app.modules.agents.model import llm_model
from app.modules.agents.prompt import SYSTEM_PROMPT
from app.modules.agents.tools import search_web
from app.modules.sessions.services import create_session

from .schema import ChatRequest

chat_router = APIRouter(prefix="/chat")


@chat_router.post("/")
async def generate_answer(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id
    if session_id == 0:
      session = create_session(db)
      session_id = session.id

    agent = Agent(
      "Assistant",
      instructions=SYSTEM_PROMPT,
      model=llm_model,
      tools=[search_web],
    )

    stmt = (
      select(ChatMessage)
      .where(ChatMessage.session_id == session_id)
      .order_by(ChatMessage.created_at.asc())
    )
    result = db.exec(stmt).all()

    messages = [
      {
        "role": row.role,
        "content": row.content,
      }
      for row in result
      if row.message_type == "text"
    ]

    db.add(
      ChatMessage(
        session_id=session_id,
        role="user",
        content=request.message,
        message_type="text",
      )
    )
    db.commit()

    messages.append(
      {
        "role": "user",
        "content": request.message,
      }
    )

    runner = Runner.run_streamed(agent, input=messages)

    async def event_generator():
      chunks: list[str] = []

      async for event in runner.stream_events():
        if (
          isinstance(event, RawResponsesStreamEvent)
          and isinstance(event.data, ResponseTextDeltaEvent)
        ):
          print(event.data.delta)
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

