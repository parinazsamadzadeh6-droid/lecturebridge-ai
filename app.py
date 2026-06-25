import streamlit as st
import os
import json
import tempfile
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    timeout=60.0
)

LANGUAGES = [
    "Persian (Farsi)",
    "Spanish",
    "French",
    "German",
    "Chinese (Mandarin)",
    "Arabic",
    "Turkish",
    "Portuguese",
    "Italian",
    "Japanese"
]

# ── Backend functions (unchanged) ──────────────────────────────────────────

def parse_json_safely(raw_text):
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return []

def transcribe(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3-turbo"
        )
    return transcription.text

def translate(transcript, language):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[{"role": "user", "content": f"""You are a professional academic translator. Translate the following lecture transcript into formal, proper {language}. Do not mix in English words except for standard technical symbols. Respond with ONLY the translated text.\n\nTranscript:\n{transcript}"""}]
    )
    return response.choices[0].message.content.strip()

def get_glossary(transcript, language):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[{"role": "user", "content": f"""You are an academic glossary builder. Extract key technical terms from this lecture transcript.\n\nFor each term provide:\n- the original English term\n- its {language} translation\n- a short one-sentence definition in {language}\n\nRespond with ONLY valid JSON. No markdown, no code fences, no explanation. Just the raw JSON array:\n[\n  {{\"term\": \"...\", \"translation\": \"...\", \"definition\": \"...\"}}\n]\n\nTranscript:\n{transcript}"""}]
    )
    return parse_json_safely(response.choices[0].message.content.strip())

def get_notes(transcript, language):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[{"role": "user", "content": f"""You are an expert academic note-taker helping an international student study.\n\nGenerate structured study notes in {language} from the following lecture transcript.\n\nStructure:\n# [Title]\n## Key Concepts\n## Formulas and Relationships\n## Important Points\n## Summary\n\nRules:\n- Write in formal {language}\n- Be clear and concise\n- Do not add information not in the transcript\n- Respond with ONLY the notes\n\nTranscript:\n{transcript}"""}]
    )
    return response.choices[0].message.content.strip()

def get_summary(transcript, language):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[{"role": "user", "content": f"""Write a concise summary of the following lecture transcript in {language}.\n\nRules:\n- Keep it proportional to transcript length\n- Cover the most important concept, key formula if any, and why it matters\n- Do not add information not in the transcript\n- Respond with ONLY the summary\n\nTranscript:\n{transcript}"""}]
    )
    return response.choices[0].message.content.strip()

def get_quiz(transcript, language):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.4,
        messages=[{"role": "user", "content": f"""Generate exam questions and answers in {language} based on this lecture transcript.\n\nGenerate exactly 3 questions:\n1. One multiple choice question with 4 options\n2. One short answer question\n3. One essay question\n\nEach with full answers. Base questions ONLY on the transcript content.\nRespond with ONLY the questions and answers.\n\nTranscript:\n{transcript}"""}]
    )
    return response.choices[0].message.content.strip()

# ── UI helpers ──────────────────────────────────────────────────────────────

