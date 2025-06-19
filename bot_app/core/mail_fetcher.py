import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from util.graph_helper import get_user_principal_name
from core.mail_uploader import save_mails_to_blob, save_mails_and_index_to_search
from core.mail_uploader import set_mail_status

load_dotenv()

GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"


def fetch_today_mails(access_token: str) -> list[dict]:
    print("📧 Fetching today's mails for current user (via /me)")

    # 한국 시간 기준 오늘 0시 → UTC로 변환
    now_kst = datetime.now(timezone(timedelta(hours=9)))
    today_kst = datetime(now_kst.year, now_kst.month, now_kst.day, tzinfo=timezone(timedelta(hours=9)))
    today_start_utc = today_kst.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    print(f"📅 Filtering mails since (UTC): {today_start_utc}")

    url = f"{GRAPH_API_ENDPOINT}/me/mailFolders/inbox/messages"
    params = {
        "$filter": f"receivedDateTime ge {today_start_utc}",
        "$select": "id,subject,bodyPreview,receivedDateTime,from,body",
        "$orderby": "receivedDateTime desc",
        "$top": 50
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Prefer": 'outlook.body-content-type="text"'
    }

    all_mails = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        mails = data.get("value", [])
        all_mails.extend(mails)

        print(f"📬 Fetched {len(mails)} mails from page")

        url = data.get("@odata.nextLink")
        params = None

    print(f"📬 총 {len(all_mails)}개의 메일 수집 완료")

    return all_mails

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
                
                # 50개씩 묶어서 저장
                if batch_mails:
                    save_mails_to_blob(user_email, batch_mails)
                    save_mails_and_index_to_search(user_email, batch_mails)

                url = data.get("@odata.nextLink")  # 다음 페이지 URL
                params = None
            
            print(f"📦 Finished fetching from folder: {folder}")
            set_mail_status(user_email, "done")

    except Exception as e:
        set_mail_status(user_email, "error")
        print(f"❌ {user_email} 수집 실패: {e}")
    
    

    

    