from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import json
from bs4 import BeautifulSoup
import urllib.parse

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
USER_ID = os.getenv("USER_ID")

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container = blob_service.get_container_client(BLOB_CONTAINER_NAME)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
)

def load_today_emails(user_id=USER_ID):
    today_str = datetime.utcnow().date().isoformat()
    prefix = f"{user_id}/{today_str}/"

    blobs = container.list_blobs(name_starts_with=prefix)
    emails = []

    for blob in blobs:
        blob_data = container.get_blob_client(blob).download_blob().readall()
        email = json.loads(blob_data)
        emails.append(email)

    return emails

def clean_html(html: str) -> str:
    """HTML 본문에서 텍스트만 추출"""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)

def summarize_emails(emails: list[dict]) -> str:
    if not emails:
        return "📭 오늘 받은 메일이 없습니다."

    # 📌 1. 메일 콘텐츠 구성 (요약 대상)
    contents = []
    for mail in emails:
        subject = mail.get("subject", "제목 없음").strip()
        body = mail.get("bodyPreview", "").strip()
        contents.append(f"제목: {subject}\n내용: {body}\n")

    prompt = (
        "다음은 오늘 받은 이메일 목록입니다. 핵심 내용을 요약하고, 필요한 경우 해야 할 일을 정리해주세요.\n\n"
        + "\n---\n".join(contents)
    )

    # 📌 2. LLM 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    summary_text = response.choices[0].message.content

    # 📌 3. 링크 포함 메일 목록 헤더 구성
    header_text = "### 📩 오늘 받은 메일 요약\n\n"
    for idx, mail in enumerate(emails, 1):
        subject = mail.get("subject", "제목 없음").strip()
        message_id = urllib.parse.quote_plus(mail["id"])
        link = f"https://outlook.office.com/mail/deeplink/read/{message_id}"
        header_text += f"{idx}. {subject}\n   ▶ {link}\n\n"

    # 📌 4. 최종 결과 조합
    return header_text + "\n" + "### 요약 내용\n\n" + summary_text.strip()