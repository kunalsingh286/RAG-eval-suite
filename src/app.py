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

import streamlit as st

from src.rag_pipeline import RagPipeline

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


with st.sidebar:
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
        "Answers are grounded only in the provided Lenny's Newsletter archives. If the material "
        "doesn't cover it, the assistant abstains."
    )


st.title("🚀 Lenny's Product Assistant RAG")
st.caption("Ask anything about product management, growth loops, and finding PMF based on Lenny's Newsletter.")

if "messages" not in st.session_state:
    st.session_state.messages = []


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


# replay the conversation so far
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and show_context and message.get("context"):
            render_context(message["context"], message.get("latency"))


query = st.chat_input("e.g. What is the difference between online and offline eval?")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        try:
            rag = get_pipeline(fetch_k, top_k)
            with st.spinner("Retrieving and generating…"):
                started = time.perf_counter()
                result = rag.invoke(query)
                latency = time.perf_counter() - started
        except Exception as exc:  # bad API key, missing store, model download, …
            st.error(f"Something went wrong: {exc}")
            st.session_state.messages.pop()  # drop the unanswered turn
        else:
            answer, context = result["answer"], result["context"]
            st.markdown(answer)
            if answer.strip() == ABSTENTION:
                st.info("The assistant abstained — this isn't covered in the transcripts.")
            if show_context:
                render_context(context, latency)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "context": context,
                    "latency": latency,
                }
            )
