# Installation guide

You need about 10 minutes the first time. After that, making a new PDF takes seconds.

## 1. Install Python

- **Windows:** download Python 3.11 or newer from [python.org](https://www.python.org/downloads/). In the installer, tick **"Add python.exe to PATH"**.
- **Mac:** download it from python.org, or run `brew install python` if you use Homebrew.

Check it worked by opening a terminal (Windows: PowerShell) and typing:

```
python --version
```

## 2. Install Jupyter (to open the notebook)

Choose one:

- **VS Code** (recommended): install [VS Code](https://code.visualstudio.com/), then the **Python** and **Jupyter** extensions.
- **Jupyter in the browser:** run `pip install notebook`, then `jupyter notebook` in the folder.

## 3. Put the files in one folder

Copy these into a new folder, for example `Documents\Notes Maker`:

- `handwritten_notes_maker.ipynb`
- your content file, for example `sql_notes.md`

## 4. Point the notebook at your file

Open the notebook and find **cell 2 (Settings)**. Change these two lines:

```python
INPUT_MD   = BASE / "sql_notes.md"
OUTPUT_PDF = BASE / "sql_notes.pdf"
```

## 5. Run all cells

Click **Run All**. The first run installs everything it needs, which takes a few minutes:

- Python packages: `markdown-it-py`, `mdit-py-plugins`, `beautifulsoup4`, `pyyaml`, `playwright`
- Chromium for Playwright (about 150 MB, used to print the PDF)
- The Kalam and Delius handwriting fonts (saved in a `fonts` folder)

When it finishes, your PDF is in the same folder. Later runs reuse everything and take seconds.

## Troubleshooting

| Problem | Fix |
|---|---|
| `pip` or `python` not found | Reinstall Python with "Add python.exe to PATH" ticked, then restart the terminal |
| Font download failed | Check your internet connection and run the fonts cell again |
| A page looks small | That page was scaled to fit. Split it with a new `# Title` in the Markdown |
| Chromium install blocked at work | Set `CHROMIUM_PATH` in cell 2 to an installed Chrome or Edge |
