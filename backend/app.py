from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

from privacy import PIISanitizer
from imap_service import IMAPService
from ai_service import AIService

load_dotenv()

app = Flask(__name__)
CORS(app)

# Rate Limiter setup (In-memory storage)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

sanitizer = PIISanitizer()

# Handle Rate Limit Exceeded Errors
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "success": False,
        "error": f"Rate limit reached ({e.description}). Please wait before sending more requests."
    }), 429

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "service": "MailMind AI Backend"})

@app.route("/api/emails/fetch", methods=["POST"])
@limiter.limit("5 per minute")  # Prevents rapid IMAP spamming
def fetch_emails():
    data = request.json or {}
    email_user = data.get("email")
    app_pass = data.get("app_password")
    imap_server = data.get("imap_server", "imap.gmail.com")
    limit = int(data.get("limit", 5))

    if not email_user or not app_pass:
        return jsonify({"success": False, "error": "Email and App Password are required"}), 400

    res = IMAPService.fetch_emails(email_user, app_pass, imap_server, limit)
    return jsonify(res)

@app.route("/api/ai/analyze", methods=["POST"])
@limiter.limit("15 per minute")  # Protects free API quotas
def analyze():
    data = request.json or {}
    email_item = data.get("email")
    provider = data.get("provider", "groq")
    redact_pii = data.get("redact_pii", True)

    if not email_item:
        return jsonify({"success": False, "error": "No email data provided"}), 400

    audit_log = {}
    if redact_pii:
        email_item["body"], audit_log = sanitizer.sanitize(email_item.get("body", ""))
        email_item["subject"], _ = sanitizer.sanitize(email_item.get("subject", ""))

    try:
        analysis_result = AIService.analyze_email(email_item, provider=provider)
        return jsonify({
            "success": True,
            "analysis": analysis_result,
            "pii_audit": audit_log
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)