from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.modules.chats.router import chat_router
from app.modules.sessions.router import session_router

app = FastAPI()

app.include_router(chat_router)
app.include_router(session_router)


@app.get("/scalar")
def scalar():
    return get_scalar_api_reference(openapi_url=app.openapi_url)
