"""Turn a meeting transcript into decisions, action items and open questions.

Everything runs on this computer: the transcript goes to Ollama on localhost,
never to a cloud service.
"""

import difflib
import io
import json
import re
from urllib.parse import urlparse

import pandas as pd
import requests

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1:8b"
NOT_STATED = "Not stated"

# The model must answer in exactly this shape (Ollama "structured outputs").
SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "decision": {"type": "string"},
                    "decided_by": {"type": "string"},
                    "source_quote": {"type": "string"},
                },
                "required": ["decision", "decided_by", "source_quote"],
            },
        },
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "owner": {"type": "string"},
                    "due": {"type": "string"},
                    "priority": {"type": "string", "enum": ["High", "Medium", "Low"]},
                    "source_quote": {"type": "string"},
                },
                "required": ["task", "owner", "due", "priority", "source_quote"],
            },
        },
        "open_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "raised_by": {"type": "string"},
                },
                "required": ["question", "raised_by"],
            },
        },
    },
    "required": ["summary", "decisions", "action_items", "open_questions"],
}

SYSTEM_PROMPT = f"""You are a careful business analyst taking minutes.
Read the meeting transcript and extract:
- summary: 2 to 3 sentences on what the meeting was about and where it ended.
- decisions: things the group agreed. Only real agreements, not suggestions.
- action_items: concrete tasks someone will do after the meeting.
- open_questions: questions that were raised but not answered.

Rules:
- Use only what is in the transcript. Never invent names, dates or tasks.
- owner: the person who agreed to do the task. If nobody clearly took it, write "{NOT_STATED}".
- If a task was handed from one person to another, the owner is the final person.
- due: copy the deadline as it was said (for example "Friday" or "end of sprint"). If none, write "{NOT_STATED}".
- priority: High if it blocks a release or a client, Low if it is nice to have, otherwise Medium.
- source_quote: copy a short phrase (5 to 15 words) word for word from the transcript that supports the item.
- Write tasks as short instructions starting with a verb, for example "Send the test plan to QA".
"""


def is_local(host: str) -> bool:
    """True when the Ollama address points at this computer."""
    name = urlparse(host).hostname or ""
    return name in {"localhost", "127.0.0.1", "::1"}


def list_models(host: str = DEFAULT_HOST) -> list[str]:
    """Models already downloaded in Ollama, for example ['llama3.1:8b']."""
    r = requests.get(f"{host}/api/tags", timeout=5)
    r.raise_for_status()
    return sorted(m["name"] for m in r.json().get("models", []))


def extract(transcript: str, model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST) -> dict:
    """Ask the local model for the minutes and return them as a dict."""
    if not transcript.strip():
        raise ValueError("The transcript is empty.")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n\n{transcript}"},
        ],
        "format": SCHEMA,
        "stream": False,
        # temperature 0: the same transcript gives (almost) the same answer each time.
        # num_ctx: room for about an hour of meeting text.
        "options": {"temperature": 0, "num_ctx": 16384},
    }
    r = requests.post(f"{host}/api/chat", json=payload, timeout=600)
    r.raise_for_status()
    content = r.json()["message"]["content"]
    result = json.loads(content)
    for key in ("decisions", "action_items", "open_questions"):
        result.setdefault(key, [])
    result.setdefault("summary", "")
    return result


# ---------- Checks: catch the model's mistakes before you trust the table ----------

def _norm(text: str) -> str:
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def quote_found(quote: str, transcript: str, threshold: float = 0.8) -> bool:
    """Is the quote (nearly) word for word in the transcript?"""
    q, t = _norm(quote), _norm(transcript)
    if not q:
        return False
    if q in t:
        return True
    match = difflib.SequenceMatcher(None, t, q, autojunk=False).find_longest_match(0, len(t), 0, len(q))
    return match.size / len(q) >= threshold


def check(result: dict, transcript: str) -> dict:
    """Add a 'check' note to each action item and decision. Empty note means it looks fine."""
    t_norm = _norm(transcript)
    for item in result["action_items"]:
        notes = []
        if not quote_found(item.get("source_quote", ""), transcript):
            notes.append("quote not found in transcript")
        owner = item.get("owner", "").strip()
        if not owner or owner.lower() == NOT_STATED.lower():
            notes.append("no owner")
        elif not any(_norm(part) in t_norm for part in owner.split()):
            notes.append("owner not mentioned in meeting")
        if not item.get("due") or item["due"].strip().lower() == NOT_STATED.lower():
            notes.append("no deadline")
        item["check"] = "; ".join(notes)
    for d in result["decisions"]:
        d["check"] = "" if quote_found(d.get("source_quote", ""), transcript) else "quote not found in transcript"
    return result


# ---------- Export ----------

def tables(result: dict) -> dict[str, pd.DataFrame]:
    cols = {
        "Action items": ["task", "owner", "due", "priority", "check", "source_quote"],
        "Decisions": ["decision", "decided_by", "check", "source_quote"],
        "Open questions": ["question", "raised_by"],
    }
    keys = {"Action items": "action_items", "Decisions": "decisions", "Open questions": "open_questions"}
    out = {}
    for name, c in cols.items():
        df = pd.DataFrame(result[keys[name]])
        df = df.reindex(columns=c).fillna("")
        df.columns = [x.replace("_", " ").capitalize() for x in c]
        out[name] = df
    return out


def to_excel(result: dict, title: str = "Meeting") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        pd.DataFrame({"Meeting": [title], "Summary": [result["summary"]]}).to_excel(xl, sheet_name="Summary", index=False)
        for name, df in tables(result).items():
            df.to_excel(xl, sheet_name=name, index=False)
        for ws in xl.book.worksheets:
            for col in ws.columns:
                width = max(len(str(c.value or "")) for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(12, width + 2), 60)
    return buf.getvalue()


def to_markdown(result: dict, title: str = "Meeting") -> str:
    lines = [f"# {title}: minutes", "", result["summary"], "", "## Action items", ""]
    lines += ["| Task | Owner | Due | Priority |", "|---|---|---|---|"]
    lines += [f"| {a['task']} | {a['owner']} | {a['due']} | {a['priority']} |" for a in result["action_items"]]
    lines += ["", "## Decisions", ""] + [f"- {d['decision']} ({d['decided_by']})" for d in result["decisions"]]
    lines += ["", "## Open questions", ""] + [f"- {q['question']} ({q['raised_by']})" for q in result["open_questions"]]
    return "\n".join(lines) + "\n"
