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

# ---------- Sidebar: which local engine and model ----------
with st.sidebar:
    st.header("Settings")
    engine_label = st.radio("AI engine (both run on this computer)",
                            ["Built-in (no extra install)", "Ollama app"])
    engine = "ollama" if engine_label.startswith("Ollama") else "built-in"
    host = ex.DEFAULT_HOST
    if engine == "built-in":
        model = st.selectbox("Model", list(ex.BUILTIN_MODELS))
        st.success("Local: the transcript stays on this computer.")
        st.caption("The first run downloads the model once (1 to 5 GB). After that it works offline.")
    else:
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
st.write("Paste a transcript or rough notes. A local AI model turns them into an Excel action tracker "
         "you can email: action items, decisions and open questions, with every item checked against the transcript.")

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

c1, c2, c3 = st.columns([3, 1.2, 1])
with c1:
    title = st.text_input("Meeting name", "Weekly project sync")
with c2:
    meeting_date = st.date_input("Meeting date", format="DD.MM.YYYY")
with c3:
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
    with st.spinner("Reading the meeting on your computer… (the first built-in run also downloads the model)"):
        try:
            st.session_state.result = ex.check(ex.extract(transcript, engine, model, host), transcript)
        except ImportError:
            st.error("The built-in engine is not installed. Run:  pip install -r requirements.txt")
        except requests.RequestException as e:
            st.error(f"Could not reach Ollama: {e}")
        except ValueError as e:
            st.error(f"The model's answer could not be read: {e}")
        except Exception as e:  # e.g. the model download is blocked on a company network
            st.error(f"The built-in model could not start: {e}. If the download is blocked, "
                     "ask IT to allow huggingface.co, or use the Ollama engine.")

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
    when = meeting_date.strftime("%d %b %Y") if meeting_date else ""
    d1, d2 = st.columns(2)
    d1.download_button("⬇ Download Excel action tracker", ex.to_excel(result, title, when),
                       f"{safe} - action tracker.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
    d2.download_button("Download Markdown (paste into an email or Teams)", ex.to_markdown(result, title),
                       f"{safe} - minutes.md", "text/markdown")
    st.caption("The Excel has an Overview sheet with charts, and a Status column (Open, In progress, Done) "
               "that updates the Overview as people tick things off.")
