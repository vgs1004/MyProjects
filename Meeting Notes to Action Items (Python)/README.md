# Meeting Notes to Action Items (local AI)

Paste a meeting transcript or rough notes and get **action items, decisions and open questions** as a table, with Excel and Markdown downloads.

It runs **entirely on your own computer**. The AI model runs locally in [Ollama](https://ollama.com), so no meeting text goes to a cloud service. That makes it safe for internal company meetings. Everything is free: no API key, no subscription.

## How it works

1. **You paste the transcript** (or upload a `.txt`, `.vtt` Teams/Zoom transcript, or `.md` file).
2. **A local model reads it** and answers in a fixed structure: summary, decisions, action items (task, owner, due, priority) and open questions. Each item must include a short quote from the transcript as evidence.
3. **The app checks the model's work** and flags rows that need a human look:
   - **quote not found in transcript**: the model may have made the item up
   - **no owner**: nobody actually took the task
   - **owner not mentioned in meeting**: a name that was never said
   - **no deadline**: nothing was agreed on timing
4. **You review the flagged rows**, then download the minutes as Excel or Markdown (ready to paste into an email or Teams).

AI does the reading. You make the final call.

## Install (one time, about 15 minutes)

1. **Ollama:** download and install it from [ollama.com/download](https://ollama.com/download) (Windows, Mac or Linux), then open the Ollama app.
2. **A model:** open a terminal (Command Prompt on Windows) and run:
   ```
   ollama pull llama3.1:8b
   ```
   This downloads about 5 GB once. On a laptop with less than 16 GB of RAM, a smaller model such as `llama3.2:3b` runs faster but is less accurate. Any model from the Ollama library will work, and the app lists the ones you have.
3. **Python packages:** in this folder, run:
   ```
   pip install -r requirements.txt
   ```

## Run

```
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`. Click **Load sample meeting** to try it with the invented example in [sample_meeting.txt](sample_meeting.txt).

## Files

| File | What it does |
|---|---|
| `app.py` | The Streamlit page: input, results table, downloads |
| `extractor.py` | The prompt, the call to Ollama, the checks, and the Excel and Markdown export |
| `sample_meeting.txt` | An invented project meeting with some tricky parts: a task handed from one person to another, a vague "someone should", and an unanswered question |
| `requirements.txt` | Python packages |

## Privacy notes

- The sidebar shows a green **Local** badge when Ollama is on your computer. If you change the address to another machine, it turns red.
- Before using it with real company meetings, check your company's policy on transcripts and AI tools, even local ones.
- The sample meeting is invented. No real meeting data is in this repository.
