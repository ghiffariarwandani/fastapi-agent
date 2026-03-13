from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.modules.chats.router import chat_router
from app.modules.sessions.router import session_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(session_router)


@app.get("/scalar")
def scalar():
    return get_scalar_api_reference(openapi_url=app.openapi_url)
