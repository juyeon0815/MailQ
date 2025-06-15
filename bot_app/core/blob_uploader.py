# app/core/blob_storage.py

import os
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from .embedding_helper import embed_and_store

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container = blob_service.get_container_client(BLOB_CONTAINER_NAME)
container_name = "emails"

def check_user_exists(user_email: str) -> bool:
    
    blob_prefix = f"{user_email}/"
    blob_list = container.get_container_client(container_name).list_blobs(name_starts_with=blob_prefix)

    return any(True for _ in blob_list)


def save_email_to_blob(user_id: str, mail: dict) -> None:
    print("blob 저장 중...")

    """
    이메일 데이터를 Blob Storage에 저장
    """
    received = mail.get("receivedDateTime", "")[:10]  # yyyy-mm-dd
    message_id = mail.get("id", "unknown")
    blob_path = f"{user_id}/{received}/{message_id}.json"

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

    container.upload_blob(name=blob_path, data=json.dumps(cleaned_mail), overwrite=False)

    # Chroma 벡터 저장
    embed_and_store(user_id, message_id, mail)
    print("저장?")
    
    print(f"✅ Saved: {blob_path}")
