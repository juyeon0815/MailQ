from core.mail_fetcher import fetch_today_mails
from core.mail_uploader import save_mails_to_blob, save_mails_to_embed_and_store
from core.mail_summarizer import summarize_emails
from util.graph_helper import get_user_principal_name
from dotenv import load_dotenv
import os

load_dotenv()


async def handle_summary_request(turn_context):

    # 테스트용으로 일단 임시로 환경 변수에서 토큰을 가져옵니다.
    # 실제로는 Teams 채널 데이터에서 토큰을 추출해야 합니다.
    access_token = os.getenv("ACCESS_TOKEN")
    
    # access_token = extract_access_token_from_context(turn_context)
    user_email = await get_user_principal_name(access_token)

    print("🔑 오늘 받은 메일을 가져옵니다.")
    # 오늘 받은 메일을 가져옵니다.
    mails = await fetch_today_mails(access_token)

    # blob에 저장 및 임베딩
    save_mails_to_blob(user_email, mails)
    save_mails_to_embed_and_store(user_email, mails)
    
    print("🔑 오늘 받은 메일을 요약합니다.")
    summary = await summarize_emails(mails)

    print("📬 오늘 받은 메일 리턴")
    await turn_context.send_activity(summary)

    

    
    
    
