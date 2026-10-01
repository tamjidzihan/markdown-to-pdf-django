from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .markdown_engine import render_markdown

MAX_BYTES = 1024 * 1024  # 1 MB

TYPEFACES = [
    {"name": "Roboto", "hint": "Familiar README look", "category": "sans",
     "family": "'Roboto', sans-serif", "gf": "Roboto:ital,wght@0,400;0,500;0,700;1,400"},
    {"name": "Montserrat", "hint": "Sans-serif for business docs", "category": "sans",
     "family": "'Montserrat', sans-serif", "gf": "Montserrat:ital,wght@0,400;0,500;0,700;1,400"},
    {"name": "Lato", "hint": "Friendly neutral sans", "category": "sans",
     "family": "'Lato', sans-serif", "gf": "Lato:ital,wght@0,400;0,700;1,400"},
    {"name": "Libre Baskerville", "hint": "Serif for papers & notes", "category": "serif",
     "family": "'Libre Baskerville', serif", "gf": "Libre+Baskerville:ital,wght@0,400;0,700;1,400"},
    {"name": "IBM Plex Sans", "hint": "High-contrast modern look", "category": "sans",
     "family": "'IBM Plex Sans', sans-serif", "gf": "IBM+Plex+Sans:ital,wght@0,400;0,500;0,700;1,400"},
    {"name": "Playfair Display", "hint": "Magazine-style serif headings", "category": "serif",
     "family": "'Playfair Display', serif", "gf": "Playfair+Display:ital,wght@0,400;0,500;0,700;1,400"},
    {"name": "JetBrains Mono", "hint": "Monospaced, developer notes", "category": "mono",
     "family": "'JetBrains Mono', monospace", "gf": "JetBrains+Mono:wght@400;700"},
]

# UI font (Inter) is loaded alongside the document typefaces.
FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&"
    + "&".join("family=" + t["gf"] for t in TYPEFACES)
    + "&display=swap"
)

COLOURS = [
    {"name": "Teal", "accent": "#0d9488"},
    {"name": "Blue", "accent": "#1d6fdc"},
    {"name": "Indigo", "accent": "#4263eb"},
    {"name": "Amber", "accent": "#b45309"},
    {"name": "Green", "accent": "#15803d"},
    {"name": "Navy", "accent": "#1e40af"},
    {"name": "Red", "accent": "#dc2626"},
    {"name": "Sky", "accent": "#0284c7"},
    {"name": "Rust", "accent": "#c2410c"},
    {"name": "Rose", "accent": "#e11d48"},
]

SAMPLE_MARKDOWN = """# Markdown to PDF
### Paste AI output, notes, or a README — download a polished PDF.

Beautiful Markdown PDFs in one click — **no CSS**, no DIY styling. Use *emphasis*, ~~strikethrough~~, `inline code`, and [links](https://www.djangoproject.com/).

![Markdown to PDF](/static/converter/logo.svg)

## Get started

1. Type or paste Markdown here
2. Pick a typeface — preview updates live
3. Click **Download PDF**

## Why people use it

- Export **ChatGPT / Claude / Gemini** answers to PDF
- Turn **Cursor** notes and specs into shareable docs
- Build a **Markdown resume** or status report
- Keep diagrams, math, and code looking clean in print

### Checklist

- [x] Headings, lists, and tables
- [x] Syntax-highlighted code
- [x] Mermaid diagrams
- [x] LaTeX / KaTeX math
- [ ] Your document next

## Code

```js
function hello(name) {
  return `Hello, ${name}!`;
}
```
"""


def index(request):
    return render(request, "converter/index.html", {
        "typefaces": TYPEFACES,
        "colours": COLOURS,
        "fonts_url": FONTS_URL,
        "sample": SAMPLE_MARKDOWN,
        "preview_html": render_markdown(SAMPLE_MARKDOWN),
    })


@require_POST
def preview(request):
    text = request.POST.get("markdown", "")
    if len(text.encode("utf-8")) > MAX_BYTES:
        return JsonResponse({"error": "Document is larger than 1 MB."}, status=413)
    return JsonResponse({"html": render_markdown(text)})


@require_POST
def upload(request):
    f = request.FILES.get("file")
    if not f:
        return JsonResponse({"error": "No file received."}, status=400)
    if not f.name.lower().endswith((".md", ".markdown", ".mdown", ".txt")):
        return JsonResponse({"error": "Please upload a .md, .markdown or .txt file."}, status=400)
    if f.size > MAX_BYTES:
        return JsonResponse({"error": "File is larger than 1 MB."}, status=413)
    try:
        text = f.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return JsonResponse({"error": "File must be UTF-8 text."}, status=400)
    return JsonResponse({"name": f.name, "text": text})
