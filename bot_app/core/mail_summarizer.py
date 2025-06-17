import os
from dotenv import load_dotenv
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from bs4 import BeautifulSoup
import urllib.parse
from util.llm_helper import generate_response
import re
import json

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
USER_ID = os.getenv("USER_ID")

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container = blob_service.get_container_client(BLOB_CONTAINER_NAME)

async def clean_html(html: str) -> str:
    """HTML 본문에서 텍스트만 추출"""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)

async def summarize_emails(emails: list[dict]) -> str:

    print(f"📧 요약할 메일 개수: {len(emails)}")

    if not emails:
        return "📭 오늘 받은 메일이 없습니다."
    
    prompt = """
        You are an expert assistant that summarizes email threads for a busy professional. Your job is to extract only the essential tasks and summarize them clearly, helping the user efficiently review what matters today.

        Each input contains multiple email threads in the format: recipient(s), sender, subject, date, content, and a unique `id`.

        The `id` field is used to construct a mail link as:
        https://outlook.office.com/mail/deeplink/read/{id}

        Please generate this link and attach it as a **Markdown hyperlink to the {subject}** (e.g., [{subject}](https://...)).

        ---

        📌 SUMMARY RULES:

        1. Summarize each email only if:
        - The user is a **direct recipient** (not just CC).
        - The message includes **requests**, **deadlines**, or **work-related actions**.
        - Even if the subject line seems like a general sharing (e.g., includes "복무 공유", "참고", "공유"), do **not automatically exclude** it.
        Use your judgment:
            - If the **body** contains phrases like “제출 바랍니다”, “확인 부탁드립니다”, “검토해 주세요”, treat it as actionable.
            - Otherwise, place it under 참고 메일.

        2. For each valid email:
        - Identify the action item and summarize it concisely in one line like:
        📜 메일 요약 및 할 일:  
        - 📌 간단한 업무 요약 (기한 포함 시 함께 명시)

        - Do not rewrite or modify the subject. Use it exactly as received to preserve ID mapping.

        3. Output format:

        📩 오늘 받은 메일 요약 :

        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})

        📜 메일 요약 및 할 일: [업무 요약]

        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})  

        📜 메일 요약 및 할 일: [업무 요약]

        4. At the end, list non-actionable emails under:

        📁 그 외 참고 메일 :  
        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})  
        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})  

        ---

        ⚠️ DO NOT include lines like “요청 메일입니다.”  
        ⚠️ Output must be in **Korean only**.  
        ⚠️ Each summary must be one line, clear, and action-oriented.
        """


    # 📌 1. 메일 콘텐츠 구성 (요약 대상)
    contents = []
    for mail in emails:
        subject = mail.get("subject", "제목 없음").strip()
        message_id = urllib.parse.quote_plus(mail["id"])
        body = mail.get("bodyPreview", "").strip()
        contents.append(f"제목: {subject}\n id: {message_id}\n 내용: {body}\n")
     
    joined_contents = "\n\n---\n\n".join(contents)

    # 📌 2. LLM 호출
    llm_response = await generate_response(prompt, joined_contents)
    
    return  llm_response.strip()