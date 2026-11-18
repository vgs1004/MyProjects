"""Build the single-file app: Meeting Notes Studio.html

Combines src/ (interface, rules, templates, exports) with two open-source
libraries so the result is ONE file that works offline:
  - ExcelJS (MIT) for the Excel export
  - Harper (Apache-2.0) for the grammar check, as compressed WebAssembly

One-time setup (needs Node.js):
    npm install --prefix build-deps harper.js@3.2.0 exceljs@4.4.0 esbuild
Then:
    python build.py
"""

import base64
import gzip
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "src"
DEPS = HERE / "build-deps" / "node_modules"
OUT = HERE / "Meeting Notes Studio.html"


def js_safe(code: str) -> str:
    """Stop inlined code from closing the <script> tag early."""
    return code.replace("</script", "<\\/script").replace("<!--", "<\\!--")


def harper_bundle() -> str:
    entry = HERE / "build-deps" / "harper-entry.js"
    entry.write_text(
        "import { LocalLinter, createBinaryModuleFromUrl, Dialect } from 'harper.js';\n"
        "window.HarperLib = { LocalLinter, createBinaryModuleFromUrl, Dialect };\n"
    )
    out = HERE / "build-deps" / "harper.bundle.js"
    externals = ["fs", "node:fs", "fs/promises", "path", "url", "module", "worker_threads"]
    subprocess.run(
        [str(DEPS / ".bin" / "esbuild"), str(entry), "--bundle", "--format=iife", "--minify", f"--outfile={out}"]
        + [f"--external:{e}" for e in externals],
        check=True,
    )
    return out.read_text()


def main() -> None:
    html = (SRC / "index.html").read_text()
    wasm = (DEPS / "harper.js" / "dist" / "harper_wasm_slim_bg.wasm").read_bytes()
    samples = {}
    for label, name in [("Project sync (transcript)", "sample_meeting.txt"),
                        ("Marketing notes (rough)", "rough_notes.txt"),
                        ("Teams file (.vtt)", "teams_transcript.vtt")]:
        samples[label] = (HERE / "samples" / name).read_text()
    parts = {
        "/*APP_CSS*/": (SRC / "app.css").read_text(),
        "/*HARPER_WASM_B64*/": base64.b64encode(gzip.compress(wasm, 9)).decode(),
        "/*EXCELJS*/": js_safe((DEPS / "exceljs" / "dist" / "exceljs.min.js").read_text()),
        "/*HARPER_BUNDLE*/": js_safe(harper_bundle()),
        "/*ENGINE*/": js_safe((SRC / "engine.js").read_text()),
        "/*TEMPLATES*/": js_safe((SRC / "templates.js").read_text()),
        "/*EXPORTERS*/": js_safe((SRC / "exporters.js").read_text()),
        "/*SAMPLES*/": "window.SAMPLES = " + js_safe(json.dumps(samples, ensure_ascii=False)) + ";",
        "/*APP*/": js_safe((SRC / "app.js").read_text()),
    }
    for marker, content in parts.items():
        assert marker in html, marker
        html = html.replace(marker, content, 1)
    OUT.write_text(html)
    print(f"Built {OUT.name}: {OUT.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
