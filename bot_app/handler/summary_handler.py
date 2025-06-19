from core.mail_fetcher import fetch_today_mails
from core.mail_uploader import save_mails_to_blob, save_mails_and_index_to_search
from core.mail_summarizer import summarize_emails
from util.graph_helper import get_user_principal_name
from dotenv import load_dotenv

load_dotenv()


def handle_summary_request(turn_context, access_token: str):
    
    user_email = get_user_principal_name(access_token)

    print("🔑 오늘 받은 메일을 가져옵니다.")
    
    # 오늘 받은 메일을 가져옵니다.
    mails = fetch_today_mails(access_token)

    # # blob에 저장 및 임베딩
    save_mails_to_blob(user_email, mails)
    save_mails_and_index_to_search(user_email, mails)
    
    # print("🔑 오늘 받은 메일을 요약합니다.")
    summary = summarize_emails(mails)

    print("📬 오늘 받은 메일 리턴", mails)
    
    return turn_context.send_activity(summary)

    

    
    
    
