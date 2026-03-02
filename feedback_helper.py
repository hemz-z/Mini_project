# ─────────────────────────────────────────────
#  Feedback Helper — Save and Load Feedback
# ─────────────────────────────────────────────

import json
import streamlit as st
from datetime import datetime


def save_feedback(source, question, answer, rating, comment, feedback_list_key):
    """Save feedback to session state and to a local JSON file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "question": question,
        "answer": answer,
        "rating": rating,
        "comment": comment,
    }
    st.session_state[feedback_list_key].append(entry)
    with open("feedback_log.json", "a") as f:
        f.write(json.dumps(entry) + "\n")


def show_feedback_stats(feedback_list, label="Responses"):
    """Display feedback stats in the sidebar."""
    if feedback_list:
        st.markdown("---")
        st.markdown("### 📊 Feedback Stats")
        total = len(feedback_list)
        avg = sum(f["rating"] for f in feedback_list) / total
        st.metric(f"{label} rated", total)
        st.metric("Avg. rating", f"{avg:.1f} / 5")
