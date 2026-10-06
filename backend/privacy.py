import re

class PIISanitizer:
    def __init__(self):
        self.patterns = {
            "EMAIL": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "PHONE": r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
            "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b'
        }

    def sanitize(self, text: str) -> tuple[str, dict]:
        sanitized_text = text
        audit_log = {}

        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, sanitized_text)
            if matches:
                audit_log[pii_type] = len(matches)
                sanitized_text = re.sub(pattern, f"[{pii_type}_REDACTED]", sanitized_text)

        return sanitized_text, audit_log