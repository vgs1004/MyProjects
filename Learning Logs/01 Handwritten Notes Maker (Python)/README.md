# Handwritten Notes Maker: two ways to make AI study notes

![Before and now: two ways to make AI study notes](images/before-and-now.png)

Everyone shares those beautiful handwritten study notes. This folder holds the two ways I made mine for interview prep, and why I switched.

Full write-up: [Learning Log #1 on my website](https://vgs1004.github.io/blog/2026/11/learning-log-01-handwritten-notes/)

## What's in this folder

| Folder | What it is |
|---|---|
| [Method 1 (One Long Prompt)](Method%201%20%28One%20Long%20Prompt%29/) | The single prompt I used for every topic, and the SQL notes it produced |
| [Method 2 (Python Notebook)](Method%202%20%28Python%20Notebook%29/) | The notebook, its format guide, the content prompt, an installation guide, and the n8n notes it produced |

## Method 1: one long prompt, Claude makes the whole PDF

I gave Claude the same long prompt for every topic ([prompt.txt](Method%201%20%28One%20Long%20Prompt%29/prompt.txt)). It asks Claude to check official documentation, teach the topic from zero, and make a PDF that looks like handwritten notes in a spiral notebook, using as many pages as needed.

Claude researches, writes, designs and builds the PDF, all in one go ([SQL notes, 25 pages](Method%201%20%28One%20Long%20Prompt%29/SQL%20Notes%20%28Method%201%29.pdf)). It works well for a single guide, but Claude builds the layout each time, and any layout fix means another round in Claude.

<img src="images/method1-sample-page.jpg" alt="A page from the Method 1 SQL notes" width="420">

## Method 2: the design is fixed, Claude writes only the content

1. **The design is fixed once** in a Python notebook: fonts, colours, layout.
2. **Claude writes only the content**, in plain Markdown, using official docs as sources. This is the only step that uses tokens.
3. **The notebook builds the PDF on my laptop:** Markdown to HTML (HTML lines the text up properly), then HTML to PDF. Free, and the same look every time.

Result: [n8n notes, 42 pages](Method%202%20%28Python%20Notebook%29/n8n%20Notes%20%28Method%202%29.pdf).

**Why I prefer it:** alignment is handled for me, layout edits are free (change a setting and re-run), every guide looks the same, and Claude's effort goes into the content.

## Average tokens per guide (estimate)

For a 20-page guide with the same research and roughly the same amount of text. Planning averages, not measured usage.

| Work Claude does | Method 1 | Method 2 |
|---|---:|---:|
| Instructions (prompt, plus format guide in Method 2) | ~300 | ~2,200 |
| Research and source reading | ~15,000 | ~15,000 |
| Writing the guide | ~7,000 | ~8,000 |
| Building the PDF, checking pages, fixing layout | ~10,000 | 0 (local Python) |
| **Total** | **~32,000** | **~25,000** |

About 20 to 30% fewer tokens per guide, and Claude writes about half as much.

<img src="images/method2-sample-page-v2.jpg" alt="A page from the Method 2 n8n notes" width="420">

## What I learned

- **Separate content from design**, like a template in Word or a theme in Power BI.
- **Use the AI only where it adds value.** Writing the content needs Claude. Building the PDF doesn't.
- **You don't need to be a developer.** I built the notebook by describing what I wanted to Claude and checking each page.
