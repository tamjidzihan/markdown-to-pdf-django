# Markdown to PDF (Django only)

Paste or upload Markdown, see a live side-by-side preview, pick a typeface and
colour, and download a polished PDF.  The only dependency is Django.

## Run

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Open http://127.0.0.1:8000/

## How it works

* `converter/markdown_engine.py` – dependency-free Markdown → HTML renderer (HTML in the source is escaped).
* `converter/views.py` – `index`, `preview` (live HTML), `upload` (reads a .md file).
* Download PDF uses the browser's print engine with a print stylesheet, so the PDF is
  exactly what you see in the preview. Choose **Save as PDF** as the destination.
* Fonts load from Google Fonts (internet needed for the typefaces).
