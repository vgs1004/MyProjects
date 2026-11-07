# Handwritten Notes Maker (Python)

Turns a plain Markdown file into a hand-drawn notebook PDF: spiral binding, wobbly ink boxes, highlighter, sticky notes, takeaway clouds and flow diagrams.

I built it by describing the design to Claude and testing it page by page. The idea is to **separate content from design**. Claude writes only the content, in Markdown. This notebook draws the notebook look locally, so styling costs zero AI tokens and every set of notes looks the same.

Write-up: [Learning Log #1 on my website](https://vgs1004.github.io/blog/2026/11/learning-log-01-handwritten-notes/)

## Files

| File | What it is |
|---|---|
| `handwritten_notes_maker.ipynb` | The notebook: setup, settings, fonts, doodle icons, style, Markdown parser and PDF builder |
| `notes_format_guide.md` | Two-page guide to every marker the notebook understands. It is also a sample input |
| `content_prompt.txt` | The prompt I give Claude to write the notes content (replace `<TOPIC NAME HERE>`) |

## How to use

1. Put the notebook and your `.md` file in one folder.
2. In cell 2 (Settings), set `INPUT_MD` and `OUTPUT_PDF`.
3. Run all cells. The first run installs `markdown-it-py`, `mdit-py-plugins`, `beautifulsoup4`, `pyyaml` and `playwright` (with Chromium), and downloads the Kalam and Delius fonts. Later runs take seconds.

To make new notes: paste `content_prompt.txt` (with your topic) and `notes_format_guide.md` into Claude, save its answer as a `.md` file, and run the notebook.

## Markers at a glance

| Write | Get |
|---|---|
| `# Title` | new page with a boxed title |
| `## Heading` | section heading, inks rotate |
| `==text==` · `[[Ctrl]]` · `{r:text}` · `:bulb:` | highlighter · key cap · coloured ink · doodle icon |
| `> tip:` `> warning:` `> example:` | callout box |
| `> takeaway:` · `> sticky:` | cloud · sticky note |
| `::: cols` · `::: box` · `::: steps` · `::: flow` | columns · box · step cards · flow diagram |
