# mail_sync_manager.py

from .mail_fetcher import fetch_all_mails, fetch_today_mails, get_user_email
from .mail_uploader import check_user_exists

def sync_user_mail(access_token: str):
    user_email = get_user_email(access_token)

    if not check_user_exists(user_email):
        print(f"[초기 수집] {user_email} 전체 메일 수집 시작")
        fetch_all_mails(access_token)
    else:
        print(f"[일일 수집] {user_email} 오늘 메일 수집 시작")
        fetch_today_mails(access_token)
