"""A small, dependency-free Markdown -> HTML renderer.

Supports: headings (ATX + setext), paragraphs, hard breaks, bold, italic,
underline (<u>), strikethrough, inline code, fenced code, links, images,
autolinks, nested ordered/unordered/task lists, blockquotes, tables,
horizontal rules and backslash escapes.  Raw HTML in the source is escaped.
"""
import html as _html
import re

_FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*([\w+#.-]*)")
_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_HR = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
_LIST = re.compile(r"^(\s*)([-*+]|\d{1,9}[.)])\s+(.*)$")
_QUOTE = re.compile(r"^\s{0,3}>\s?(.*)$")
_SETEXT = re.compile(r"^\s{0,3}(=+|-+)\s*$")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$")
_TASK = re.compile(r"^\[( |x|X)\]\s+(.*)$")

_CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
_ESCAPED = re.compile(r"\\([\\`*_{}\[\]()#+\-.!~|<>])")
_IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
_LINK = re.compile(r'\[([^\]]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
_AUTOLINK = re.compile(r'(?<![\w/"=>])(https?://[^\s<>"\x00]*[^\s<>".,;:!?)\]\x00])')
_STASH = re.compile(r"\x00(\d+)\x00")


def _esc(s):
    return _html.escape(s, quote=False)


def _indent(ws):
    return len(ws.expandtabs(4))


def _safe_url(url):
    low = re.sub(r"[\x00-\x20]+", "", _html.unescape(url)).lower()
    if low.startswith(("javascript:", "vbscript:", "file:")):
        return "#"
    if low.startswith("data:") and not low.startswith("data:image/"):
        return "#"
    return url.strip().replace('"', "%22")


def _format(t):
    t = re.sub(r"&lt;u&gt;(.+?)&lt;/u&gt;", r"<u>\1</u>", t)
    t = re.sub(r"\*\*(.+?)\*\*|__(.+?)__",
               lambda m: "<strong>%s</strong>" % (m.group(1) or m.group(2)), t)
    t = re.sub(r"~~(.+?)~~", r"<del>\1</del>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", t)
    return t


def _inline(text):
    text = text.replace("\x00", "")
    stash = []

    def keep(fragment):
        stash.append(fragment)
        return "\x00%d\x00" % (len(stash) - 1)

    text = _CODE_SPAN.sub(lambda m: keep("<code>%s</code>" % _esc(m.group(2).strip())), text)
    text = _ESCAPED.sub(lambda m: keep(_esc(m.group(1))), text)
    text = _esc(text)
    text = _IMAGE.sub(lambda m: keep('<img src="%s" alt="%s">' % (
        _safe_url(m.group(2)), m.group(1).replace('"', "&quot;"))), text)
    text = _LINK.sub(lambda m: keep('<a href="%s">%s</a>' % (
        _safe_url(m.group(2)), _format(m.group(1)))), text)
    text = _AUTOLINK.sub(lambda m: keep('<a href="%s">%s</a>' % (
        _safe_url(m.group(1)), m.group(1))), text)
    text = _format(text)
    for _ in range(4):
        if "\x00" not in text:
            break
        text = _STASH.sub(lambda m: stash[int(m.group(1))], text)
    return text


def _cells(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|") and not row.endswith("\\|"):
        row = row[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", row)]


def _is_table_start(lines, i):
    return (
        "|" in lines[i]
        and i + 1 < len(lines)
        and "|" in lines[i + 1]
        and bool(_TABLE_SEP.match(lines[i + 1]))
    )


def _is_block_start(lines, i):
    line = lines[i]
    return bool(
        _FENCE.match(line) or _HEADING.match(line) or _HR.match(line)
        or _LIST.match(line) or _QUOTE.match(line) or _is_table_start(lines, i)
    )


def _list(lines, i):
    n = len(lines)
    m = _LIST.match(lines[i])
    base = _indent(m.group(1))
    ordered = m.group(2)[0].isdigit()
    start = int(m.group(2).rstrip(".)")) if ordered else 1
    items = []  # [css_class, html]

    while i < n:
        line = lines[i]
        if not line.strip():
            j = i
            while j < n and not lines[j].strip():
                j += 1
            mj = _LIST.match(lines[j]) if j < n else None
            if mj and _indent(mj.group(1)) >= base:
                i = j
                continue
            break
        m = _LIST.match(line)
        if m:
            ind = _indent(m.group(1))
            if ind < base:
                break
            if ind > base and items:
                sub, i = _list(lines, i)
                items[-1][1] += sub
                continue
            if m.group(2)[0].isdigit() != ordered:
                break
            task = _TASK.match(m.group(3))
            if task:
                box = '<input type="checkbox" disabled%s> ' % (
                    " checked" if task.group(1).lower() == "x" else "")
                items.append(["task-item", box + _inline(task.group(2))])
            else:
                items.append(["", _inline(m.group(3))])
            i += 1
            continue
        if items and _indent(line) > base:
            items[-1][1] += " " + _inline(line.strip())
            i += 1
            continue
        break

    tag = "ol" if ordered else "ul"
    attr = ' start="%d"' % start if ordered and start != 1 else ""
    body = "".join(
        '<li%s>%s</li>' % (' class="%s"' % c if c else "", h) for c, h in items)
    return "<%s%s>%s</%s>" % (tag, attr, body, tag), i


def _blocks(lines):
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        m = _FENCE.match(line)
        if m:
            fence, lang = m.group(1), m.group(2)
            closing = re.compile(r"^\s*%s{%d,}\s*$" % (re.escape(fence[0]), len(fence)))
            i += 1
            buf = []
            while i < n and not closing.match(lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = ' class="language-%s"' % _esc(lang) if lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (cls, _esc("\n".join(buf))))
            continue

        m = _HEADING.match(line)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, _inline(m.group(2)), lvl))
            i += 1
            continue

        if _HR.match(line):
            out.append("<hr>")
            i += 1
            continue

        if _QUOTE.match(line):
            inner = []
            while i < n and _QUOTE.match(lines[i]):
                inner.append(_QUOTE.match(lines[i]).group(1))
                i += 1
            out.append("<blockquote>%s</blockquote>" % _blocks(inner))
            continue

        if _LIST.match(line):
            html_, i = _list(lines, i)
            out.append(html_)
            continue

        if _is_table_start(lines, i):
            head = _cells(line)
            aligns = []
            for c in _cells(lines[i + 1]):
                c = c.strip()
                if c.startswith(":") and c.endswith(":"):
                    aligns.append("center")
                elif c.endswith(":"):
                    aligns.append("right")
                elif c.startswith(":"):
                    aligns.append("left")
                else:
                    aligns.append("")
            i += 2
            rows = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                rows.append(_cells(lines[i]))
                i += 1

            def cell(tag, text, k):
                a = aligns[k] if k < len(aligns) else ""
                style = ' style="text-align:%s"' % a if a else ""
                return "<%s%s>%s</%s>" % (tag, style, _inline(text), tag)

            cols = len(head)
            thead = "<tr>%s</tr>" % "".join(cell("th", c, k) for k, c in enumerate(head))
            tbody = "".join(
                "<tr>%s</tr>" % "".join(
                    cell("td", (r + [""] * cols)[k], k) for k in range(cols))
                for r in rows)
            out.append('<div class="table-wrap"><table><thead>%s</thead><tbody>%s</tbody></table></div>'
                       % (thead, tbody))
            continue

        para = []
        heading = None
        while i < n:
            ln = lines[i]
            if not ln.strip():
                break
            if para and _SETEXT.match(ln):
                heading = (1 if ln.strip()[0] == "=" else 2, " ".join(p.strip() for p in para))
                i += 1
                break
            if para and _is_block_start(lines, i):
                break
            para.append(ln)
            i += 1
        if heading:
            out.append("<h%d>%s</h%d>" % (heading[0], _inline(heading[1]), heading[0]))
        else:
            parts = []
            for ln in para:
                hard = ln.endswith("  ") or ln.endswith("\\")
                s = ln.strip()
                if s.endswith("\\"):
                    s = s[:-1]
                parts.append(_inline(s) + ("<br>" if hard else ""))
            out.append("<p>%s</p>" % "\n".join(parts))

    return "\n".join(out)


def render_markdown(source):
    source = (source or "").replace("\r\n", "\n").replace("\r", "\n")
    return _blocks(source.split("\n"))
