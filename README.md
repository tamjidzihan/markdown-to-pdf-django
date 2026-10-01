# markdowntopdf

An elegant, minimal, and privacy-first web utility to convert Markdown into publication-ready PDFs in real time.

Draft or paste Markdown, preview live side-by-side with curated typography and color schemes, and export crisp, calibrated A4 PDFs directly through the browser's print engine.

![markdowntopdf](converter/static/converter/logo.svg)

---

## ✨ Features

- **Instant Dual-Pane Live Preview:** Real-time synchronized rendering with line-numbered editor and drag-and-drop file upload.
- **Curated Typography System:** One-click typeface switching (Roboto, Montserrat, Lato, Libre Baskerville, IBM Plex Sans, Playfair Display, JetBrains Mono).
- **Designer Color Accents:** Curated accent palettes (Teal, Blue, Indigo, Amber, Green, Navy, Red, Sky, Rust, Rose).
- **Fine-Tune Controls:** Live body font-size and line-height sliders.
- **Document Presets / Templates:** Quick-start templates for General Guides, Resumes / CVs, Meeting Notes, and Technical Specs.
- **Live Document Metrics:** Real-time word count, character count, and estimated reading time.
- **Interactive Formatting Toolbar & Cheatsheet:** One-click shortcuts for bold, italics, tables, task lists, code blocks, quote blocks, and link insertion.
- **100% Stateless & Private:** In-memory execution without any database or telemetry. Your documents are never persisted to disk or cloud databases.
- **Calibrated Print Engine:** `@media print` styles calibrated for standard A4 pages with clean page breaks and watermark controls.

---

## 🚀 Quick Start with Docker

Deploy `markdowntopdf` anywhere in seconds with Docker:

### Using Docker Compose (Recommended)

```bash
docker compose up -d --build
```

Access the application at [http://localhost:8000](http://localhost:8000).

### Using Standalone Docker

```bash
# Build the Docker image
docker build -t markdowntopdf .

# Run the container
docker run -d -p 8000:8000 --name markdowntopdf markdowntopdf
```

---

## 💻 Local Development

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)

### 2. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Development Server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| <kbd>Ctrl</kbd> + <kbd>B</kbd> / <kbd>Cmd</kbd> + <kbd>B</kbd> | Bold selection |
| <kbd>Ctrl</kbd> + <kbd>I</kbd> / <kbd>Cmd</kbd> + <kbd>I</kbd> | Italic selection |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> / <kbd>Cmd</kbd> + <kbd>K</kbd> | Insert link |
| <kbd>Ctrl</kbd> + <kbd>P</kbd> / <kbd>Cmd</kbd> + <kbd>P</kbd> | Export PDF (Browser Print) |
| <kbd>Esc</kbd> | Close Cheatsheet or Dropdown menus |

---

## 🛠️ Architecture

- `converter/markdown_engine.py`: Dependency-free Markdown → HTML parser escaping unsafe input.
- `converter/views.py`: In-memory Django views (`index`, `preview`, `upload`).
- `converter/static/converter/`: Minimalist CSS design system and reactive JavaScript client.
- `Dockerfile`: Multi-stage Python 3.12-slim production container with Gunicorn and WhiteNoise static asset compression.

---

## 📄 License

Open-source and free for personal and commercial use.
