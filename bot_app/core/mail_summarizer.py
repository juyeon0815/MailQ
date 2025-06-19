import os
from dotenv import load_dotenv
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from bs4 import BeautifulSoup
import urllib.parse
from util.llm_helper import generate_response

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
USER_ID = os.getenv("USER_ID")

blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container = blob_service.get_container_client(BLOB_CONTAINER_NAME)

def clean_html(html: str) -> str:
    """HTML 본문에서 텍스트만 추출"""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)

# escape 함수
def escape_markdown(text: str) -> str:
    return text.replace("[", "\\[").replace("]", "\\]")


def summarize_emails(emails: list[dict]) -> str:

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

        📌 요약 및 분류 규칙:

        1. 모든 메일을 다음 2가지 유형으로 정확히 분류하세요.

        📩 오늘 받은 메일 요약:
        → 사용자가 **확인 및 처리해야 하는 업무 관련 메일**만 여기에 넣으세요.
        - 예: 요청, 확인 부탁, 검토 요청, 기한 안내 등
        - 본문에 "제출 바랍니다", "확인 부탁드립니다", "요청드립니다", "검토해 주세요" 같은 표현이 있다면 반드시 이 항목에 포함하세요.

        📁 그 외 참고 메일:
        → 회신이나 조치가 필요 없는 **공지, 복무 공유, 단순 참고용 메일**은 여기에 포함하세요.

        2. 제목(subject)은 절대로 수정하지 말고, 그대로 링크에 사용하세요.
        예시:
        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})

        3. 요약 형식:

        📩 오늘 받은 메일 요약:

        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})  
        📜 메일 요약 및 할 일: [업무 요약 1줄]

        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})  
        📜 메일 요약 및 할 일: [업무 요약 1줄]

        📁 그 외 참고 메일:

        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})  
        - [{subject}](https://outlook.office.com/mail/deeplink/read/{id})

        ---

        ⚠️ 중복 금지  
        ⚠️ Output must be in **Korean only**  
        ⚠️ 각 요약은 반드시 1줄이며 명확하고 행동 중심적이어야 합니다  
        ⚠️ “요청 메일입니다” 같은 불필요한 문장은 절대 넣지 마세요
        ⚠️  문장형 요약 대신 짧고 명확한 액션 중심의 요약을 작성
        ⚠️  본문에 날짜가 시간 정보가 있다면 반드시 포함  
        """

    # 📌 1. 메일 콘텐츠 구성 (요약 대상)
    contents = []
    for mail in emails:
        subject = mail.get("subject", "제목 없음").strip()
        safe_subject = escape_markdown(subject)
        message_id = urllib.parse.quote_plus(mail["id"])
        body = mail.get("bodyPreview", "").strip()
        contents.append(f"제목: {safe_subject}\n id: {message_id}\n 내용: {body}\n")
     
    joined_contents = "\n\n---\n\n".join(contents)

    # 📌 2. LLM 호출
    llm_response = generate_response(prompt, joined_contents)
    
    return  llm_response.strip()