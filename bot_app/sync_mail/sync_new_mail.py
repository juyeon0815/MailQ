# outlook_bot_app/sync_mail/sync_new_mail.py

import os
from core.mail_fetcher import fetch_today_mails
from core.blob_uploader import save_mail_to_blob

USER_ID = os.getenv("USER_ID")

if __name__ == "__main__":
    print("[*] 오늘 받은 메일 수집 시작...")
    mails = fetch_today_mails(USER_ID)

    for mail in mails:
        save_mail_to_blob(USER_ID, mail)

    print(f"[+] 오늘 메일 {len(mails)}건 저장 완료.")
