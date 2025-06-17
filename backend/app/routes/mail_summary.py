from fastapi import APIRouter, Request
from app.services.graph_client import get_today_emails

router = APIRouter()

@router.get("/summary")
def get_today_summary(request: Request):
    access_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    emails = get_today_emails(access_token)
    # 이후 summarizer로 넘김
    return {"count": len(emails), "sample": emails[:1]}