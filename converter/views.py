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

import json

SAMPLE_MARKDOWN = """# markdowntopdf
### Paste AI output, notes, or READMEs — download a polished PDF in seconds.

Beautiful Markdown PDFs in one click — **no CSS**, no DIY styling. Use *emphasis*, ~~strikethrough~~, `inline code`, and [links](https://github.com).

![markdowntopdf logo](/static/converter/logo.svg)

## Get started

1. Type or paste your Markdown in the left editor
2. Pick a typeface and color accent — preview updates instantly
3. Click **Download PDF** to export via your browser's print engine

## Why use markdowntopdf?

- **100% In-Memory & Private:** No documents are saved to any database or stored on disk.
- **Publication-Ready Typography:** Curated typefaces with balanced hierarchy and spacing.
- **Fast Live Preview:** Real-time dual-pane rendering with line-numbered editor.
- **Zero Config:** Runs out of the box with zero external runtime dependencies.

### Document Checklist

- [x] Crisp headings and typographic scale
- [x] Multi-level lists and task checkboxes
- [x] Responsive data tables with alternating rows
- [x] Syntax-friendly code blocks and inline badges
- [ ] Your document ready to export

## Sample Code Block

```javascript
function convertDocument(markdown) {
  const options = { format: 'A4', orientation: 'portrait' };
  console.log('Rendering publication-ready PDF...');
  return print(markdown, options);
}
```

> **Pro Tip:** Use the shortcut `Ctrl+P` (or `Cmd+P`) at any time to open your browser's print dialog and select **Save as PDF** as destination.
"""

RESUME_MARKDOWN = """# Alex Morgan
**Senior Software Engineer & Distributed Systems Architect**  
San Francisco, CA • alex.morgan@example.com • [linkedin.com/in/alexmorgan](https://linkedin.com) • [github.com/alexmorgan](https://github.com)

---

## Executive Summary
Results-driven software architect with 8+ years of experience leading engineering teams, designing resilient cloud services, and delivering high-impact web platforms. Passionate about developer tooling, API design, and performance optimization.

## Technical Skills
- **Languages:** Python, TypeScript, Go, SQL, Rust
- **Frameworks & Libraries:** Django, FastAPI, React, Next.js, Node.js
- **Cloud & DevOps:** Docker, Kubernetes, AWS, PostgreSQL, Redis, CI/CD Pipelines
- **Architecture:** Distributed Systems, Microservices, Event-Driven Architecture, High Availability

## Professional Experience

### Lead Platform Architect — CloudScale Technologies
*2022 – Present | San Francisco, CA*
- Spearheaded the redesign of core ingestion services, processing **50M+ events daily** with 99.99% uptime.
- Reduced overall cloud infrastructure expenditure by **32%** through resource rightsizing and container optimization.
- Led and mentored a cross-functional squad of 10 engineers across backend and infrastructure disciplines.

### Senior Software Engineer — Nexus Platforms
*2019 – 2022 | Austin, TX*
- Designed and migrated monolithic services into containerized Django microservices.
- Implemented real-time caching layers that decreased p99 API latency from 450ms to 48ms.
- Built automated release pipelines reducing production deployment time from 40 minutes to under 5 minutes.

## Key Projects
- **High-Throughput Task Queue:** Open-source asynchronous task worker handling 10k tasks/sec with zero drops.
- **Stateless Document Engine:** Client-side document renderer with custom A4 print calibration and font subsetting.

## Education
**B.S. in Computer Science** — University of California, Berkeley *(Honors, Magna Cum Laude)*
"""

MEETING_MARKDOWN = """# Product Strategy & Architecture Review
**Date:** October 1, 2026 • **Facilitator:** Product Team • **Status:** Approved

---

## Meeting Attendees
- **Alex Morgan** (Lead Architect)
- **Sarah Chen** (Head of Product)
- **Marcus Brody** (Design Director)
- **Elena Rostova** (Quality Assurance Lead)

## Key Objectives
1. Review roadmap for Q4 document publishing milestone.
2. Finalize typography hierarchy and color accent tokens.
3. Validate containerized Docker deployment and stateless production runtime.

## Discussion & Decisions

### 1. Stateless In-Memory Architecture
The team confirmed that **markdowntopdf** will remain strictly stateless:
- No user-uploaded files or editor contents will be stored in a database or disk cache.
- Document previews are processed in-memory via lightweight API endpoints.
- Full privacy compliance is maintained across all environments.

### 2. Deliverables & Ownership

| Initiative | Owner | Target Date | Status |
| :--- | :--- | :--- | :--- |
| Docker Containerization | Alex M. | Nov 15, 2026 | In Progress |
| Print CSS Calibration | Marcus B. | Nov 20, 2026 | Completed |
| Security & Memory Audit | Elena R. | Dec 01, 2026 | Scheduled |

## Action Items
- [x] Implement multi-stage Dockerfile and docker-compose orchestration
- [x] Configure WhiteNoise static asset pipeline for production
- [ ] Add browser automated regression tests for print media queries
- [ ] Publish documentation and keyboard shortcuts guide
"""

TECHSPEC_MARKDOWN = """# RFC-104: High-Performance Stateless Document Generator
**Author:** Platform Engineering • **Version:** 1.0.0 • **Status:** Proposed

---

## 1. Abstract
This specification describes the architecture and runtime execution model of `markdowntopdf`, a privacy-first web utility for rendering markdown documents into publication-quality PDFs using native browser layout engines.

## 2. System Architecture

```
[ Markdown Source ] ──> [ In-Memory Engine ] ──> [ Live Canvas ]
                                                        │
                                                        ▼
                                             [ Print-Optimized PDF ]
```

### Core Design Constraints
1. **Zero State:** No database connections (`DATABASES = {}`). No file persistence.
2. **Deterministic Print Output:** Standardized A4 page geometry with calibrated print margins (`16mm 16mm 18mm`).
3. **Container-Ready:** Lean Python 3.12 container running Gunicorn with WhiteNoise static compression.

## 3. API Surface

### `POST /preview/`
Accepts a form payload with `markdown` string. Returns parsed HTML structure.
- **Max Payload:** 1 MB (`MAX_BYTES`)
- **Content-Type:** `application/json`

### `POST /upload/`
Accepts a single `.md` or `.txt` file multipart upload. Returns decoded UTF-8 text.

## 4. Deployment

```bash
# Build and run with Docker Compose
docker compose up -d --build
```
"""

TEMPLATES = {
    "sample": SAMPLE_MARKDOWN,
    "resume": RESUME_MARKDOWN,
    "meeting": MEETING_MARKDOWN,
    "techspec": TECHSPEC_MARKDOWN,
    "empty": "# Document Title\n\nWrite your markdown content here...",
}


def index(request):
    return render(request, "converter/index.html", {
        "typefaces": TYPEFACES,
        "colours": COLOURS,
        "fonts_url": FONTS_URL,
        "sample": SAMPLE_MARKDOWN,
        "templates_json": json.dumps(TEMPLATES),
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
