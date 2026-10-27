#!/usr/bin/env python3
"""Render the withholding project README as a printable PDF."""

from pathlib import Path

import markdown
from weasyprint import HTML

BASE = Path("/home/rimas/liquidador-retenciones")
md = (BASE / "README.md").read_text(encoding="utf-8")
body = markdown.markdown(md, extensions=["tables", "sane_lists", "fenced_code"], output_format="html5")

css = r"""
@page {
  size: A4;
  margin: 18mm 16mm 18mm 16mm;
  @top-left { content: "Liquidador de retenciones Colombia 2026"; font-family: "DejaVu Sans", sans-serif; font-size: 7.5pt; color: #5f6f7f; }
  @top-right { content: "Diseño y 16 casos de control"; font-family: "DejaVu Sans", sans-serif; font-size: 7.5pt; color: #5f6f7f; }
  @bottom-right { content: counter(page) " / " counter(pages); font-family: "DejaVu Sans", sans-serif; font-size: 7.5pt; color: #5f6f7f; }
}
* { box-sizing: border-box; }
body { font-family: "DejaVu Sans", "Lato", Arial, sans-serif; font-size: 9.2pt; line-height: 1.45; color: #1f2933; }
h1 { font-size: 22pt; line-height: 1.1; color: #ffffff; background: #16324f; padding: 6mm 4mm; margin: 0 0 5mm; border-bottom: 3mm solid #c9a227; }
h2 { font-size: 13pt; color: #16324f; border-bottom: 1.2pt solid #d9e2ea; padding-bottom: 1.5mm; margin: 7mm 0 3mm; page-break-after: avoid; }
h3 { font-size: 10.5pt; color: #1f4e79; margin: 5mm 0 2mm; page-break-after: avoid; }
p { margin: 0 0 2.5mm; }
blockquote { margin: 3mm 0; padding: 2.5mm 3mm; background: #fff8e6; border-left: 1.2mm solid #c9a227; color: #5f4b00; font-size: 8.8pt; }
table { width: 100%; border-collapse: collapse; margin: 2.5mm 0 4mm; font-size: 8pt; }
th { background: #16324f; color: #ffffff; font-weight: bold; text-align: left; padding: 1.5mm 1.2mm; border: 0.3pt solid #16324f; }
td { padding: 1.3mm 1.2mm; border: 0.3pt solid #d9e2ea; vertical-align: top; }
tr:nth-child(even) td { background: #f3f6f9; }
ul, ol { margin: 0 0 3mm 4.5mm; padding: 0; }
li { margin-bottom: 1mm; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; background: #eef5fb; padding: 0.2mm 1mm; border-radius: 1mm; }
hr { border: 0; border-top: 0.4pt solid #d9e2ea; margin: 5mm 0; }
strong { color: #16324f; }
a { color: #1f4e79; text-decoration: none; }
tr { page-break-inside: avoid; }
"""

html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Liquidador de retenciones Colombia 2026</title><style>{css}</style></head>
<body>{body}</body></html>"""

out = BASE / "Guia_Retenciones_16_Casos.pdf"
HTML(string=html, base_url=str(BASE)).write_pdf(str(out))
print(f"OK: {out}")
