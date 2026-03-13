from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.models.database import ChatSession
from app.models.engine import get_db
from app.utils.params import pagination

session_router = APIRouter(prefix="/chat-sessions")


@session_router.get("/")
def get_session(params=Depends(pagination), db: Session = Depends(get_db)):
    stmt = select(ChatSession)
    result = db.exec(stmt.offset(params["offset"]).limit(params["limit"])).all()
    return {"data": result, "message": "Success retrieve sessions"}
