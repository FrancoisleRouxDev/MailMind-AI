import os
import imaplib
import email
from email.header import decode_header
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)

# Helper function to decode email headers safely
def decode_mime_words(header_value):
    if not header_value:
        return ""
    decoded_fragments = decode_header(header_value)
    header_text = ""
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            header_text += fragment.decode(encoding or "utf-8", errors="ignore")
        else:
            header_text += fragment
    return header_text

# Helper function to extract plain text body from raw message
def extract_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode("utf-8", errors="ignore")
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="ignore")
        except Exception:
            pass
    return body.strip() or "No readable text content."

# Get AI client based on selected provider
def get_ai_client(provider):
    if provider == "nvidia":
        return OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        ), "microsoft/kosmos-2"
        
    elif provider == "groq":
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        ), "llama-3.3-70b-versatile"

    else:
        raise ValueError(f"Unsupported provider: {provider}")


# --- ROUTE 1: IMAP FETCH EMAILS ---
@app.route('/api/emails/fetch', methods=['POST'])
def fetch_emails():
    try:
        data = request.json or {}
        user_email = data.get("email")
        app_password = data.get("app_password")
        imap_server = data.get("imap_server", "imap.gmail.com")
        limit = int(data.get("limit", 3))

        if not user_email or not app_password:
            return jsonify({"success": False, "error": "Email and app password are required"}), 400

        # Connect to IMAP Server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(user_email, app_password)
        mail.select("INBOX")

        # Search for all recent emails
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            return jsonify({"success": False, "error": "Failed to search inbox"}), 500

        mail_ids = messages[0].split()
        latest_ids = mail_ids[-limit:]  # Get the last N emails
        fetched_emails = []

        for msg_id in reversed(latest_ids):
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw_msg = email.message_from_bytes(response_part[1])
                    subject = decode_mime_words(raw_msg.get("Subject", "No Subject"))
                    sender = decode_mime_words(raw_msg.get("From", "Unknown Sender"))
                    body = extract_email_body(raw_msg)

                    fetched_emails.append({
                        "id": msg_id.decode('utf-8'),
                        "subject": subject,
                        "sender": sender,
                        "body": body[:2000]  # Truncate to prevent token limit overload
                    })

        mail.logout()
        return jsonify({"success": True, "emails": fetched_emails})

    except imaplib.IMAP4.error as e:
        return jsonify({"success": False, "error": f"IMAP Auth Failed: {str(e)}"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --- ROUTE 2: AI ANALYSIS ---
@app.route('/api/ai/analyze', methods=['POST'])
def analyze_email():
    try:
        data = request.json or {}
        email_data = data.get("email", {})
        provider = data.get("provider", "nvidia")
        redact_pii = data.get("redact_pii", True)

        subject = email_data.get("subject", "No Subject")
        sender = email_data.get("sender", "Unknown Sender")
        body = email_data.get("body", "")

        client, model_name = get_ai_client(provider)

        prompt = f"""
        Analyze the following email:
        From: {sender}
        Subject: {subject}
        Body:
        {body}

        Format response:
        • Summary: (2 clear sentences)
        • Priority: (High / Medium / Low)
        • Action Items: (Bullet points or None)
        {"• Note: Redact any phone numbers, addresses, or SSNs." if redact_pii else ""}
        """

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a precise, concise executive email assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=400
        )

        analysis = response.choices[0].message.content

        return jsonify({
            "success": True,
            "analysis": analysis
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)