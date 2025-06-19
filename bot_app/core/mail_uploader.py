# app/core/blob_storage.py

import os
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from typing import List
import requests
from datetime import datetime
import json

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container = blob_service.get_container_client(BLOB_CONTAINER_NAME)

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# 사용자 이메일이 Blob Storage에 존재하는지 확인하는 함수 정의
STATUS_CONTAINER_NAME = os.getenv("STATUS_CONTAINER_NAME")
status_container = blob_service.get_container_client(STATUS_CONTAINER_NAME)

def check_user_exists(user_email: str) -> bool:

    print(f"🔍 Checking if user exists in Blob Storage: {user_email}")
    
    blob_prefix = f"{user_email}/"
    blob_list = container.list_blobs(name_starts_with=blob_prefix)
    
    return any(True for _ in blob_list)

# Blob Storage 저장하는 함수 정의
def save_mails_to_blob(user_email: str, mails: List[dict]) -> None:
    
    print("[*] Blob Storage에 메일 저장 시작...")

    for mail in mails:

        received = mail.get("receivedDateTime", "")[:10]  # yyyy-mm-dd
        message_id = mail.get("id", "unknown")
        blob_path = f"{user_email}/{received}/{message_id}.json"

        if container.get_blob_client(blob_path).exists():
            return  # 이미 저장된 메일은 skip

        cleaned_mail = {
            "id": message_id,
            "subject": mail.get("subject"),
            "from": mail.get("from", {}).get("emailAddress", {}).get("address", ""),
            "received": mail.get("receivedDateTime"),
            "bodyPreview": mail.get("bodyPreview"),
            "body": mail.get("body", {}).get("content", ""),
        }

        container.upload_blob(name=blob_path, data=json.dumps(cleaned_mail), overwrite=True)



# 메일을 AI Search에 인덱싱하고 저장하는 함수 정의
def save_mails_and_index_to_search(user_email: str, mails: List[dict]) -> None:

    print("[*] AI Search에 메일 인덱싱 시작...")
    
    for mail in mails:

        received = mail.get("receivedDateTime", "")[:10]  # yyyy-mm-dd
        message_id = mail.get("id", "unknown")

        subject = mail.get("subject")
        sender = mail.get("from", {}).get("emailAddress", {}).get("address", "")
        blob_path = f"{user_email}/{received}/{message_id}.json"

        content = mail.get("subject", "") + "\n" + mail.get("body", {}).get("content", "")

        # AI Search에 인덱싱할 문서 포맷
        document = {
            "id": message_id,
            "user_email": user_email,
            "date": mail.get("receivedDateTime"),
            "subject": subject,
            "sender": sender,
            "blob_path": blob_path,
            "content": content
        }

    
        headers = {
        "Content-Type": "application/json",
        "api-key": SEARCH_KEY
        }

        payload = { "value": [document] }

        url = f"{SEARCH_ENDPOINT}/indexes/{INDEX_NAME}/docs/index?api-version=2023-11-01"
        
        res = requests.post(url, headers=headers, json=payload)
        return res.raise_for_status()


def set_mail_status(user_email: str, status: str):
    blob_name = f"{user_email}.json"

    data = {
        "status": status,
        "timestamp": datetime.utcnow().isoformat() 
    }
    status_container.upload_blob(
        name=blob_name,
        data=json.dumps(data),
        overwrite=True
    )



def get_mail_status(user_email: str) -> str:
    
    blob_name = f"{user_email}.json"
    
    print(f"🔍 Checking mail status for user: {user_email}")

    try:

        blob_client = status_container.get_blob_client(blob_name)
        if not blob_client.exists():
            print(f"⚠️ Blob {blob_name} does not exist.")
            return "not_found"

        print(f"📥 Downloading blob: {blob_name}")
        blob_data = blob_client.download_blob().readall()
        data = json.loads(blob_data)
        status = data.get("status", "unknown")
        print(f"✅ Status: {status}")
        return status

    except Exception as e:
        print(f"❌ Error reading {blob_name}: {e}")
        return "error"
