# Method 2: Python notebook

Claude writes the content as Markdown. This notebook turns that Markdown into a hand-drawn notebook PDF: spiral binding, wobbly ink boxes, highlighter, sticky notes, takeaway clouds and flow diagrams. Styling costs zero AI tokens, and every set of notes looks the same.

New here? Start with the [installation guide](INSTALL.md).

## Files

| File | What it is |
|---|---|
| `handwritten_notes_maker.ipynb` | The notebook: setup, settings, fonts, doodle icons, style, Markdown parser and PDF builder |
| `notes_format_guide.md` | Two-page guide to every marker the notebook understands. It is also a sample input |
| `content_prompt.txt` | The prompt I give Claude to write the notes content (replace `<TOPIC NAME HERE>`) |
| `n8n Notes (Method 2).pdf` | Example output: 42 pages on n8n automation |

## How it works

1. Paste `content_prompt.txt` (with your topic) and `notes_format_guide.md` into Claude.
2. Save Claude's answer as a `.md` file next to the notebook.
3. Run the notebook. It converts the Markdown to HTML, then prints the HTML to PDF with Playwright, all on your computer.

## Markers at a glance

| Write | Get |
|---|---|
| `# Title` | new page with a boxed title |
| `## Heading` | section heading, inks rotate |
| `==text==` · `[[Ctrl]]` · `{r:text}` · `:bulb:` | highlighter · key cap · coloured ink · doodle icon |
| `> tip:` `> warning:` `> example:` | callout box |
| `> takeaway:` · `> sticky:` | cloud · sticky note |
| `::: cols` · `::: box` · `::: steps` · `::: flow` | columns · box · step cards · flow diagram |
