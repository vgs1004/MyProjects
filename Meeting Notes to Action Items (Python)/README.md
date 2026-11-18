# Meeting Notes to Action Items (local AI)

Turn any meeting transcript into a **presentable Excel action tracker** you can email: action items with owners and deadlines, decisions, open questions, and an overview sheet with charts.

**Why not just use the built-in meeting minutes?** Teams and similar tools only write minutes for meetings they record, and many companies don't allow cloud AI on internal meetings. This works with *any* transcript or rough notes, including meetings you couldn't record, and it runs **entirely on your own computer**. No meeting text goes to a cloud service. Everything is free: no API key, no subscription.

## What you get

**An Excel workbook with four sheets:**

| Sheet | What's on it |
|---|---|
| Overview | KPI tiles (action items, still open, high priority open, need a check), the summary, actions per owner and by priority, two charts |
| Action tracker | One row per action: task, owner, due, priority, **Status dropdown** (Open, In progress, Done), checks, and the quote from the transcript as evidence |
| Decisions | What the group agreed |
| Open questions | What was raised but not answered |

The Overview uses formulas, so when someone sets an action to **Done**, the tiles and charts update by themselves, and finished rows are struck through. You can send the file after the meeting and reuse it at the next one.

There's also a Markdown version for pasting into an email or Teams.

## How it works

1. **You paste the transcript** (or upload a `.txt`, `.vtt` Teams/Zoom transcript, or `.md` file).
2. **A local AI model reads it** and answers in a fixed structure. Each item must include a short quote from the transcript as evidence.
3. **The app checks the model's work** and marks rows that need a human look:
   - **quote not found in transcript**: the model may have made the item up
   - **no owner**: nobody actually took the task
   - **owner not mentioned in meeting**: a name that was never said
   - **no deadline**: nothing was agreed on timing
4. **You review the marked rows** and download the Excel tracker.

AI does the reading. You make the final call.

## Two engines, both local

| Engine | What you install | Good for |
|---|---|---|
| **Built-in** (default) | Nothing extra: it comes with `pip install` | Simplest setup. The model runs inside Python. |
| **Ollama** | The free [Ollama](https://ollama.com/download) app | If you already use Ollama or want to try many models |

With the built-in engine, the first run downloads a free model from Hugging Face once:

| Model | Download | Notes |
|---|---|---|
| Qwen 2.5 3B (recommended) | about 2 GB | Good balance on a normal laptop (8 GB RAM) |
| Qwen 2.5 1.5B | about 1 GB | Faster, less accurate |
| Qwen 2.5 7B | about 4.7 GB | Most accurate, needs about 16 GB RAM |

After the download it works offline. On a company network that blocks Hugging Face, download the model at home once, or use Ollama.

## Install (one time)

```
pip install -r requirements.txt
```

**On Windows**, if that fails while building `llama-cpp-python`, install the ready-made version first, then run the line above again:

```
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

## Run

```
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`. Click **Load sample meeting** to try it with the invented example in [sample_meeting.txt](sample_meeting.txt), then **Extract action items** and **Download Excel action tracker**.

## Files

| File | What it does |
|---|---|
| `app.py` | The Streamlit page: engine choice, input, results, downloads |
| `extractor.py` | The prompt, the call to the local model (built-in or Ollama), and the checks |
| `excel_report.py` | Builds the formatted Excel tracker with charts and the Status dropdown |
| `sample_meeting.txt` | An invented project meeting with some tricky parts: a task handed from one person to another, a vague "someone should", and an unanswered question |
| `requirements.txt` | Python packages |

## Privacy notes

- Both engines run on your computer. The sidebar shows a green **Local** badge. If you point the Ollama engine at another machine, it turns red.
- The only internet use is the one-time model download. The transcript is never sent anywhere.
- Before using it with real company meetings, check your company's policy on transcripts and AI tools, even local ones.
- The sample meeting is invented. No real meeting data is in this repository.
