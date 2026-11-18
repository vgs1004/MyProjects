"""Meeting Notes to Action Items: a local Streamlit app.

Run:  streamlit run app.py
Needs Ollama running on this computer (see README).
"""

from pathlib import Path

import requests
import streamlit as st

import extractor as ex

HERE = Path(__file__).parent
SAMPLE = HERE / "sample_meeting.txt"

st.set_page_config(page_title="Meeting Notes to Action Items", page_icon="📝", layout="wide")

# ---------- Sidebar: which local model ----------
with st.sidebar:
    st.header("Settings")
    host = st.text_input("Ollama address", ex.DEFAULT_HOST)
    if ex.is_local(host):
        st.success("Local: the transcript stays on this computer.")
    else:
        st.error("This address is not on this computer. The transcript would leave your machine.")
    try:
        models = ex.list_models(host)
    except requests.RequestException:
        models = []
        st.warning("Ollama is not running. Start the Ollama app, then refresh this page.")
    if models:
        default = models.index(ex.DEFAULT_MODEL) if ex.DEFAULT_MODEL in models else 0
        model = st.selectbox("Model", models, index=default)
    else:
        model = st.text_input("Model", ex.DEFAULT_MODEL)
    st.caption("Download a model once with:  ollama pull llama3.1:8b")

# ---------- Input ----------
st.title("📝 Meeting Notes to Action Items")
st.write("Paste a transcript or rough notes. A local AI model turns them into action items, "
         "decisions and open questions, then checks its own work against the transcript.")

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

c1, c2 = st.columns([3, 1])
with c1:
    title = st.text_input("Meeting name", "Weekly project sync")
with c2:
    st.write("")
    st.write("")
    if st.button("Load sample meeting"):
        st.session_state.transcript = SAMPLE.read_text(encoding="utf-8")

uploaded = st.file_uploader("…or upload a transcript (.txt, .vtt, .md)", type=["txt", "vtt", "md"])
if uploaded is not None:
    st.session_state.transcript = uploaded.read().decode("utf-8", errors="replace")

transcript = st.text_area("Transcript", key="transcript", height=280)

# ---------- Run ----------
if st.button("Extract action items", type="primary", disabled=not transcript.strip()):
    with st.spinner(f"{model} is reading the meeting on your computer…"):
        try:
            st.session_state.result = ex.check(ex.extract(transcript, model, host), transcript)
        except requests.RequestException as e:
            st.error(f"Could not reach Ollama: {e}")
        except ValueError as e:
            st.error(f"The model's answer could not be read: {e}")

# ---------- Output ----------
result = st.session_state.get("result")
if result:
    st.subheader("Summary")
    st.write(result["summary"])

    t = ex.tables(result)
    flagged = sum(1 for a in result["action_items"] if a.get("check"))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Action items", len(result["action_items"]))
    m2.metric("Need a look", flagged)
    m3.metric("Decisions", len(result["decisions"]))
    m4.metric("Open questions", len(result["open_questions"]))

    st.subheader("Action items")
    if flagged:
        st.info("Rows with a note under **Check** need a human look: missing owner or deadline, "
                "or a quote the model may have made up.")
    st.dataframe(t["Action items"], use_container_width=True, hide_index=True)

    a, b = st.columns(2)
    with a:
        st.subheader("Decisions")
        st.dataframe(t["Decisions"], use_container_width=True, hide_index=True)
    with b:
        st.subheader("Open questions")
        st.dataframe(t["Open questions"], use_container_width=True, hide_index=True)

    safe = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in title).strip() or "meeting"
    d1, d2 = st.columns(2)
    d1.download_button("Download Excel", ex.to_excel(result, title), f"{safe} - minutes.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    d2.download_button("Download Markdown (for email or Teams)", ex.to_markdown(result, title),
                       f"{safe} - minutes.md", "text/markdown")