def rtl(text):
    st.markdown(
        f'<div class="rtl-text">{text}</div>',
        unsafe_allow_html=True
    )

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    /* ── Reset & base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f1a;
        color: #f1f5f9;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 860px;
    }

    /* ── Hero ── */
    .hero {
        position: relative;
        background: linear-gradient(135deg, #0f1e3a 0%, #0b0f1a 60%);
        border: 1px solid #1e2d47;
        border-radius: 20px;
        padding: 3rem 2.5rem 2.5rem;
        margin-bottom: 2rem;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #f59e0b, #10b981, #3b82f6, #f59e0b);
        background-size: 200% 100%;
        animation: shimmer 3s linear infinite;
    }
    @keyframes shimmer {
        0%   { background-position: 0% 0%; }
        100% { background-position: 200% 0%; }
    }
    .hero-eyebrow {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #f59e0b;
        margin-bottom: 0.75rem;
    }
    .hero-title {
        font-family: 'Sora', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        line-height: 1.15;
        color: #f1f5f9;
        margin-bottom: 0.9rem;
    }
    .hero-title span {
        color: #f59e0b;
    }
    .hero-body {
        font-size: 1.05rem;
        color: #94a3b8;
        max-width: 560px;
        line-height: 1.65;
        margin-bottom: 1.8rem;
    }
    .pill-row {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
    }
    .pill {
        background: #141929;
        border: 1px solid #1e2d47;
        border-radius: 100px;
        padding: 0.35rem 0.9rem;
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
    }
    .pill span {
        margin-right: 0.35rem;
    }

    /* ── Upload card ── */
    .upload-card {
        background: #141929;
        border: 1px solid #1e2d47;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .upload-card-label {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.6rem;
    }
    div[data-testid="stFileUploader"] {
        background: #0b0f1a !important;
        border: 2px dashed #1e2d47 !important;
        border-radius: 12px !important;
        transition: border-color 0.2s;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #f59e0b !important;
    }
    div[data-testid="stFileUploader"] label {
        color: #94a3b8 !important;
    }

    /* ── Selectbox ── */
    div[data-baseweb="select"] > div {
        background: #0b0f1a !important;
        border: 1px solid #1e2d47 !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }

    /* ── Process button ── */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0b0f1a !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.85rem 2rem !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        width: 100% !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 20px rgba(245,158,11,0.25) !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(245,158,11,0.4) !important;
    }

    /* ── Download button ── */
    div[data-testid="stDownloadButton"] > button {
        background: transparent !important;
        color: #f59e0b !important;
        border: 1px solid #f59e0b !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background: #f59e0b !important;
        color: #0b0f1a !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #141929 !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid #1e2d47 !important;
        gap: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px !important;
        color: #64748b !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 0.9rem !important;
        transition: all 0.2s !important;
    }
    .stTabs [aria-selected="true"] {
        background: #f59e0b !important;
        color: #0b0f1a !important;
        font-weight: 700 !important;
    }

    /* ── Output card ── */
    .out-card {
        background: #141929;
        border: 1px solid #1e2d47;
        border-radius: 14px;
        padding: 1.6rem;
        margin-bottom: 1rem;
        line-height: 1.75;
        color: #f1f5f9;
    }
    .out-card h1, .out-card h2, .out-card h3 {
        font-family: 'Sora', sans-serif;
        color: #f1f5f9;
    }
    .out-card h2 { color: #f59e0b; border-bottom: 1px solid #1e2d47; padding-bottom: 0.4rem; }

    /* ── RTL text ── */
    .rtl-text {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
        line-height: 1.9;
        font-size: 1rem;
        color: #e2e8f0;
    }

    /* ── Glossary card ── */
    .g-card {
        background: #0b0f1a;
        border: 1px solid #1e2d47;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.7rem;
        border-left: 3px solid #f59e0b;
    }
    .g-en {
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: #f59e0b;
    }
    .g-tr {
        direction: rtl;
        text-align: right;
        font-size: 0.95rem;
        color: #10b981;
        margin-top: 0.3rem;
        font-weight: 500;
    }
    .g-def {
        direction: rtl;
        text-align: right;
        font-size: 0.85rem;
        color: #f1f5f9;
        margin-top: 0.4rem;
        line-height: 1.65;
    }

    /* ── Status / alert ── */
    div[data-testid="stStatusWidget"] {
        background: #141929 !important;
        border: 1px solid #1e2d47 !important;
        border-radius: 12px !important;
    }
    .stAlert {
        border-radius: 10px !important;
        border: 1px solid #1e2d47 !important;
    }

    /* ── Section label ── */
    .section-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.5rem;
    }

    /* ── Divider ── */
    hr {
        border-color: #1e2d47 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ── Page config ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LectureBridge AI",
    page_icon="🎓",
    layout="centered"
)

inject_css()

# ── Hero ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">AI-Powered Study Assistant</div>
    <div class="hero-title">Turn any lecture into<br><span>study materials</span><br>in your language.</div>
    <div class="hero-body">
        Upload a lecture recording. Get a full transcript, translation,
        bilingual glossary, structured notes, summary, and exam questions —
        automatically, in under a minute.
    </div>
    <div class="pill-row">
        <div class="pill"><span>🎤</span>Transcript</div>
        <div class="pill"><span>🌍</span>Translation</div>
        <div class="pill"><span>📚</span>Glossary</div>
        <div class="pill"><span>📝</span>Notes</div>
        <div class="pill"><span>⚡</span>Summary</div>
        <div class="pill"><span>🎯</span>Quiz</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Upload + language ──────────────────────────────────────────────────────

col_a, col_b = st.columns([3, 2], gap="medium")

with col_a:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown('<div class="upload-card-label">📁 Lecture Audio</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="",
        type=["mp3", "mp4", "m4a", "wav", "webm", "mpeg"],
        help="Max 25 MB · MP3, M4A, WAV, MP4, WEBM",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    st.markdown('<div class="upload-card-label">🌍 Output Language</div>', unsafe_allow_html=True)
    target_language = st.selectbox(
        label="",
        options=LANGUAGES,
        index=0,
        label_visibility="collapsed"
    )
    st.markdown("""
        <div style="margin-top:1rem; font-size:0.78rem; color:#64748b; line-height:1.6;">
            Choose the language your study materials will be generated in.
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Process ────────────────────────────────────────────────────────────────

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

if uploaded_file is not None:
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.success(f"✅ **{uploaded_file.name}** · {file_size_mb:.1f} MB")
    with col_info2:
        st.info(f"🌍 Output: **{target_language}**")

    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

    process_button = st.button(
        "🚀  Process Lecture",
        type="primary",
        use_container_width=True
    )

    if process_button:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{uploaded_file.name.split('.')[-1]}"
        ) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            with st.status("⚙️  Processing your lecture…", expanded=True) as status:
                st.write("🎤  Transcribing audio…")
                transcript = transcribe(tmp_path)
                st.write("✅  Transcription complete")

                st.write("🌍  Translating transcript…")
                translation = translate(transcript, target_language)
                st.write("✅  Translation complete")

                st.write("📚  Extracting glossary…")
                glossary = get_glossary(transcript, target_language)
                st.write(f"✅  Glossary complete — {len(glossary)} terms")

                st.write("📝  Generating study notes…")
                notes = get_notes(transcript, target_language)
                st.write("✅  Notes complete")

                st.write("⚡  Generating summary…")
                summary = get_summary(transcript, target_language)
                st.write("✅  Summary complete")

                st.write("🎯  Generating quiz…")
                quiz = get_quiz(transcript, target_language)
                st.write("✅  Quiz complete")

                status.update(
                    label="🎉  Study materials ready — see tabs below",
                    state="complete",
                    expanded=False
                )

            st.divider()

            st.markdown('<div class="section-label">Your study materials</div>', unsafe_allow_html=True)

            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🎤 Transcript",
                "🌍 Translation",
                "📚 Glossary",
                "📝 Notes",
                "⚡ Summary",
                "🎯 Quiz"
            ])

            with tab1:
                st.markdown(f'<div class="out-card">{transcript}</div>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Transcript", transcript, file_name="transcript.txt", mime="text/plain")

            with tab2:
                st.markdown(f'<div class="out-card rtl-text">{translation}</div>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Translation", translation, file_name="translation.txt", mime="text/plain")

            with tab3:
                if glossary:
                    for item in glossary:
                        st.markdown(f"""
                        <div class="g-card">
                            <div class="g-en">{item['term']}</div>
                            <div class="g-tr">{item['translation']}</div>
                            <div class="g-def">{item['definition']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    glossary_text = "\n".join([
                        f"{i['term']} | {i['translation']} | {i['definition']}"
                        for i in glossary
                    ])
                    st.download_button("⬇️ Download Glossary", glossary_text, file_name="glossary.txt", mime="text/plain")
                else:
                    st.warning("No glossary terms were found. Try a longer audio file.")

            with tab4:
                st.markdown(f'<div class="out-card rtl-text">{notes}</div>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Notes", notes, file_name="notes.md", mime="text/markdown")

            with tab5:
                st.markdown(f'<div class="out-card rtl-text">{summary}</div>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Summary", summary, file_name="summary.txt", mime="text/plain")

            with tab6:
                st.markdown(f'<div class="out-card rtl-text">{quiz}</div>', unsafe_allow_html=True)
                st.download_button("⬇️ Download Quiz", quiz, file_name="quiz.md", mime="text/markdown")

        finally:
            os.unlink(tmp_path)

else:
    st.markdown("""
    <div style="
        text-align: center;
        padding: 2.5rem 1rem;
        color: #64748b;
        border: 1px dashed #1e2d47;
        border-radius: 14px;
        margin-top: 0.5rem;
    ">
        <div style="font-size:2.5rem; margin-bottom:0.8rem;">🎙️</div>
        <div style="font-size:1rem; font-weight:600; color:#94a3b8;">
            Upload a lecture to get started
        </div>
        <div style="font-size:0.82rem; margin-top:0.4rem;">
            Supports MP3 · M4A · WAV · MP4 · WEBM &nbsp;·&nbsp; Max 25 MB
        </div>
    </div>
    """, unsafe_allow_html=True)