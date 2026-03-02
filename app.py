import streamlit as st

# Import helpers
from pdf_helper import extract_text_from_pdf, build_vector_store, answer_question
from yt_helper import extract_video_id, get_transcript, summarize_transcript
from feedback_helper import save_feedback, show_feedback_stats

# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind",
    page_icon="🧠",
    layout="wide",
)

# ─────────────────────────────────────────────
#  Load CSS
# ─────────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Session state init
# ─────────────────────────────────────────────
for key, default in {
    "chat_history": [],
    "vector_store": None,
    "feedback_data": [],
    "pdf_name": None,
    "yt_summary": None,
    "yt_transcript": None,
    "yt_video_id": None,
    "yt_feedback_data": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown('<p class="main-title">🧠 DocuMind</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">RAG-powered PDF Q&A & YouTube Summarizer · Built with LangChain, Groq & Streamlit</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📄 PDF Question Answering", "▶️ YouTube Summarizer"])


# ══════════════════════════════════════════════
#  TAB 1 — PDF Q&A
# ══════════════════════════════════════════════
with tab1:
    left_col, right_col = st.columns([1, 2], gap="large")

    with left_col:
        st.markdown("### Upload PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], label_visibility="collapsed")

        if uploaded_file:
            if st.session_state.pdf_name != uploaded_file.name:
                with st.spinner("🔍 Reading and indexing your PDF…"):
                    raw_text = extract_text_from_pdf(uploaded_file)
                    st.session_state.vector_store = build_vector_store(raw_text)
                    st.session_state.pdf_name = uploaded_file.name
                    st.session_state.chat_history = []
                st.success(f"✅ '{uploaded_file.name}' indexed!")
            st.markdown(f'<div class="status-ready">📗 Active: {st.session_state.pdf_name}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
- *"What is the main topic?"*
- *"Summarize this document"*
- *"List the key points"*
- *"What does chapter 2 say?"*
""")
        show_feedback_stats(st.session_state.feedback_data, "Responses")

    with right_col:
        st.markdown("### Chat with your PDF")

        for i, msg in enumerate(st.session_state.chat_history):
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)
                with st.expander("💬 Rate this answer", expanded=False):
                    rating = st.slider("Rating", 1, 5, 3, key=f"pdf_rating_{i}")
                    comment = st.text_input("Comment (optional)", key=f"pdf_comment_{i}", placeholder="What was good or bad?")
                    if st.button("Submit Feedback", key=f"pdf_submit_{i}"):
                        q = st.session_state.chat_history[i - 1]["content"] if i > 0 else ""
                        save_feedback(st.session_state.pdf_name, q, msg["content"], rating, comment, "feedback_data")
                        st.success("✅ Feedback saved!")

        st.markdown("---")

        if st.session_state.vector_store is None:
            st.info("⬅️ Upload a PDF first to start asking questions.")
        else:
            question = st.text_input(
                "Ask a question",
                placeholder="e.g. What is the main topic of this document?",
                key="pdf_question_input",
            )
            if st.button("Ask ➜", key="pdf_ask"):
                if question.strip():
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    with st.spinner("Thinking…"):
                        answer = answer_question(st.session_state.vector_store, question)
                    st.session_state.chat_history.append({"role": "bot", "content": answer})
                    st.rerun()


# ══════════════════════════════════════════════
#  TAB 2 — YouTube Summarizer
# ══════════════════════════════════════════════
with tab2:
    left_col2, right_col2 = st.columns([1, 2], gap="large")

    with left_col2:
        st.markdown("### Paste YouTube URL")
        yt_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="yt_url_input"
        )

        if st.button("Summarize ▶️", key="yt_summarize"):
            if yt_url.strip():
                video_id = extract_video_id(yt_url)
                if not video_id:
                    st.error("❌ Invalid YouTube URL. Please check and try again.")
                else:
                    with st.spinner("📥 Fetching transcript…"):
                        try:
                            transcript = get_transcript(video_id)
                            st.session_state.yt_transcript = transcript
                            st.session_state.yt_video_id = video_id
                        except Exception as e:
                            st.error(f"❌ Could not fetch transcript.\n\nError: {str(e)}")
                            transcript = None

                    if transcript:
                        with st.spinner("🧠 Summarizing…"):
                            summary = summarize_transcript(transcript)
                            st.session_state.yt_summary = summary
                        st.success("✅ Summary ready!")

        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
- Works on videos with **captions/subtitles**
- Auto-generated captions work too
- Best for lectures, tutorials, talks
- Try TED Talks or educational videos
""")
        show_feedback_stats(st.session_state.yt_feedback_data, "Summaries")

    with right_col2:
        st.markdown("### Video Summary")

        if st.session_state.yt_video_id:
            st.markdown(f"""
            <div class="yt-info-box">
                <iframe width="100%" height="250"
                src="https://www.youtube.com/embed/{st.session_state.yt_video_id}"
                frameborder="0" allowfullscreen></iframe>
            </div>
            """, unsafe_allow_html=True)

        if st.session_state.yt_summary:
            st.markdown(f'<div class="summary-box">{st.session_state.yt_summary}</div>', unsafe_allow_html=True)

            with st.expander("📜 View full transcript"):
                st.text_area("Transcript", st.session_state.yt_transcript, height=300, label_visibility="collapsed")

            st.markdown("---")
            st.markdown("#### 💬 Rate this summary")
            yt_rating = st.slider("Rating (1 = poor, 5 = excellent)", 1, 5, 3, key="yt_rating")
            yt_comment = st.text_input("Comment (optional)", key="yt_comment", placeholder="Was the summary accurate?")
            if st.button("Submit Feedback", key="yt_feedback_submit"):
                save_feedback(
                    f"youtube:{st.session_state.yt_video_id}",
                    "summarize video",
                    st.session_state.yt_summary,
                    yt_rating, yt_comment,
                    "yt_feedback_data"
                )
                st.success("✅ Feedback saved – thank you!")
        else:
            st.info("⬅️ Paste a YouTube URL and click Summarize to get started.")
