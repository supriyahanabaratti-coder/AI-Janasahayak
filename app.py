
import io
import hashlib
import streamlit as st
import speech_recognition as sr

from streamlit_mic_recorder import mic_recorder

from backend.pdf_reader import extract_text_from_pdf
from backend.ai_engine import explain_document, ask_question
from backend.translator import (
    get_supported_languages,
    get_speech_code
)
from backend.eligibility import extract_eligibility_information
from database.db import create_database, save_history, get_history


# =====================================================
# PAGE SETTINGS
# =====================================================

st.set_page_config(
    page_title="AI JanSahayak",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_database()


# =====================================================
# SESSION STATE
# =====================================================

DEFAULTS = {
    "menu": "🏠 Home",
    "document_text": "",
    "document_name": "",
    "document_pages": 0,
    "answer": "",
    "question_input": "",
    "last_audio_hash": "",
    "chat_language": "English",
    "chat_messages": [],
    "show_tips": True,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================================
# NAVIGATION CALLBACKS
# =====================================================

def go_to_page(page):
    st.session_state.menu = page


def go_to_document():
    st.session_state.menu = "📄 Document Assistant"


# =====================================================
# STYLE
# =====================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: linear-gradient(
            135deg,
            #f5f7ff 0%,
            #f8fbff 55%,
            #eef6ff 100%
        );
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #102a56 0%,
            #173e72 100%
        );
    }

    [data-testid="stSidebar"] * {
        color: #f5f8ff !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255,255,255,.07);
        border-radius: 10px;
        padding: 8px 10px;
        margin: 3px 0;
    }

    .hero {
        padding: 30px 32px;
        border-radius: 22px;
        background: linear-gradient(120deg, #12366b, #2876bd);
        color: white;
        box-shadow: 0 12px 30px rgba(22,65,120,.16);
        margin-bottom: 18px;
    }

    .hero h1 {
        color: white;
        font-size: 36px;
        margin: 0 0 8px 0;
    }

    .hero p {
        color: #e7f1ff;
        font-size: 16px;
        margin: 0;
    }

    .section-kicker {
        color: #3976b9;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .feature-card {
        background: white;
        border: 1px solid #e5ecf7;
        border-radius: 16px;
        padding: 18px;
        min-height: 145px;
        box-shadow: 0 5px 18px rgba(31,61,104,.05);
    }

    .feature-card h3 {
        color: #18345d;
        margin: 8px 0 6px 0;
        font-size: 18px;
    }

    .feature-card p {
        color: #64748b;
        font-size: 14px;
        margin: 0;
    }

    .status-pill {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 30px;
        background: #e7f7ef;
        color: #16734b;
        font-size: 12px;
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5ecf7;
        padding: 15px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(31,61,104,.04);
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 43px;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #e2eaf5;
        border-radius: 12px;
        background: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🏛️ AI JanSahayak")
st.sidebar.caption("Government Information Assistant")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📄 Document Assistant",
        "💬 Ask AI",
        "📚 History",
        "ℹ️ About"
    ],
    key="menu"
)

st.sidebar.divider()
st.sidebar.markdown("### 🌐 Supported Languages")

for language_name in get_supported_languages():
    st.sidebar.write("🌐 " + language_name)

st.sidebar.divider()
st.sidebar.caption(
    "Making government information accessible to everyone."
)


# =====================================================
# HOME PAGE
# =====================================================

