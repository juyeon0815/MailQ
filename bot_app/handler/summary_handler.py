from core.mail_fetcher import fetch_today_mails
# from core.blob_uploader import save_mail_to_blob
# from core.blob_checker import is_first_time_user
# from core.blob_loader import load_today_mails_from_blob
from core.mail_summarizer import summarize_emails
from datetime import datetime
# import asyncio

from dotenv import load_dotenv
import os

load_dotenv()

async def handle_summary_request(turn_context):

    # 테스트용으로 일단 임시로 환경 변수에서 토큰을 가져옵니다.
    # 실제로는 Teams 채널 데이터에서 토큰을 추출해야 합니다.

    access_token = os.getenv("ACCESS_TOKEN")
    
    # access_token = extract_access_token_from_context(turn_context)
    
    # user_email = get_user_email_from_token(access_token)

    today = datetime.utcnow().strftime("%Y-%m-%d")

    # 오늘 받은 메일을 가져옵니다.
    mails = fetch_today_mails(access_token)

    # 요약 먼저 해주고,
    summary = summarize_emails(mails)
    
    await turn_context.send_activity(summary)

    # 처음 실행한 사용자라면, 오늘 받은 메일을 저장하고 전체 메일도 백그라운드에서 수집합니다.




    # await turn_context.send_activity(mails)
    # for mail in mails:
    #     save_mail_to_blob(user_email, today, mail, access_token)

#     summary = summarize_emails(mails)
#     await turn_context.send_activity(summary)

#     if is_first_time_user(user_email):
#         await turn_context.send_activity("🔄 전체 메일도 백그라운드에서 수집 중입니다...")
#         asyncio.create_task(store_all_mails_async(user_email, access_token))


# async def store_all_mails_async(user_email: str, access_token: str):
#     all_mails = fetch_all_mails(access_token)
#     for mail in all_mails:
#         save_mail_to_blob(user_email, mail["date"], mail, access_token)
