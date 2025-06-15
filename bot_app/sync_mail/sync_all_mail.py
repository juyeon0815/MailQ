# outlook_bot_app/sync_mail/sync_all_mail.py

import os
from core.mail_fetcher import fetch_all_mails
from core.blob_uploader import save_mail_to_blob

USER_ID = os.getenv("USER_ID")

if __name__ == "__main__":
    print("[*] Inbox 메일 수집 시작...")
    inbox_mails = fetch_all_mails(USER_ID, folder_name="inbox")
    for mail in inbox_mails:
        save_mail_to_blob(USER_ID, mail)

    print("[*] Archive 메일 수집 시작...")
    archive_mails = fetch_all_mails(USER_ID, folder_name="archive")
    for mail in archive_mails:
        save_mail_to_blob(USER_ID, mail)

    print(f"[+] 총 {len(inbox_mails) + len(archive_mails)}건 저장 완료.")
