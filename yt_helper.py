# ─────────────────────────────────────────────
#  YouTube Helper — Transcript & Summarization
# ─────────────────────────────────────────────

import re
from youtube_transcript_api import YouTubeTranscriptApi
from ai_helper import call_groq


def extract_video_id(url):
    """Extract YouTube video ID from any YouTube URL format."""
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(video_id):
    """Fetch the transcript/captions of a YouTube video."""
    try:
        # New API style (v0.7+)
        ytt = YouTubeTranscriptApi()
        transcript_list = ytt.fetch(video_id)
        full_text = " ".join([entry.text for entry in transcript_list])
        return full_text
    except Exception:
        # Old API style fallback (v0.6)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry["text"] for entry in transcript_list])
        return full_text


def summarize_transcript(transcript):
    """Summarize a YouTube video transcript using Groq."""
    trimmed = transcript[:8000]
    prompt = f"""You are a helpful assistant. Please provide a clear, well-structured summary of the following video transcript.
Include:
- Main topic
- Key points
- Important takeaways

Transcript:
{trimmed}

Summary:"""
    result = call_groq(prompt, max_tokens=600)
    if result:
        return result
    return "📝 **Transcript excerpt:**\n\n" + transcript[:1000] + "..."
