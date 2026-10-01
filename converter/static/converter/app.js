(function () {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  const body = document.body;
  const root = document.documentElement;
  const ta = $('#editor');
  const gutter = $('#gutter');
  const preview = $('#preview');
  const csrf = $('input[name=csrfmiddlewaretoken]') ? $('input[name=csrfmiddlewaretoken]').value : '';

  let lineCount = 0, seq = 0, timer = null, toastTimer = null;

  /* ── templates data ───────────────────────── */
  let templates = {};
  try {
    const tEl = $('#templatesData');
    if (tEl) templates = JSON.parse(tEl.textContent || '{}');
  } catch (e) {
    console.error('Failed to parse templates JSON:', e);
  }

  /* ── toast helper ─────────────────────────── */
  function toast(msg) {
    const t = $('#toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('show'), 3200);
  }

  /* ── document statistics ─────────────────── */
  function updateStats() {
    const text = ta.value;
    const words = (text.trim().match(/\S+/g) || []).length;
    const chars = text.length;
    const readMin = Math.max(1, Math.ceil(words / 200));

    const wc = $('#wordCount');
    const cc = $('#charCount');
    const rt = $('#readTime');
    if (wc) wc.textContent = words.toLocaleString();
    if (cc) cc.textContent = chars.toLocaleString();
    if (rt) rt.textContent = readMin;
  }

  /* ── gutter numbers ──────────────────────── */
  function updateGutter() {
    const n = ta.value.split('\n').length;
    if (n === lineCount) return;
    lineCount = n;
    const nums = new Array(n);
    for (let i = 0; i < n; i++) nums[i] = i + 1;
    gutter.textContent = nums.join('\n');
  }

  /* ── live preview (rendered by Django) ───── */
  function render() {
    clearTimeout(timer);
    const id = ++seq;
    const fd = new FormData();
    fd.append('markdown', ta.value);
    return fetch(body.dataset.previewUrl, {
      method: 'POST',
      body: fd,
      headers: { 'X-CSRFToken': csrf }
    })
      .then(r => r.json().then(d => { if (!r.ok) throw new Error(d.error || 'Preview failed'); return d; }))
      .then(d => { if (id === seq) preview.innerHTML = d.html; })
      .catch(err => toast(err.message || 'Could not update preview.'));
  }

  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(render, 180);
  }

  function changed() {
    updateGutter();
    updateStats();
    schedule();
    ta.focus();
  }

  ta.addEventListener('input', () => {
    updateGutter();
    updateStats();
    schedule();
  });
  ta.addEventListener('scroll', () => { gutter.scrollTop = ta.scrollTop; });

  /* ── toolbar actions ─────────────────────── */
  function wrap(before, after, placeholder) {
    const s = ta.selectionStart, e = ta.selectionEnd;
    const sel = ta.value.slice(s, e) || placeholder;
    ta.setRangeText(before + sel + after, s, e, 'end');
    ta.setSelectionRange(s + before.length, s + before.length + sel.length);
    changed();
  }

  function mapLines(fn) {
    const v = ta.value;
    const s = ta.selectionStart ? v.lastIndexOf('\n', ta.selectionStart - 1) + 1 : 0;
    let e = v.indexOf('\n', ta.selectionEnd);
    if (e === -1) e = v.length;
    const out = v.slice(s, e).split('\n').map(fn).join('\n');
    ta.setRangeText(out, s, e, 'select');
    changed();
  }

  const toggle = p => l => (l.startsWith(p) ? l.slice(p.length) : p + l);
  const heading = p => l => {
    const bare = l.replace(/^#{1,6}\s+/, '');
    return l.startsWith(p) ? bare : p + bare;
  };

  function insertHr() {
    const s = ta.selectionStart, e = ta.selectionEnd;
    ta.setRangeText('\n\n---\n\n', s, e, 'end');
    changed();
  }

  /* Fix: repair common Markdown slips (outside code fences). */
  function fix() {
    let inFence = false, prevHeading = false;
    const out = [];
    ta.value.split('\n').forEach(raw => {
      if (/^\s*(```|~~~)/.test(raw)) { inFence = !inFence; out.push(raw); prevHeading = false; return; }
      if (inFence) { out.push(raw); return; }
      let l = raw.replace(/^(#{1,6})([^#\s])/, '$1 $2').replace(/^(\s*)[•▪●]\s+/, '$1- ');
      const isHeading = /^#{1,6}\s/.test(l);
      if (isHeading && out.length && out[out.length - 1].trim() !== '') out.push('');
      if (prevHeading && l.trim() !== '') out.push('');
      out.push(l);
      prevHeading = isHeading;
    });
    ta.value = out.join('\n');
    changed();
    toast('Fixed common Markdown issues');
  }

  /* Beautify: tidy whitespace (outside code fences). */
  function beautify() {
    let inFence = false, blank = 0;
    const out = [];
    ta.value.split('\n').forEach(raw => {
      if (/^\s*(```|~~~)/.test(raw)) { inFence = !inFence; blank = 0; out.push(raw.replace(/\s+$/, '')); return; }
      if (inFence) { out.push(raw); return; }
      const hardBreak = / {2}$/.test(raw) && raw.trim() !== '';
      const l = hardBreak ? raw : raw.replace(/\s+$/, '');
      if (l.trim() === '') {
        blank++;
        if (blank > 1 || out.length === 0) return;
      } else { blank = 0; }
      out.push(l);
    });
    while (out.length && out[out.length - 1].trim() === '') out.pop();
    ta.value = out.join('\n') + '\n';
    changed();
    toast('Document tidied');
  }

  const actions = {
    bold: () => wrap('**', '**', 'bold text'),
    italic: () => wrap('*', '*', 'italic text'),
    underline: () => wrap('<u>', '</u>', 'underlined'),
    strike: () => wrap('~~', '~~', 'strikethrough'),
    h1: () => mapLines(heading('# ')),
    h2: () => mapLines(heading('## ')),
    h3: () => mapLines(heading('### ')),
    ul: () => mapLines(toggle('- ')),
    tasks: () => mapLines(toggle('- [ ] ')),
    quote: () => mapLines(toggle('> ')),
    code: () => wrap('`', '`', 'code'),
    block: () => wrap('```\n', '\n```', 'code'),
    link: () => wrap('[', '](https://)', 'link text'),
    image: () => wrap('![', '](https://)', 'alt text'),
    hr: insertHr,
    fix: fix,
    beautify: beautify,
  };

  $$('[data-act]').forEach(btn => btn.addEventListener('click', () => actions[btn.dataset.act]()));

  /* Clear Editor */
  const clearBtn = $('#clearEditorBtn');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      if (!ta.value.trim() || confirm('Clear all content from the editor?')) {
        ta.value = '';
        changed();
        toast('Editor cleared');
      }
    });
  }

  /* ── upload (Django parses the file) ─────── */
  async function uploadFile(file) {
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    try {
      const r = await fetch(body.dataset.uploadUrl, {
        method: 'POST',
        body: fd,
        headers: { 'X-CSRFToken': csrf }
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.error || 'Upload failed');
      ta.value = d.text;
      ta.scrollTop = 0;
      ta.scrollLeft = 0;
      lineCount = 0;
      updateGutter();
      updateStats();
      render();
      toast('Loaded ' + d.name);
    } catch (err) {
      toast(err.message || 'Upload failed');
    }
  }

  const fileInput = $('#fileInput');
  const uploadBtn = $('#uploadBtn');
  if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
      uploadFile(fileInput.files[0]);
      fileInput.value = '';
    });
  }

  const zone = $('#dropzone');
  if (zone) {
    ['dragenter', 'dragover'].forEach(ev => zone.addEventListener(ev, e => {
      if (e.dataTransfer && Array.from(e.dataTransfer.types).includes('Files')) {
        e.preventDefault();
        zone.classList.add('drop');
      }
    }));
    ['dragleave', 'drop'].forEach(ev => zone.addEventListener(ev, () => zone.classList.remove('drop')));
    zone.addEventListener('drop', e => {
      if (e.dataTransfer && e.dataTransfer.files.length) {
        e.preventDefault();
        uploadFile(e.dataTransfer.files[0]);
      }
    });
  }

  /* ── templates menu ──────────────────────── */
  const templateBtn = $('#templateBtn');
  const templateMenu = $('#templateMenu');
  if (templateBtn && templateMenu) {
    templateBtn.addEventListener('click', e => {
      e.stopPropagation();
      const hidden = templateMenu.hasAttribute('hidden');
      if (hidden) {
        templateMenu.removeAttribute('hidden');
        templateBtn.setAttribute('aria-expanded', 'true');
      } else {
        templateMenu.setAttribute('hidden', '');
        templateBtn.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('click', e => {
      if (!templateBtn.contains(e.target) && !templateMenu.contains(e.target)) {
        templateMenu.setAttribute('hidden', '');
        templateBtn.setAttribute('aria-expanded', 'false');
      }
    });

    $$('[data-template]', templateMenu).forEach(item => {
      item.addEventListener('click', () => {
        const key = item.dataset.template;
        if (templates[key] !== undefined) {
          ta.value = templates[key];
          changed();
          toast('Loaded ' + (item.querySelector('.template-name') ? item.querySelector('.template-name').textContent : key) + ' template');
        }
        templateMenu.setAttribute('hidden', '');
        templateBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ── copy markdown ───────────────────────── */
  const copyBtn = $('#copyMarkdownBtn');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(ta.value);
        toast('Markdown copied to clipboard!');
      } catch (err) {
        toast('Could not copy to clipboard.');
      }
    });
  }

  /* ── modal cheatsheet & shortcuts ────────── */
  const helpModal = $('#helpModal');
  const helpBtn = $('#helpBtn');
  const footerShortcutsLink = $('#footerShortcutsLink');
  const modalCloseBtn = $('#modalCloseBtn');
  const modalOkBtn = $('#modalOkBtn');

  function openModal() {
    if (helpModal) helpModal.removeAttribute('hidden');
  }
  function closeModal() {
    if (helpModal) helpModal.setAttribute('hidden', '');
  }

  if (helpBtn) helpBtn.addEventListener('click', openModal);
  if (footerShortcutsLink) footerShortcutsLink.addEventListener('click', e => { e.preventDefault(); openModal(); });
  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
  if (modalOkBtn) modalOkBtn.addEventListener('click', closeModal);

  if (helpModal) {
    helpModal.addEventListener('click', e => {
      if (e.target === helpModal) closeModal();
    });
  }

  /* ── typeface ────────────────────────────── */
  const fontBtns = $$('.font');
  fontBtns.forEach(b => b.addEventListener('click', () => {
    fontBtns.forEach(x => x.classList.toggle('on', x === b));
    root.style.setProperty('--doc-font', b.dataset.family);
  }));

  const pills = $$('.pill');
  pills.forEach(p => p.addEventListener('click', () => {
    pills.forEach(x => x.classList.toggle('on', x === p));
    const f = p.dataset.filter;
    fontBtns.forEach(b => { b.hidden = f !== 'all' && b.dataset.cat !== f; });
  }));

  /* ── colours ─────────────────────────────── */
  const sws = $$('.sw');
  sws.forEach(s => s.addEventListener('click', () => {
    sws.forEach(x => x.classList.toggle('on', x === s));
    root.style.setProperty('--accent', s.dataset.accent);
  }));

  /* ── fine-tune ───────────────────────────── */
  const tune = $('#tune'), panel = $('#tunePanel');
  if (tune && panel) {
    tune.addEventListener('click', () => {
      const open = panel.classList.toggle('open');
      tune.setAttribute('aria-expanded', open);
    });
  }
  const sizeInput = $('#size');
  if (sizeInput) {
    sizeInput.addEventListener('input', e => {
      root.style.setProperty('--doc-size', e.target.value + 'px');
      $('#sizeOut').textContent = e.target.value + 'px';
    });
  }
  const lhInput = $('#lh');
  if (lhInput) {
    lhInput.addEventListener('input', e => {
      root.style.setProperty('--doc-lh', e.target.value);
      $('#lhOut').textContent = (+e.target.value).toFixed(2).replace(/0$/, '');
    });
  }

  /* ── watermark + download ────────────────── */
  const noWmCheckbox = $('#noWm');
  if (noWmCheckbox) {
    noWmCheckbox.addEventListener('change', e => {
      body.classList.toggle('no-wm', e.target.checked);
      const dlNote = $('#dlNote');
      if (dlNote) {
        dlNote.textContent = e.target.checked ? 'Clean export — no watermark' : 'Free download includes a watermark';
      }
    });
  }

  async function triggerDownload() {
    await render();
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    const h1 = preview.querySelector('h1');
    const oldTitle = document.title;
    document.title = (h1 && h1.textContent.trim()) || 'markdowntopdf-document';
    const restore = () => {
      document.title = oldTitle;
      window.removeEventListener('afterprint', restore);
    };
    window.addEventListener('afterprint', restore);
    toast('In print dialog, select “Save as PDF”');
    setTimeout(() => window.print(), 350);
  }

  const downloadBtn = $('#download');
  if (downloadBtn) downloadBtn.addEventListener('click', triggerDownload);

  const navDownloadBtn = $('#navDownloadBtn');
  if (navDownloadBtn) navDownloadBtn.addEventListener('click', triggerDownload);

  /* ── keyboard shortcuts ──────────────────── */
  window.addEventListener('keydown', e => {
    // Escape closes modal or dropdown
    if (e.key === 'Escape') {
      closeModal();
      if (templateMenu) templateMenu.setAttribute('hidden', '');
      return;
    }

    if (!(e.ctrlKey || e.metaKey)) return;
    const k = e.key.toLowerCase();
    if (k === 'b') { e.preventDefault(); actions.bold(); }
    else if (k === 'i') { e.preventDefault(); actions.italic(); }
    else if (k === 'k') { e.preventDefault(); actions.link(); }
    else if (k === 'p') { e.preventDefault(); triggerDownload(); }
  });

  /* Initial setup */
  updateGutter();
  updateStats();
})();
