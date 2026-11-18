/* Meeting Notes Studio: user interface. */
(function () {
  'use strict';
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
  const E = window.Engine, TP = window.Templates, X = window.Exporters;
  const esc = TP.esc;
  const KEY = 'meeting-notes-studio-v1';
  const TYPES = [
    ['action', 'Actions', 'Action'], ['decision', 'Decisions', 'Decision'], ['question', 'Open questions', 'Question'],
    ['risk', 'Risks', 'Risk'], ['note', 'Discussion notes', 'Note'],
  ];
  const today = () => new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  const blankMeta = () => ({ title: '', date: '', time: '', location: '', chair: '', minuteTaker: '', attendees: [], absent: '', agenda: [], nextMeeting: '' });

  let S = { step: 'input', transcript: '', meta: blankMeta(), summary: '', items: [], template: 'formal', filter: 'all', dialect: 'British' };
  try { const saved = JSON.parse(localStorage.getItem(KEY) || 'null'); if (saved && saved.items) S = Object.assign(S, saved); } catch (e) { /* storage blocked: start fresh */ }
  let saveTimer;
  function save() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      try { localStorage.setItem(KEY, JSON.stringify(Object.assign({}, S, { items: S.items.map((i) => Object.assign({}, i, { gram: undefined })) }))); } catch (e) { /* ignore */ }
    }, 250);
  }
  function toast(msg, ms) {
    const t = $('#toast'); t.textContent = msg; t.classList.add('on');
    clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('on'), ms || 2600);
  }
  const style = document.createElement('style'); style.textContent = TP.CSS; document.head.appendChild(style);

  // ---------------- navigation ----------------
  function go(step) {
    S.step = step; save();
    $$('.view').forEach((v) => v.classList.toggle('on', v.id === 'v-' + step));
    $$('.steps button').forEach((b) => { b.classList.toggle('on', b.dataset.step === step); b.disabled = b.dataset.step !== 'input' && !S.items.length && !S.summary; });
    if (step === 'review') renderReview();
    if (step === 'export') renderExport();
    window.scrollTo(0, 0);
  }
  $$('.steps button').forEach((b) => b.addEventListener('click', () => go(b.dataset.step)));
  $('#reset').addEventListener('click', () => {
    if (!confirm('Start over? This clears the transcript and all points on this computer.')) return;
    S = { step: 'input', transcript: '', meta: blankMeta(), summary: '', items: [], template: S.template, filter: 'all', dialect: S.dialect };
    $('#transcript').value = ''; save(); go('input');
  });

  // ---------------- step 1: input ----------------
  const ta = $('#transcript');
  ta.value = S.transcript;
  ta.addEventListener('input', () => { S.transcript = ta.value; save(); });
  const samples = window.SAMPLES || {};
  $('#samples').innerHTML = Object.keys(samples).map((k) => `<button data-s="${esc(k)}">${esc(k)}</button>`).join('');
  $('#samples').addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; ta.value = samples[b.dataset.s]; S.transcript = ta.value; S.meta = blankMeta(); save(); toast('Sample loaded. Click "Find actions and decisions".'); });

  async function takeFile(f) {
    try { ta.value = await X.readFile(f); S.transcript = ta.value; save(); toast(`Loaded ${f.name}`); }
    catch (err) { toast('Could not read that file: ' + err.message, 4000); }
  }
  $('#file').addEventListener('change', (e) => e.target.files[0] && takeFile(e.target.files[0]));
  const drop = $('#drop');
  ['dragenter', 'dragover'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove('over'); }));
  drop.addEventListener('drop', (e) => e.dataTransfer.files[0] && takeFile(e.dataTransfer.files[0]));
  ta.addEventListener('drop', (e) => { if (e.dataTransfer.files[0]) { e.preventDefault(); takeFile(e.dataTransfer.files[0]); } });

  function mergeMeta(found) {
    const m = S.meta;
    Object.keys(found).forEach((k) => {
      const empty = Array.isArray(m[k]) ? !m[k].length : !m[k];
      if (empty && found[k] && (!Array.isArray(found[k]) || found[k].length)) m[k] = found[k];
    });
    if (!m.date) m.date = today();
  }
  $('#go').addEventListener('click', () => {
    if (!ta.value.trim()) { toast('Paste a transcript or notes first.'); return; }
    const r = E.extract(ta.value);
    S.meta = blankMeta(); mergeMeta(r.meta);
    S.items = r.items; S.summary = r.summary; S.filter = 'all';
    save(); go('review');
    const a = r.items.filter((i) => i.type === 'action').length;
    toast(`Found ${a} action${a === 1 ? '' : 's'}, ${r.items.length - a} other points. Now check them.`, 3500);
  });
  $('#copyPrompt').addEventListener('click', async () => {
    const text = E.AI_PROMPT + ta.value;
    try { await navigator.clipboard.writeText(text); }
    catch (e) { const t = document.createElement('textarea'); t.value = text; document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove(); }
    toast('Prompt and transcript copied. Paste them into your approved AI.');
  });
  $('#useAi').addEventListener('click', () => {
    try {
      const r = E.fromAiJson($('#aiAnswer').value);
      const base = E.extract(ta.value || '');
      S.meta = blankMeta(); mergeMeta(base.meta);
      S.items = r.items; S.summary = r.summary || base.summary; save(); go('review');
      toast(`Loaded ${r.items.length} points from the AI answer. Check them like any draft.`, 3500);
    } catch (err) { toast('Could not read that answer: ' + err.message, 4000); }
  });

  // ---------------- step 2: review ----------------
  function itemHtml(it) {
    const typeSel = `<select class="type" title="Type">${TYPES.map(([v, , one]) => `<option value="${v}"${v === it.type ? ' selected' : ''}>${one}</option>`).join('')}</select>`;
    let f = typeSel;
    if (it.type === 'action') {
      f += `<input class="owner" list="people" placeholder="Owner" value="${esc(it.owner)}">`;
      f += `<input class="due" placeholder="Due (e.g. Friday)" value="${esc(it.due)}">`;
      f += `<select class="priority">${['High', 'Medium', 'Low'].map((p) => `<option${p === it.priority ? ' selected' : ''}>${p}</option>`).join('')}</select>`;
      f += `<select class="status">${['Open', 'In progress', 'Done'].map((p) => `<option${p === it.status ? ' selected' : ''}>${p}</option>`).join('')}</select>`;
    } else if (it.type === 'decision') f += `<input class="by" list="people" placeholder="Agreed by" value="${esc(it.by)}" style="width:260px">`;
    else if (it.type === 'question') f += `<input class="by" list="people" placeholder="Raised by" value="${esc(it.by)}">`;
    if (it.source && it.source !== it.text) f += `<button class="orig" title="Replace with the words used in the meeting">Use original words</button>`;
    f += `<button class="del">Delete</button>`;
    const flags = (it.flags || []).map((x) => `<span class="flag ${x.level}">${esc(x.text)}</span>`).join('');
    return `<div class="item t-${it.type}${it.checked ? ' ok' : ''}" data-id="${it.id}">
      <input type="checkbox" class="chk" title="Tick when this point is right"${it.checked ? ' checked' : ''}>
      <textarea class="txt" rows="1" spellcheck="false">${esc(it.text)}</textarea>
      <div class="fields">${f}</div>
      <div class="flags">${flags}<span class="gram"></span></div>
      ${it.source ? `<div class="src">From the meeting: “${esc(it.source)}”${it.speaker ? ' (' + esc(it.speaker.split(' ')[0]) + ')' : ''}</div>` : ''}
    </div>`;
  }
  const needsLook = (it) => !it.checked && ((it.flags || []).some((f) => f.level === 'warn') || (it.gram && it.gram.length));

  function renderReview() {
    const counts = { all: S.items.length, look: S.items.filter(needsLook).length };
    TYPES.forEach(([t]) => { counts[t] = S.items.filter((i) => i.type === t).length; });
    $('#filters').innerHTML = [['all', 'All'], ['look', 'Needs a look']].concat(TYPES.map(([t, many]) => [t, many])).map(([k, l]) => `<button data-f="${k}" class="${S.filter === k ? 'on' : ''}">${l} (${counts[k]})</button>`).join('');
    $('#summary').value = S.summary;
    const show = (it) => S.filter === 'all' || (S.filter === 'look' ? needsLook(it) : it.type === S.filter);
    $('#items').innerHTML = TYPES.filter(([t]) => S.filter === 'all' || S.filter === 'look' || S.filter === t).map(([t, many, one]) => {
      const arr = S.items.filter((i) => i.type === t && show(i));
      if (S.filter === 'look' && !arr.length) return '';
      return `<div class="section-h"><h3>${many}</h3><span class="count">${arr.length}</span><button class="btn small add" data-t="${t}">+ Add ${one.toLowerCase()}</button></div>${arr.map(itemHtml).join('') || `<p class="empty-sec">None found. Add one if the meeting had any.</p>`}`;
    }).join('');
    $('#people').innerHTML = (S.meta.attendees || []).map((p) => `<option value="${esc(p)}">`).join('');
    $$('#items textarea.txt').forEach(autosize);
    S.items.forEach(paintGram);
    renderMeta();
    progress();
  }
  function autosize(t) { t.style.height = 'auto'; t.style.height = t.scrollHeight + 'px'; }
  function progress() {
    const n = S.items.length, c = S.items.filter((i) => i.checked).length;
    $('#progTxt').textContent = n ? `${c} of ${n} points ticked` : 'No points yet';
    $('#progBar').style.width = n ? (c / n) * 100 + '%' : '0';
  }
  const byId = (id) => S.items.find((i) => i.id === id);

  $('#filters').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) { S.filter = b.dataset.f; save(); renderReview(); } });
  $('#summary').addEventListener('input', (e) => { S.summary = e.target.value; save(); });
  $('#items').addEventListener('input', (e) => {
    const box = e.target.closest('.item'); if (!box) return;
    const it = byId(box.dataset.id); const el = e.target;
    if (el.classList.contains('txt')) { it.text = el.value; autosize(el); lintSoon(it); }
    else if (el.classList.contains('owner')) it.owner = el.value;
    else if (el.classList.contains('due')) it.due = el.value;
    else if (el.classList.contains('by')) it.by = el.value;
    save();
  });
  $('#items').addEventListener('change', (e) => {
    const box = e.target.closest('.item'); if (!box) return;
    const it = byId(box.dataset.id); const el = e.target;
    if (el.classList.contains('chk')) { it.checked = el.checked; box.classList.toggle('ok', el.checked); progress(); }
    else if (el.classList.contains('priority')) it.priority = el.value;
    else if (el.classList.contains('status')) it.status = el.value;
    else if (el.classList.contains('type')) { it.type = el.value; if (it.type === 'action' && !it.priority) it.priority = 'Medium'; renderReview(); }
    else if (el.classList.contains('owner') && it.owner) it.flags = (it.flags || []).filter((f) => !/No owner/.test(f.text));
    else if (el.classList.contains('due') && it.due) it.flags = (it.flags || []).filter((f) => !/No deadline/.test(f.text));
    save();
  });
  $('#items').addEventListener('click', (e) => {
    const add = e.target.closest('.add');
    if (add) {
      const it = { id: E.newId(), type: add.dataset.t, text: '', owner: '', due: '', priority: 'Medium', status: 'Open', source: '', speaker: '', flags: [], checked: false, by: '' };
      S.items.push(it); if (S.filter === 'look') S.filter = 'all'; save(); renderReview();
      const t = $(`.item[data-id="${it.id}"] textarea`); if (t) t.focus();
      return;
    }
    const box = e.target.closest('.item'); if (!box) return;
    const it = byId(box.dataset.id);
    if (e.target.classList.contains('del')) { S.items = S.items.filter((x) => x !== it); save(); renderReview(); toast('Deleted.'); }
    else if (e.target.classList.contains('orig')) { it.text = it.source.replace(/^\s*\w[\w ]{0,20}:\s*/, ''); save(); renderReview(); }
    else if (e.target.classList.contains('gram') && e.target.dataset.k != null) {
      const g = it.gram[+e.target.dataset.k]; const rep = e.target.dataset.r;
      it.text = it.text.slice(0, g.start) + rep + it.text.slice(g.end);
      const t = $('textarea.txt', box); t.value = it.text; autosize(t); save(); lintNow(it);
    }
  });
  $('#tickAll').addEventListener('click', () => {
    let n = 0;
    S.items.forEach((i) => { if (!i.checked && !(i.flags || []).some((f) => f.level === 'warn') && !(i.gram && i.gram.length) && i.text.trim()) { i.checked = true; n++; } });
    save(); renderReview(); toast(n ? `Ticked ${n} points that had no notes. Read the rest yourself.` : 'Nothing to tick: the rest need a look.');
  });

  // meeting details
  const META = [['title', 'Meeting name'], ['date', 'Date'], ['time', 'Time'], ['location', 'Location or call'], ['chair', 'Chair'], ['minuteTaker', 'Minutes by'], ['attendees', 'Present (comma-separated)'], ['absent', 'Apologies'], ['nextMeeting', 'Next meeting'], ['agenda', 'Agenda (one per line)']];
  function renderMeta() {
    $('#meta').innerHTML = META.map(([k, l]) => {
      const v = k === 'attendees' ? (S.meta.attendees || []).join(', ') : k === 'agenda' ? (S.meta.agenda || []).join('\n') : S.meta[k] || '';
      return `<label class="f">${l}</label>${k === 'agenda' ? `<textarea class="t" data-m="${k}" rows="3">${esc(v)}</textarea>` : `<input class="t" data-m="${k}" value="${esc(v)}">`}`;
    }).join('');
    $('#dialect').value = S.dialect;
  }
  $('#meta').addEventListener('input', (e) => {
    const k = e.target.dataset.m; if (!k) return;
    S.meta[k] = k === 'attendees' ? e.target.value.split(',').map((s) => s.trim()).filter(Boolean) : k === 'agenda' ? e.target.value.split('\n').map((s) => s.trim()).filter(Boolean) : e.target.value;
    if (k === 'attendees') $('#people').innerHTML = S.meta.attendees.map((p) => `<option value="${esc(p)}">`).join('');
    save();
  });
  $('#toExport').addEventListener('click', () => go('export'));

  // ---------------- grammar check (Harper, runs inside this page) ----------------
  let linterP = null, linterDialect = null;
  function linter() {
    if (linterP && linterDialect === S.dialect) return linterP;
    linterDialect = S.dialect;
    linterP = (async () => {
      const H = window.HarperLib;
      const b64 = ($('#harper-wasm') || {}).textContent || '';
      if (!H || b64.length < 100) throw new Error('not bundled');
      const gz = await (await fetch('data:application/gzip;base64,' + b64.trim())).arrayBuffer();
      const wasm = await new Response(new Blob([gz]).stream().pipeThrough(new DecompressionStream('gzip'))).blob();
      const url = URL.createObjectURL(new Blob([wasm], { type: 'application/wasm' }));
      const l = new H.LocalLinter({ binary: H.createBinaryModuleFromUrl(url, 'slim'), dialect: H.Dialect[S.dialect] });
      await l.setup();
      return l;
    })();
    return linterP;
  }
  const lower = (s) => s.toLowerCase();
  async function lintNow(it) {
    if (!it.text.trim()) { it.gram = []; paintGram(it); return; }
    try {
      const l = await linter();
      const names = new Set([].concat(S.meta.attendees || []).join(' ').split(/\s+/).map(lower));
      const lints = await l.lint(it.text, { language: 'plaintext' });
      it.gram = lints.map((x) => {
        const sp = x.span();
        return { start: sp.start, end: sp.end, problem: x.get_problem_text(), kind: x.lint_kind(), msg: x.message(), sug: x.suggestions().slice(0, 3).map((s) => s.get_replacement_text()) };
      }).filter((g) => !(g.kind === 'Spelling' && (/^[A-ZÄÖÜ]/.test(g.problem) || names.has(lower(g.problem)) || /\d/.test(g.problem))));
      paintGram(it);
      setGramState('ok');
    } catch (err) {
      setGramState(err.message === 'not bundled' ? 'off' : 'err');
    }
  }
  const timers = {};
  function lintSoon(it) { clearTimeout(timers[it.id]); timers[it.id] = setTimeout(() => lintNow(it), 450); }
  function paintGram(it) {
    const box = $(`.item[data-id="${it.id}"] .gram`); if (!box) return;
    box.innerHTML = (it.gram || []).map((g, k) => g.sug.length
      ? g.sug.map((s) => `<button class="flag gram" data-k="${k}" data-r="${esc(s)}" title="${esc(g.msg)}">${esc(g.problem)} → ${esc(s || '(remove)')}</button>`).join('')
      : `<span class="flag gram" title="${esc(g.msg)}">${esc(g.kind)}: “${esc(g.problem)}”</span>`).join('');
  }
  function setGramState(s) {
    const el = $('#gramState');
    el.textContent = { load: 'Grammar check: starting…', ok: 'Grammar check: on (runs on this computer)', off: 'Grammar check: not included in this build', err: 'Grammar check could not start in this browser' }[s];
  }
  async function lintAll() {
    setGramState('load');
    for (const it of S.items) await lintNow(it); // eslint-disable-line no-await-in-loop
    if ($('#v-review').classList.contains('on')) { const f = S.filter; renderReviewCounts(f); }
  }
  function renderReviewCounts() {
    const n = S.items.filter(needsLook).length;
    const b = $('#filters button[data-f="look"]'); if (b) b.textContent = `Needs a look (${n})`;
  }
  $('#dialect').addEventListener('change', (e) => { S.dialect = e.target.value; save(); lintAll(); });

  // ---------------- step 3: design and export ----------------
  function data() {
    const pick = (t) => S.items.filter((i) => i.type === t && i.text.trim());
    return { meta: S.meta, summary: S.summary, actions: pick('action'), decisions: pick('decision'), questions: pick('question'), risks: pick('risk'), notes: pick('note') };
  }
  const tplOf = (id) => TP.list.find((t) => t.id === id) || TP.list[0];
  function renderExport() {
    const d = data();
    const groups = [...new Set(TP.list.map((t) => t.group))];
    $('#gallery').innerHTML = groups.map((g) => `<div class="gal-group">${g}</div>` + TP.list.filter((t) => t.group === g).map((t) => {
      const w = t.orient === 'portrait' ? 794 : 1123;
      return `<button class="tcard${t.id === S.template ? ' on' : ''}" data-t="${t.id}"><div class="thumb"><div style="transform:scale(${96 / w});width:${w}px">${TP.render(t.id, d)}</div></div><div><b>${t.name}</b><small>${t.blurb}</small></div></button>`;
    }).join('')).join('');
    const left = S.items.filter((i) => !i.checked).length;
    $('#warnbar').innerHTML = left ? `<div class="warnbar">${left} point${left === 1 ? ' is' : 's are'} not ticked yet. You can export, but check ${left === 1 ? 'it' : 'them'} first. <button id="backReview">Back to review</button></div>` : '';
    const b = $('#backReview'); if (b) b.addEventListener('click', () => { S.filter = 'all'; go('review'); });
    paintPreview();
  }
  function paintPreview() {
    const t = tplOf(S.template);
    $('#tplName').textContent = t.name;
    const inner = $('#preview');
    inner.innerHTML = TP.render(t.id, data());
    const paper = inner.firstElementChild;
    requestAnimationFrame(() => {
      const avail = $('#stage').clientWidth - 40;
      const sc = Math.min(1, avail / paper.offsetWidth);
      inner.style.transform = `scale(${sc})`;
      inner.style.width = paper.offsetWidth + 'px';
      inner.style.height = paper.offsetHeight + 'px';
      inner.parentElement.style.height = paper.offsetHeight * sc + 40 + 'px';
    });
  }
  window.addEventListener('resize', () => { if (S.step === 'export') paintPreview(); });
  $('#gallery').addEventListener('click', (e) => {
    const b = e.target.closest('.tcard'); if (!b) return;
    S.template = b.dataset.t; save();
    $$('.tcard').forEach((c) => c.classList.toggle('on', c === b));
    paintPreview();
  });
  $('#xPdf').addEventListener('click', () => { $('#print-root').innerHTML = TP.render(S.template, data()); X.pdf(tplOf(S.template)); });
  $('#xXlsx').addEventListener('click', async () => {
    try { await X.excel(data(), tplOf(S.template)); toast('Excel tracker downloaded.'); }
    catch (err) { toast('Excel export failed: ' + err.message, 5000); console.error(err); }
  });
  $('#xDoc').addEventListener('click', () => { X.word(data(), tplOf(S.template)); toast('Word file downloaded. Word opens it and you can keep editing.'); });
  $('#xMail').addEventListener('click', async () => {
    const ok = await X.copyEmail(data());
    toast(ok ? `Copied. Paste into a new email. Subject: ${X.subjectLine(data())}` : 'Copy did not work in this browser. Use the Email summary design and PDF instead.', 4500);
  });

  // ---------------- start ----------------
  go(S.items.length && S.step !== 'input' ? S.step : 'input');
  if (S.items.length) lintAll();
  const origGo = go;
  // lint once when the review step first opens after an extraction
  let lastLinted = null;
  const obs = new MutationObserver(() => {
    if ($('#v-review').classList.contains('on') && lastLinted !== S.items) { lastLinted = S.items; lintAll(); }
  });
  obs.observe($('#v-review'), { attributes: true, attributeFilter: ['class'] });
  void origGo;
  setTimeout(() => { linter().catch(() => {}); }, 1500); // warm up in the background
})();
