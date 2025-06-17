import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from util.graph_helper import get_user_principal_name
from core.mail_uploader import save_mails_to_blob, save_mails_to_embed_and_store
from core.mail_uploader import set_mail_status

load_dotenv()

GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"


async def fetch_today_mails(access_token: str) -> str:
    
    user_email = get_user_principal_name(access_token)
    
    print(f"📧 Fetching today's mails for user: {user_email}")

    today = datetime.utcnow().date()
    today_start = f"{today}T00:00:00Z"

    # url = f"{GRAPH_API_ENDPOINT}/users/{user_email}/mailFolders/inbox/messages"
    url = f"{GRAPH_API_ENDPOINT}/me/mailFolders/inbox/messages"
    params = {
        "$filter": f"receivedDateTime ge {today_start}",
        "$select": "id,subject,bodyPreview,receivedDateTime,from,body",
        "$orderby": "receivedDateTime desc",
        "$top": 50
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Prefer": 'outlook.body-content-type="text"'
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    mails = response.json().get("value", [])

    print(f"📬 Fetched {len(mails)} mails for today.")

    return mails

# 전체 메일을 가져오는 함수 (보관함 / 아카이브)
async def fetch_all_mails(access_token: str, folders: list[str] = ["inbox", "archive"]) :
    
    user_email = get_user_principal_name(access_token)

    try :
        set_mail_status(user_email, "pending")
        print(f"📧 Fetching all mails for user: {user_email}")

        headers = {
        "Authorization": f"Bearer {access_token}",
        "Prefer": 'outlook.body-content-type="text"'
        }
        
        BATCH_SIZE = 50  # 한 번에 가져올 메일 수

        for folder in folders:
            print(f"📦 Fetching from folder: {folder}")
            
            url = f"{GRAPH_API_ENDPOINT}/users/{user_email}/mailFolders/{folder}/messages"
            params = {
                "$select": "id,subject,bodyPreview,receivedDateTime,from,body",
                "$orderby": "receivedDateTime desc",
                "$top": BATCH_SIZE
            }

            while url:

                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                batch_mails = data.get("value", [])

                print(f"📦 batch_mails 타입: {type(batch_mails)}")  # 확인용
                
                # # 50개씩 묶어서 저장
                if batch_mails:
                    save_mails_to_blob(user_email, batch_mails)
                    save_mails_to_embed_and_store(user_email, batch_mails)

                url = data.get("@odata.nextLink")  # 다음 페이지 URL
                params = None
            
            print(f"📦 Finished fetching from folder: {folder}")
            set_mail_status(user_email, "done")

    except Exception as e:
        set_mail_status(user_email, "error")
        print(f"❌ {user_email} 수집 실패: {e}")
    
    

    

    