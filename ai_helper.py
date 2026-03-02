# ─────────────────────────────────────────────
#  AI Helper — Groq API calls
# ─────────────────────────────────────────────

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def call_groq(prompt, max_tokens=500):
    """Send a prompt to Groq and return the AI response."""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Groq error:", e)
        return None
