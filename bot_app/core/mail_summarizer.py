from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import json
from bs4 import BeautifulSoup
import urllib.parse
from util.llm_helper import generate_response

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
USER_ID = os.getenv("USER_ID")

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container = blob_service.get_container_client(BLOB_CONTAINER_NAME)

# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
#     base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
# )

# def load_today_emails(user_id=USER_ID):
#     today_str = datetime.utcnow().date().isoformat()
#     prefix = f"{user_id}/{today_str}/"

#     blobs = container.list_blobs(name_starts_with=prefix)
#     emails = []

#     for blob in blobs:
#         blob_data = container.get_blob_client(blob).download_blob().readall()
#         email = json.loads(blob_data)
#         emails.append(email)

#     return emails

def clean_html(html: str) -> str:
    """HTML 본문에서 텍스트만 추출"""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)

def summarize_emails(emails: list[dict]) -> str:

    if not emails:
        return "📭 오늘 받은 메일이 없습니다."
    
    prompt = """
            You are an AI assistant that summarizes email threads and extracts actionable tasks for the user.  
            Analyze the full email content (including multiple replies or forwards) and organize the output according to the following rules.  
            ⚠️ Please provide all answers in Korean.

            [Input Type]
            - Complete email bodies including multiple replies, forwards, or original messages
            - May include headers such as “FW:”, “RE:”, “-----Original Message-----”, -------------------------------, etc.

            [Processing Rules]
            1. Prioritize and summarize the most recent response or message in the thread.
            2. Analyze and outline the entire thread history in chronological order based on reply or forward history.
            3. Identify the purpose of each message (request, reply, confirmation, info-sharing, etc.).
            4. If the email is for simple notification, forwarding, or status sharing, explicitly state “할 일 없음 (No action needed)”.
            5. Generate action items only if there’s a clear and specific task the user needs to do. Avoid generating unnecessary to-do items.

            [Output Format]

            ---
            📩 제목: [Email Subject]  
            📌 최신 내용 요약:  
            - [가장 최근 회신의 요점 요약]  

            📜 메일 스레드 요약:  
            - [날짜, 보낸 사람] → [요청 / 회신 / 공유 등 메일 내용]  
            - …

            📝 할 일:  
            - [명확한 업무 지시가 있을 경우: 예. “테스트 일정 회신”]  
            - [단순 참고일 경우: “할 일 없음”]  
            - [판단이 필요한 경우: “검토 후 판단 필요”]

            ---

            [Notes]
            - Parse and understand replies, forwards, and nested message history
            - Avoid redundant or duplicate summaries
            - Only generate action items if truly required
            - If only one message exists, summarize that one
            - ⚠️ 모든 출력은 반드시 **한국어로 작성**할 것
            """

    # 📌 1. 메일 콘텐츠 구성 (요약 대상)
    contents = []
    for mail in emails:
        subject = mail.get("subject", "제목 없음").strip()
        body = mail.get("bodyPreview", "").strip()
        contents.append(f"제목: {subject}\n내용: {body}\n")

    
        
    joined_contents = "\n\n---\n\n".join(contents)


    # 📌 2. LLM 호출
    summary_text = generate_response(prompt, contents)

    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0.4
    # )

    # summary_text = response.choices[0].message.content

    # 📌 3. 링크 포함 메일 목록 헤더 구성
    header_text = "### 📩 오늘 받은 메일 요약\n\n"
    for idx, mail in enumerate(emails, 1):
        subject = mail.get("subject", "제목 없음").strip()
        message_id = urllib.parse.quote_plus(mail["id"])
        link = f"https://outlook.office.com/mail/deeplink/read/{message_id}"
        header_text += f"{idx}. {subject}\n   ▶ {link}\n\n"

    # 📌 4. 최종 결과 조합
    return header_text + "\n" + "### 요약 내용\n\n" + summary_text.strip()