if menu == "🏠 Home":

    st.markdown(
        """
        <div class="hero">
            <div class="section-kicker" style="color:#b9d9ff">
                CIVIC INFORMATION • MADE SIMPLE
            </div>

            
        </div>
        """,
        unsafe_allow_html=True
    )

    active_doc = bool(
        st.session_state.document_text.strip()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Document status",
        "Ready" if active_doc else "Not uploaded"
    )

    col2.metric(
        "Languages",
        len(get_supported_languages())
    )

    col3.metric(
        "Saved conversations",
        len(get_history())
    )

    st.markdown("### What would you like to do today?")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            """
            <div class="feature-card">
                <div style="font-size:28px">📄</div>
                <h3>Understand a PDF</h3>
                <p>
                    Upload a government document and get
                    a clear, structured explanation.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Open Document Assistant →",
            key="home_doc",
            use_container_width=True,
            on_click=go_to_page,
            args=("📄 Document Assistant",)
        )

    with c2:

        st.markdown(
            """
            <div class="feature-card">
                <div style="font-size:28px">💬</div>
                <h3>Ask your questions</h3>
                <p>
                    Ask AI about the document using text
                    or your voice.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Ask AI →",
            key="home_chat",
            use_container_width=True,
            on_click=go_to_page,
            args=("💬 Ask AI",)
        )

    with c3:

        st.markdown(
            """
            <div class="feature-card">
                <div style="font-size:28px">📚</div>
                <h3>Continue where you left</h3>
                <p>
                    Revisit previous explanations and
                    answers anytime.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "View History →",
            key="home_history",
            use_container_width=True,
            on_click=go_to_page,
            args=("📚 History",)
        )

    st.markdown("### A simple 3-step process")

    step1, step2, step3 = st.columns(3)

    step1.info(
        "**01 · Upload**\n\n"
        "Choose a government PDF from your device."
    )

    step2.info(
        "**02 · Understand**\n\n"
        "Get key points, eligibility and required documents."
    )

    step3.info(
        "**03 · Ask**\n\n"
        "Ask follow-up questions in any of our 13 supported languages."
    )

    st.caption(
        "Your answers are based on the text extracted from "
        "the PDF you upload. Always verify important decisions "
        "with the official department."
    )


# =====================================================
# DOCUMENT ASSISTANT
# =====================================================

elif menu == "📄 Document Assistant":

    st.title("📄 Document Assistant")

    st.caption(
        "Upload once. Understand the important details in a few steps."
    )

    language = st.selectbox(
        "Choose your explanation language",
        get_supported_languages(),
        key="document_language"
    )

    uploaded_file = st.file_uploader(
        "📤 Upload Government PDF",
        type=["pdf"],
        help="Select a PDF document from your computer."
    )

    if uploaded_file is None:

        st.info("📤 Please upload a government PDF to get started.")

    else:

        current_file_hash = hashlib.sha256(
            uploaded_file.getvalue()
        ).hexdigest()

        if st.session_state.get("document_hash") != current_file_hash:

            try:

                with st.spinner("Reading your PDF document..."):

                    pages = extract_text_from_pdf(uploaded_file)

                    full_text = "\n\n".join(
                        f"Page {page['page']}\n{page['text']}"
                        for page in pages
                    )

                st.session_state.document_text = full_text
                st.session_state.document_name = uploaded_file.name
                st.session_state.document_pages = len(pages)
                st.session_state.document_hash = current_file_hash
                st.session_state.answer = ""
                st.session_state.question_input = ""
                st.session_state.last_audio_hash = ""

            except Exception as error:

                st.error(f"PDF Error: {error}")
                st.stop()

        if not st.session_state.document_text.strip():

            st.warning(
                "No readable text was found. This may be a scanned PDF "
                "that requires OCR."
            )

        else:

            st.success(
                f"✅ Uploaded: {st.session_state.document_name}"
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Extracted Characters",
                len(st.session_state.document_text)
            )

            col2.metric(
                "PDF Pages",
                st.session_state.document_pages
            )

            preview_tab, details_tab = st.tabs(
                ["👀 Document preview", "📋 Extracted details"]
            )

            with preview_tab:

                st.text_area(
                    "Extracted text (preview)",
                    st.session_state.document_text[:5000],
                    height=220,
                    disabled=True
                )

            with details_tab:

                st.write(
                    "**File name:**",
                    st.session_state.document_name
                )

                st.write(
                    "**Pages processed:**",
                    st.session_state.document_pages
                )

                st.write(
                    "**Text extracted:**",
                    f"{len(st.session_state.document_text):,} characters"
                )

            st.divider()

            if st.button(
                "🤖 Generate AI Explanation",
                use_container_width=True
            ):

                with st.spinner(
                    "AI JanSahayak is analyzing your document..."
                ):

                    try:

                        answer = explain_document(
                            st.session_state.document_text[:12000],
                            language
                        )

                        st.session_state.answer = answer

                        save_history(
                            "Explain: " + st.session_state.document_name,
                            answer,
                            language
                        )

                        st.success("Document analysis completed!")

                    except Exception as error:

                        st.error(f"AI Error: {error}")

            if st.session_state.answer:

                st.divider()

                st.subheader("🤖 Document Explanation")

                st.markdown(st.session_state.answer)

                st.download_button(
                label="📥 Download Explanation",
                data=answer,
                file_name="scheme_explanation.txt",
                mime="text/plain"
)
            st.divider()

            st.subheader("📋 Eligibility Information")

            eligibility = extract_eligibility_information(
                st.session_state.document_text
            )

            if eligibility:

                for item in eligibility:
                    st.write("•", item)

            else:

                st.info(
                    "No clear eligibility information was found "
                    "in this document."
                )


# =====================================================
# ASK AI PAGE
# =====================================================

elif menu == "💬 Ask AI":

    st.title("💬 Ask AI JanSahayak")

    st.caption(
        "Ask questions about your uploaded government document."
    )

    language_options = get_supported_languages()

    current_language = st.session_state.chat_language

    if current_language not in language_options:
        current_language = language_options[0]

    language = st.selectbox(
        "Select answer language",
        language_options,
        index=language_options.index(current_language),
        key="chat_language"
    )

    if not st.session_state.document_text.strip():

        st.warning(
            "Please upload a government PDF in Document Assistant first."
        )

        st.button(
            "📄 Go to Document Assistant",
            on_click=go_to_document,
            use_container_width=True
        )

    else:

        st.success(
            f"📄 Active document: {st.session_state.document_name}"
        )

        reset_col, spacer_col = st.columns([1, 3])

        with reset_col:

            if st.button(
                "🧹 Clear this chat",
                use_container_width=True
            ):

                st.session_state.chat_messages = []
                st.session_state.question_input = ""
                st.rerun()

        st.divider()

        st.subheader("🎤 Ask Using Your Voice")

        st.caption(
            "Click Start Recording, speak your question, "
            "then click Stop Recording."
        )

        language_code = get_speech_code(language)

        audio = mic_recorder(
            start_prompt="🎤 Start Recording",
            stop_prompt="⏹️ Stop Recording",
            key="voice_recorder",
            format="wav"
        )

        if audio and audio.get("bytes"):

            audio_hash = hashlib.sha256(
                audio["bytes"]
            ).hexdigest()

            if st.session_state.last_audio_hash != audio_hash:

                st.session_state.last_audio_hash = audio_hash

                try:

                    recognizer = sr.Recognizer()

                    audio_buffer = io.BytesIO(audio["bytes"])

                    with sr.AudioFile(audio_buffer) as source:
                        recorded_audio = recognizer.record(source)

                    voice_text = recognizer.recognize_google(
                        recorded_audio,
                        language=language_code
                    )

                    st.session_state.question_input = voice_text

                    st.success("✅ Voice converted into text!")

                    st.write(
                        "Recognized question:",
                        voice_text
                    )

                except sr.UnknownValueError:

                    st.warning(
                        "Voice was not clear. Please try again."
                    )

                except sr.RequestError as error:

                    st.error(
                        f"Speech recognition service error: {error}"
                    )

                except Exception as error:

                    st.error(
                        f"Audio error: {error}. Check microphone "
                        "permission and WAV audio."
                    )

        st.markdown("### 💡 Try asking")

        suggestions = [
            "Who is eligible for this scheme?",
            "What documents are required?",
            "How can I apply?",
            "What benefits are mentioned?"
        ]

        suggestion_cols = st.columns(2)

        for index, suggestion in enumerate(suggestions):

            with suggestion_cols[index % 2]:

                st.button(
                    suggestion,
                    key=f"suggestion_{index}",
                    use_container_width=True,
                    on_click=lambda value=suggestion: (
                        st.session_state.update(
                            {"question_input": value}
                        )
                    )
                )

        if st.session_state.chat_messages:

            st.markdown("### 💬 This conversation")

            for message in st.session_state.chat_messages:

                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        st.divider()

        st.subheader("⌨️ Type Your Question")

        question = st.text_input(
            "Your question",
            key="question_input",
            placeholder="Example: What documents are required?"
        )

        if st.button("🤖 Ask AI", use_container_width=True):

            if not question.strip():

                st.warning(
                    "Please enter or record a question first."
                )

            else:

                with st.spinner(
                    "Finding the answer in your document..."
                ):

                    try:

                        answer = ask_question(
                            st.session_state.document_text,
                            question.strip(),
                            language
                        )

                        st.session_state.chat_messages.append(
                            {
                                "role": "user",
                                "content": question.strip()
                            }
                        )

                        st.session_state.chat_messages.append(
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        )

                        save_history(
                            question.strip(),
                            answer,
                            language
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(f"AI Error: {error}")


# =====================================================
# HISTORY PAGE
# =====================================================

elif menu == "📚 History":

    st.title("📚 Conversation History")

    st.caption(
        "Your saved explanations and question-answer sessions."
    )

    records = get_history()

    st.metric(
        "Total saved conversations",
        len(records)
    )

    search_text = st.text_input(
        "🔍 Search History",
        placeholder="Search by question or answer..."
    )

    if records:

        filtered_records = [
            record for record in records
            if search_text.lower() in str(record[1]).lower()
            or search_text.lower() in str(record[2]).lower()
        ]

        if filtered_records:

            for record in filtered_records:

                with st.expander(f"📄 {record[1]}"):

                    st.write(
                        "**Language:**",
                        record[3]
                    )

                    st.markdown(record[2])

                    st.download_button(
                        "⬇️ Download Answer",
                        data=record[2],
                        file_name=f"JanSahayak_History_{record[0]}.txt",
                        mime="text/plain",
                        key=f"history_download_{record[0]}"
                    )

        else:

            st.info("No matching history found.")

    else:

        st.info(
            "No previous history available yet. Generate an explanation "
            "or ask a question to save a record."
        )


# =====================================================
# ABOUT PAGE
# =====================================================

elif menu == "ℹ️ About":

    st.title("ℹ️ About AI JanSahayak")

    st.markdown(
        '<span class="status-pill">A student-built civic-tech project</span>',
        unsafe_allow_html=True
    )

    st.write(
        "AI JanSahayak is an AI-powered multilingual government "
        "information assistant. Its purpose is to make government "
        "information easier to understand and accessible to everyone."
    )

    st.divider()

    st.subheader("✨ Our Features")

    st.markdown(
        "- 📄 Government PDF analysis\n"
        "- 🤖 Simple AI explanations\n"
        "- 🌐 13 Indian languages support\n"
        "- 💬 Document-based AI question answering\n"
        "- 🎤 Voice-based question input\n"
        "- 📋 Eligibility information extraction\n"
        "- ⬇️ Downloadable explanations\n"
        "- 📚 Saved conversation history"
    )

    st.divider()

    st.subheader("🛠️ Technology Used")

    st.markdown(
        "- Python and Streamlit\n"
        "- Google Gemini AI\n"
        "- PyMuPDF\n"
        "- SQLite\n"
        "- SpeechRecognition"
    )

    st.divider()

    st.subheader("🎯 Our Mission")

    st.write(
        "To make government schemes, policies and public information "
        "easier to understand through AI and multilingual technology."
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "© AI JanSahayak | Making Government Information Accessible to Everyone"
)
