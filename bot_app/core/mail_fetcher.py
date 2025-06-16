import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from util.graph_helper import get_user_principal_name
# from .blob_uploader import save_email_to_blob

load_dotenv()

GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"


def fetch_today_mails(access_token: str) -> list[dict]:
    
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

    print(mails)

    # for mail in mails:
    #     save_email_to_blob(user_email, mail)

    return mails

# def fetch_all_mails(access_token: str, folders: list[str] = ["inbox", "archive"]) -> list:
    
#     user_email = get_user_email(access_token)

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Prefer": 'outlook.body-content-type="text"'
#     }
    
#     mails = []

#     for folder in folders:
#         print(f"📦 Fetching from folder: {folder}")
        
#         url = f"{GRAPH_API_ENDPOINT}/users/{user_email}/mailFolders/{folder}/messages"
        
#         params = {
#             "$select": "id,subject,bodyPreview,receivedDateTime,from,body",
#             "$orderby": "receivedDateTime desc",
#             "$top": 50
#         }

#         while url:
#             response = requests.get(url, headers=headers, params=params)
#             response.raise_for_status()
#             data = response.json()

#             mails = data.get("value", [])
#             mails.extend(mails)

#             for mail in mails:
#                 save_email_to_blob(user_email, mail)

#             url = data.get("@odata.nextLink")  # 페이징 처리

#     return mails

# def get_all_mail_folders():
#     token = get_graph_token()
#     headers = {"Authorization": f"Bearer {token}"}
#     url = f"{GRAPH_API_ENDPOINT}/users/{USER_ID}/mailFolders"
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     folders = response.json().get("value", [])
#     return folders


# def fetch_mails_from_folder(folder_id, start_datetime: str = None, end_datetime: str = None):
#     token = get_graph_token()
#     headers = {"Authorization": f"Bearer {token}"}

#     url = f"{GRAPH_API_ENDPOINT}/users/{USER_ID}/mailFolders/{folder_id}/messages"
#     params = {
#         "$select": "id,subject,bodyPreview,receivedDateTime,from,body",
#         "$orderby": "receivedDateTime desc",
#         "$top": 50
#     }

#     if start_datetime:
#         filter_str = f"receivedDateTime ge {start_datetime}"
#         if end_datetime:
#             filter_str += f" and receivedDateTime lt {end_datetime}"
#         params["$filter"] = filter_str

#     all_mails = []
#     while url:
#         response = requests.get(url, headers=headers, params=params)
#         response.raise_for_status()
#         data = response.json()
#         all_mails.extend(data.get("value", []))
#         url = data.get("@odata.nextLink", None)
#         params = None

#     return all_mails
