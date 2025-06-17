# MS Graph API 연동 (메일 수신 확인)
## Graph API 호출 및 토큰 관리

import requests
from dotenv import load_dotenv 
from datetime import datetime, timedelta
import pytz
import os
import msal

load_dotenv()

# === Azure 앱 등록 정보 ===
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
GRAPH_API_BASE =  os.getenv("GRAPH_API_BASE")

# === Microsoft Graph 설정 ===
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Mail.Read"]

# === 2. MSAL 앱 초기화 ===
app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)


import httpx
from fastapi import HTTPException

async def get_user_messages(access_token: str, top: int = 10):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?$top={top}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

def get_today_emails(access_token):
    # 오늘 날짜 (한국 시간 기준)
    now = datetime.now(pytz.timezone("Asia/Seoul"))
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    url = (
        f"{GRAPH_API_BASE}/me/messages"
        f"?$filter=receivedDateTime ge {start_of_day.isoformat()} and "
        f"receivedDateTime lt {end_of_day.isoformat()}"
        "&$top=50&$select=subject,receivedDateTime,from,body"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Prefer": "outlook.body-content-type='text'"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])