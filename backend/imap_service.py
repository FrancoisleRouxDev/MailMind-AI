import imaplib
import email
from email.header import decode_header

class IMAPService:
    @staticmethod
    def fetch_emails(user_email: str, app_password: str, imap_url: str = "imap.gmail.com", limit: int = 5):
        try:
            mail = imaplib.IMAP4_SSL(imap_url)
            mail.login(user_email, app_password)
            mail.select("inbox")

            _, status = mail.search(None, "ALL")
            email_ids = status[0].split()[-limit:]
            
            emails_list = []

            for e_id in reversed(email_ids):
                _, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject_raw = msg.get("Subject", "No Subject")
                        subject, encoding = decode_header(subject_raw)[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8", errors="ignore")
                        
                        sender = msg.get("From", "Unknown Sender")
                        
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        
                        emails_list.append({
                            "id": e_id.decode("utf-8"),
                            "subject": str(subject),
                            "sender": str(sender),
                            "body": body[:3000]  # Safe token cap
                        })

            mail.close()
            mail.logout()
            return {"success": True, "emails": emails_list}
        except Exception as e:
            return {"success": False, "error": str(e)}