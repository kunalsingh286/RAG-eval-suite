"""
src/app.py — Streamlit chat UI for the RAG pipeline.

Run from the PROJECT ROOT (the chroma_store/ and data/ paths are relative):

    uv run streamlit run src/app.py
"""

import sys
import time
from pathlib import Path

# streamlit puts src/ on sys.path, not the project root — add the root so that
# `from src.rag_pipeline import ...` resolves the same way it does in the evals.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Sync and sanitize Streamlit Cloud secrets into os.environ
try:
    if hasattr(st, "secrets"):
        for k in ["OPENAI_API_KEY", "LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT", "LANGCHAIN_TRACING_V2", "ALPHA_USERS", "MIXPANEL_PROJECT_TOKEN"]:
            if k in st.secrets:
                os.environ[k] = str(st.secrets[k]).strip().replace("\n", "").replace("\r", "").replace(" ", "").replace('"', '').replace("'", "")
except Exception:
    pass

from src.rag_pipeline import RagPipeline
from src.analytics import track_event

ABSTENTION = "I don't have enough information in the provided data to answer that."

st.set_page_config(page_title="Product Assistant RAG", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    /* Premium Dark Mode Glassmorphism Theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    h1 {
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .stChatMessage:hover {
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
    }
    
    /* Inputs & Buttons */
    .stTextInput input, .stChatInputContainer {
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        background: rgba(0, 0, 0, 0.2) !important;
        color: white !important;
    }
    .stButton button {
        background: linear-gradient(45deg, #38bdf8, #818cf8) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover {
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5) !important;
        transform: scale(1.02) !important;
    }
</style>
""", unsafe_allow_html=True)


# the pipeline loads the vector store + downloads/loads the cross-encoder, so
# build it once per (fetch_k, top_k) combo instead of on every rerun
@st.cache_resource(show_spinner="Loading retriever and reranker…")
def get_pipeline(fetch_k: int, top_k: int) -> RagPipeline:
    return RagPipeline(fetch_k=fetch_k, top_k=top_k)


# --- ALPHA ACCESS CONTROL & COST PROTECTION GUARDRAILS ---
MAX_QUERIES_PER_USER = 15
MAX_QUERY_CHARS = 300

# 15 Alpha testing slots + any custom names from env var ALPHA_USERS
DEFAULT_ALPHA_USERS = {
    "kunal",
    "alpha1", "alpha2", "alpha3", "alpha4", "alpha5",
    "tester1", "tester2", "tester3", "tester4", "tester5",
    "friend1", "friend2", "friend3", "friend4", "friend5",
    "rahul", "sneha", "amit", "priya", "rohit", "ananya", "vikram", "neha", "arjun", "pooja"
}

env_users = Path(".env").exists()
import os
raw_env_users = os.getenv("ALPHA_USERS", "")
if raw_env_users:
    ALLOWED_USERS = {u.strip().lower() for u in raw_env_users.split(",") if u.strip()}
else:
    ALLOWED_USERS = DEFAULT_ALPHA_USERS

# Resolve user from URL query param (?user=name) or session state
url_user = st.query_params.get("user", "")
if isinstance(url_user, list):
    url_user = url_user[0] if url_user else ""
url_user = str(url_user).strip().lower()

if "current_user" not in st.session_state:
    st.session_state.current_user = url_user if url_user in ALLOWED_USERS else ""

if url_user and url_user in ALLOWED_USERS:
    st.session_state.current_user = url_user

current_user = st.session_state.current_user

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- GATEKEEPER: BLOCK UNAUTHORIZED USERS (PREVENTS API DRAIN) ---
if not current_user:
    st.title("🔒 Lenny's Product Assistant — Private Alpha")
    st.markdown("""
    Welcome! This product prototype is currently undergoing a **closed Alpha evaluation** with a cohort of 10–15 testers.
    
    To protect OpenAI API quotas, public unauthenticated queries are disabled.
    """)

    st.info("💡 **If you received an invite link**, make sure you opened it with your custom link (e.g. `?user=yourname`).")

    with st.expander("🔑 Have an invite username? Enter it to unlock access", expanded=True):
        input_user = st.text_input("Invite Username / Name", placeholder="e.g. rahul, sneha, tester1").strip().lower()
        if st.button("Unlock Prototype", type="primary"):
            if input_user in ALLOWED_USERS:
                st.session_state.current_user = input_user
                st.query_params["user"] = input_user
                st.rerun()
            else:
                st.error("Invalid invite username. Please check with the project owner.")

    st.caption("Contact the project administrator for an invite token or access link.")
    st.stop()


# --- AUTHORIZED USER SESSION ---
# Count queries made in this session
user_queries_count = len([m for m in st.session_state.messages if m["role"] == "user"])
queries_remaining = max(0, MAX_QUERIES_PER_USER - user_queries_count)

# Track Session Started once per user session
if "session_started_tracked" not in st.session_state:
    track_event(current_user, "Session Started", {"cohort": "alpha"})
    st.session_state.session_started_tracked = True



with st.sidebar:
    st.subheader(f"👋 Welcome, {current_user.capitalize()}!")
    st.caption("Alpha Testing Cohort")
    
    # Quota Card
    st.markdown(f"**Question Quota:** `{user_queries_count} / {MAX_QUERIES_PER_USER}` used")
    st.progress(user_queries_count / MAX_QUERIES_PER_USER)
    if queries_remaining > 0:
        st.caption(f"⚡ {queries_remaining} question{'s' if queries_remaining != 1 else ''} remaining")
    else:
        st.warning("Quota reached for this session.")

    st.divider()
    st.header("Retrieval settings")
    fetch_k = st.slider(
        "fetch_k — candidates from the vector store",
        min_value=5,
        max_value=30,
        value=10,
        help="How many chunks the bi-encoder over-retrieves before reranking.",
    )
    top_k = st.slider(
        "top_k — chunks kept after reranking",
        min_value=1,
        max_value=10,
        value=5,
        help="How many chunks the cross-encoder keeps and feeds to the generator.",
    )
    if top_k > fetch_k:
        st.warning("top_k is larger than fetch_k — you'll get at most fetch_k chunks.")

    st.divider()
    show_context = st.toggle("Show retrieved context", value=True)
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(
        "Answers are grounded strictly in Lenny's Newsletter archives. If the material "
        "doesn't cover it, the assistant will abstain."
    )


st.title("🚀 Lenny's Product Assistant RAG")
st.caption(f"Alpha Prototype · Session Active for **{current_user.capitalize()}**")


def render_context(context: list[str], latency: float | None = None) -> None:
    """Show the retrieved chunks behind an answer in a collapsed expander."""
    label = f"📚 {len(context)} retrieved chunk{'s' if len(context) != 1 else ''}"
    if latency is not None:
        label += f" · {latency:.1f}s"
    with st.expander(label):
        for i, chunk in enumerate(context, start=1):
            st.markdown(f"**Chunk {i}**")
            st.text(chunk)
            if i != len(context):
                st.divider()


# Replay conversation history
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if show_context and message.get("context"):
                render_context(message["context"], message.get("latency"))
            # In-app thumbs feedback routed to LangSmith
            fb_key = f"fb_{idx}"
            if fb_key not in st.session_state:
                st.session_state[fb_key] = message.get("user_score")
            
            rating = st.feedback("thumbs", key=fb_key)
            if rating is not None and rating != message.get("user_score") and message.get("run_id"):
                message["user_score"] = rating
                score = 1.0 if rating == 1 else 0.0
                try:
                    from langsmith import Client
                    client = Client()
                    client.create_feedback(
                        run_id=message["run_id"],
                        key="user_feedback",
                        score=score,
                        comment="👍 User Thumbs Up" if rating == 1 else "👎 User Thumbs Down",
                    )
                    st.toast("Feedback sent to LangSmith! 🎉")
                except Exception as fb_err:
                    print(f"Error logging user feedback: {fb_err}")
                
                # Product Analytics: Track user feedback in Mixpanel
                track_event(
                    current_user,
                    "Feedback Submitted",
                    {
                        "rating": "thumbs_up" if rating == 1 else "thumbs_down",
                        "score": score,
                        "query_index": idx // 2,
                    }
                )


# Chat Input with budget check and length guardrail
if queries_remaining <= 0:
    if "quota_reached_tracked" not in st.session_state:
        track_event(current_user, "Quota Reached", {"total_queries": MAX_QUERIES_PER_USER})
        st.session_state.quota_reached_tracked = True
    st.info("🎉 **You have reached your 15-question alpha quota!** Thank you so much for testing Lenny's Assistant.")
else:
    placeholder = f"Ask anything about product management ({queries_remaining} questions left, max {MAX_QUERY_CHARS} chars)..."
    query = st.chat_input(placeholder, max_chars=MAX_QUERY_CHARS)

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            try:
                rag = get_pipeline(fetch_k, top_k)
                with st.spinner("Retrieving and generating…"):
                    started = time.perf_counter()
                    # Tag trace with the tester's username in LangSmith
                    result = rag.invoke(
                        query,
                        langsmith_extra={
                            "metadata": {"user": current_user},
                            "tags": [current_user, "alpha-cohort"]
                        }
                    )
                    latency = time.perf_counter() - started
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
                st.session_state.messages.pop()
            else:
                answer, context = result["answer"], result["context"]
                run_id = result.get("run_id")
                st.markdown(answer)
                if answer.strip() == ABSTENTION:
                    st.info("The assistant abstained — this isn't covered in the transcripts.")
                if show_context:
                    render_context(context, latency)

                # Product Analytics: Track query in Mixpanel
                track_event(
                    current_user,
                    "Query Submitted",
                    {
                        "query_number": len(st.session_state.messages) // 2,
                        "char_length": len(query),
                        "latency_seconds": round(latency, 2),
                        "abstained": (answer.strip() == ABSTENTION),
                    }
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "context": context,
                        "latency": latency,
                        "run_id": run_id,
                        "user_score": None,
                    }
                )
                st.rerun()

