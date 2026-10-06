import os
from openai import OpenAI
from google import genai

class AIService:
    @staticmethod
    def analyze_email(email_data: dict, provider: str = "groq") -> str:
        prompt = f"""
You are an expert AI email assistant. Analyze the email below and fulfill these exact tasks:

1. Category: Identify if this is 'Recruiter/Job Offer', 'Friend/Personal', or 'Other/Work'.
2. Summary: Provide a concise 2-sentence summary of the main request or context.
3. Response Option 1 (Positive/Accept): Draft a polite and enthusiastic response accepting or scheduling a follow-up.
4. Response Option 2 (Polite Decline/Reschedule): Draft a professional, polite declination or request to reschedule.

Email Details:
- From: {email_data.get('sender')}
- Subject: {email_data.get('subject')}
- Body:
{email_data.get('body')}
"""

        if provider == "groq":
            key = os.getenv("GROQ_API_KEY")
            if not key:
                raise ValueError("GROQ_API_KEY missing in backend .env configuration.")
            client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return response.choices[0].message.content

        elif provider == "nvidia":
            key = os.getenv("NVIDIA_API_KEY")
            if not key:
                raise ValueError("NVIDIA_API_KEY missing in backend .env configuration.")
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=key)
            response = client.chat.completions.create(
                model="meta/llama-3.1-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return response.choices[0].message.content

        elif provider == "gemini":
            key = os.getenv("GEMINI_API_KEY")
            if not key:
                raise ValueError("GEMINI_API_KEY missing in backend .env configuration.")
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        else:
            raise ValueError(f"Unsupported provider: {provider}")