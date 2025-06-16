# test_summarizer.py

from bot_app.core.mail_summarizer import load_today_emails, summarize_emails

if __name__ == "__main__":
    emails = load_today_emails()
    summary = summarize_emails(emails)
    print(summary)
