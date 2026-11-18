# Meeting Notes Studio

**One HTML file that turns a meeting transcript or rough notes into presentable minutes, an Excel tracker or an email, without installing anything and without any data leaving the computer.**

Most companies allow meeting transcripts but don't allow installing tools or pasting meeting content into public AI. This works within those rules: you open the file in the browser that is already on every work laptop, and it runs offline.

## How to use it

1. Download **[Meeting Notes Studio.html](Meeting%20Notes%20Studio.html)** and double-click it. It opens in Chrome or Edge (Firefox and Safari also work).
2. **Transcript:** paste what was discussed, even rough notes, or drop a file: Teams or Zoom `.vtt`, Teams "Download as Word" `.docx`, `.txt` or `.md`. Three samples are built in.
3. **Check points:** the tool drafts actions (with owner, due date and priority), decisions, open questions, risks and discussion notes. You edit, delete or add points and tick each one once it is right.
   - **Amber notes** show what to look at: no owner, no deadline, an unclear "it", a condition ("depends on…"), a task mentioned twice.
   - **Pink chips** are grammar and spelling fixes. Click one to apply it.
   - **Use original words** puts back exactly what was said.
4. **Design and export:** pick one of 12 designs, see your points in it, then export.

## 12 designs

| Documents | Trackers | Visual boards | One-pagers |
|---|---|---|---|
| Formal minutes | Action tracker | Workshop wall (sticky notes) | Executive one-pager |
| Steering committee (with RAG status) | Owner matrix (who does what) | Kanban board | Email summary |
| Client recap | Stand-up cards (one per person) | Deadline timeline, Retro board | |

## Exports

| Export | What you get |
|---|---|
| **PDF** | The chosen design, through the browser's print window ("Save as PDF") |
| **Excel tracker** | Overview with KPI tiles and actions per owner, an Action tracker with a Status dropdown (Open, In progress, Done), Decisions, and Questions and risks. The Overview uses formulas, so it updates as actions are marked Done. |
| **Word** | Editable minutes that open in Word |
| **Copy for email** | Formatted text to paste into Outlook or Gmail, with a suggested subject line |

## Privacy

- **No server, no upload.** Everything runs inside the page.
- **Network blocked by design.** The file contains a security rule (Content Security Policy) that stops the page from connecting to anything on the internet, so meeting text can't be sent anywhere even by mistake.
- **Drafts stay in this browser.** Your current draft is kept in the browser's local storage so a refresh doesn't lose it. **Start over** clears it.
- **Optional AI step.** If your company has an approved AI assistant (for example Microsoft 365 Copilot), you can copy a ready-made prompt with your transcript into it and paste its answer back. You still check every point.

## How it works

- **Extraction uses plain rules, not AI:** patterns like "I'll…", "Tom, can you… by Wednesday?", "let's agree…", "someone should…", "that's a risk". It also handles a few harder cases: tasks handed from one person to another, "actually no" corrections, someone volunteering, and working out what "it" refers to. The draft is good but not perfect, which is why the review step exists.
- **Rewording** turns speech into short task lines ("I'll send it tomorrow morning" becomes "Send the email", due "Tomorrow morning") and removes filler words.
- **Grammar check** uses [Harper](https://writewithharper.com), an open-source grammar checker that runs inside the page (British or American English).

## Files

| Path | What it is |
|---|---|
| `Meeting Notes Studio.html` | The finished app: one file, about 12 MB (mostly the grammar checker) |
| `src/engine.js` | Rules that find actions, decisions, questions, risks and notes |
| `src/templates.js` | The 12 designs |
| `src/exporters.js` | PDF, Excel, Word and email export, and the `.docx` reader |
| `src/app.js`, `src/app.css`, `src/index.html` | The interface |
| `samples/` | Invented example meetings (no real data) |
| `build.py` | Combines everything into the single HTML file |

## Rebuild after changing the source

Needs Node.js and Python:

```
npm install --prefix build-deps harper.js@3.2.0 exceljs@4.4.0 esbuild
python build.py
```

## Open-source parts

- [ExcelJS](https://github.com/exceljs/exceljs) (MIT licence) for the Excel export
- [Harper](https://github.com/Automattic/harper) (Apache 2.0 licence) for the grammar check
