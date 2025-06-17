from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from graph_client import get_user_messages

app = FastAPI()
security = HTTPBearer()

@app.post("/sync-mails")
async def sync_mails(credentials: HTTPAuthorizationCredentials = Depends(security)):
    access_token = credentials.credentials
    messages = await get_user_messages(access_token)
    subjects = [msg["subject"] for msg in messages.get("value", [])]
    return {"message_count": len(subjects), "subjects": subjects}
