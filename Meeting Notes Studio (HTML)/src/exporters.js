/* Meeting Notes Studio: file import and export (all in the browser). */
(function (root) {
  'use strict';
  const T = () => root.Templates;

  // ---------------- import: .docx (Teams "Download as Word") ----------------
  async function readDocx(file) {
    const buf = new Uint8Array(await file.arrayBuffer());
    const dv = new DataView(buf.buffer);
    let eocd = -1;
    for (let i = buf.length - 22; i >= Math.max(0, buf.length - 70000); i--) if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
    if (eocd < 0) throw new Error('This does not look like a Word file.');
    const count = dv.getUint16(eocd + 10, true);
    let p = dv.getUint32(eocd + 16, true);
    for (let n = 0; n < count; n++) {
      const method = dv.getUint16(p + 10, true), csize = dv.getUint32(p + 20, true);
      const nlen = dv.getUint16(p + 28, true), xlen = dv.getUint16(p + 30, true), clen = dv.getUint16(p + 32, true);
      const off = dv.getUint32(p + 42, true);
      const name = new TextDecoder().decode(buf.subarray(p + 46, p + 46 + nlen));
      if (name === 'word/document.xml') {
        const lnl = dv.getUint16(off + 26, true), lxl = dv.getUint16(off + 28, true);
        const data = buf.subarray(off + 30 + lnl + lxl, off + 30 + lnl + lxl + csize);
        let xml;
        if (method === 0) xml = new TextDecoder().decode(data);
        else {
          const ds = new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
          xml = await new Response(ds).text();
        }
        return xml
          .replace(/<w:tab\/>/g, '\t').replace(/<w:br[^>]*\/>/g, '\n')
          .replace(/<\/w:p>/g, '\n').replace(/<[^>]+>/g, '')
          .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'")
          .replace(/\n{3,}/g, '\n\n').trim();
      }
      p += 46 + nlen + xlen + clen;
    }
    throw new Error('No text found in this Word file.');
  }
  async function readFile(file) {
    if (/\.docx$/i.test(file.name)) return readDocx(file);
    return (await file.text()).replace(/^﻿/, '');
  }

  function download(blob, name) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
  }
  const safeName = (s) => (s || 'meeting').replace(/\s*:\s*/g, ' - ').replace(/[\\/*?"<>|]+/g, '-').replace(/\s+/g, ' ').trim().slice(0, 80) || 'meeting';

  // ---------------- export: PDF (browser print → Save as PDF) ----------------
  function pdf(tpl) {
    let st = document.getElementById('page-style');
    if (!st) { st = document.createElement('style'); st.id = 'page-style'; document.head.appendChild(st); }
    st.textContent = `@page{size:A4 ${tpl.orient};margin:0}`;
    document.body.classList.add('printing');
    const done = () => { document.body.classList.remove('printing'); window.removeEventListener('afterprint', done); };
    window.addEventListener('afterprint', done);
    setTimeout(() => { window.print(); setTimeout(done, 500); }, 60);
  }

  // ---------------- export: Excel tracker ----------------
  async function excel(d, tpl) {
    const ExcelJS = root.ExcelJS;
    const wb = new ExcelJS.Workbook();
    wb.creator = 'Meeting Notes Studio';
    const A = (tpl.accent || '#3A1E4A').replace('#', '').toUpperCase();
    const DARK = '2B2B35';
    const fill = (c) => ({ type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF' + c } });
    const thin = { style: 'thin', color: { argb: 'FFE3E0E8' } };
    const box = { top: thin, left: thin, bottom: thin, right: thin };
    const title = d.meta.title || 'Meeting';

    function banner(ws, text, sub, cols) {
      ws.mergeCells(1, 1, 1, cols); ws.mergeCells(2, 1, 2, cols);
      const c1 = ws.getCell(1, 1), c2 = ws.getCell(2, 1);
      c1.value = text; c1.font = { size: 18, bold: true, color: { argb: 'FFFFFFFF' } }; c1.fill = fill(DARK); c1.alignment = { vertical: 'middle', indent: 1 };
      c2.value = sub; c2.font = { size: 10, italic: true, color: { argb: 'FFFFFFFF' } }; c2.fill = fill(A); c2.alignment = { vertical: 'middle', indent: 1 };
      ws.getRow(1).height = 34; ws.getRow(2).height = 20;
    }
    function table(ws, name, headers, rows, widths, startRow) {
      ws.columns = widths.map((w) => ({ width: w }));
      ws.addTable({
        name, ref: `A${startRow}`, headerRow: true, style: { theme: 'TableStyleLight1', showRowStripes: true },
        columns: headers.map((h) => ({ name: h, filterButton: true })),
        rows: rows.length ? rows : [headers.map((h, i) => (i === 1 ? '(none)' : ''))],
      });
      const hr = ws.getRow(startRow);
      hr.eachCell((c) => { c.fill = fill(DARK); c.font = { bold: true, color: { argb: 'FFFFFFFF' } }; c.border = box; c.alignment = { vertical: 'middle', wrapText: true }; });
      const last = startRow + Math.max(rows.length, 1);
      for (let r = startRow + 1; r <= last; r++) ws.getRow(r).eachCell({ includeEmpty: true }, (c) => { c.alignment = { vertical: 'top', wrapText: true }; c.border = box; });
      ws.views = [{ state: 'frozen', ySplit: startRow }];
      ws.pageSetup = { orientation: 'landscape', fitToPage: true, fitToWidth: 1, fitToHeight: 0, paperSize: 9 };
      return { first: startRow + 1, last };
    }

    // Overview first so it opens first; filled after the tracker exists
    const ov = wb.addWorksheet('Overview', { views: [{ showGridLines: false }] });
    const at = wb.addWorksheet('Action tracker');
    banner(at, `${title}: action tracker`, 'Change Status as work moves on: the Overview updates by itself.', 7);
    const rows = d.actions.map((a, i) => [i + 1, a.text, a.owner || 'Unassigned', a.due || '', a.priority || 'Medium', a.status || 'Open', a.source || '']);
    const r = table(at, 'Actions', ['#', 'Action', 'Owner', 'Due', 'Priority', 'Status', 'From the transcript'], rows, [5, 50, 20, 18, 11, 14, 50], 4);
    for (let i = r.first; i <= r.last; i++) {
      at.getCell(`F${i}`).dataValidation = { type: 'list', allowBlank: false, formulae: ['"Open,In progress,Done"'] };
      at.getCell(`G${i}`).font = { italic: true, size: 9, color: { argb: 'FF8A8A8A' } };
      ['A', 'E', 'F'].forEach((c) => { at.getCell(`${c}${i}`).alignment = { horizontal: 'center', vertical: 'top' }; });
    }
    const R = `${r.first}:`, rng = (c) => `'Action tracker'!$${c}$${r.first}:$${c}$${r.last}`;
    at.addConditionalFormatting({ ref: `E${r.first}:E${r.last}`, rules: [
      { type: 'cellIs', operator: 'equal', formulae: ['"High"'], style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: 'FFFBE3EA' } }, font: { bold: true, color: { argb: 'FFA3264F' } } } },
      { type: 'cellIs', operator: 'equal', formulae: ['"Medium"'], style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: 'FFFCEBD9' } }, font: { bold: true, color: { argb: 'FF9A5410' } } } },
      { type: 'cellIs', operator: 'equal', formulae: ['"Low"'], style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: 'FFE3F2E6' } }, font: { bold: true, color: { argb: 'FF2E7D45' } } } },
    ] });
    at.addConditionalFormatting({ ref: `A${r.first}:G${r.last}`, rules: [{ type: 'expression', formulae: [`$F${r.first}="Done"`], style: { font: { strike: true, color: { argb: 'FFA0A0A0' } } } }] });
    at.addConditionalFormatting({ ref: `C${r.first}:D${r.last}`, rules: [{ type: 'expression', formulae: [`OR($C${r.first}="Unassigned",LEN(C${r.first})=0)`], style: { fill: { type: 'pattern', pattern: 'solid', bgColor: { argb: 'FFFFF1C9' } } } }] });
    void R;

    const de = wb.addWorksheet('Decisions');
    banner(de, `${title}: decisions`, 'What the group agreed.', 3);
    table(de, 'Decisions', ['#', 'Decision', 'Agreed by'], d.decisions.map((x, i) => [i + 1, x.text, x.by || '']), [5, 70, 34], 4);
    const qr = wb.addWorksheet('Questions and risks');
    banner(qr, `${title}: open questions and risks`, 'Raised but not settled yet.', 3);
    table(qr, 'Open', ['Type', 'Item', 'Raised by'], d.questions.map((q) => ['Question', q.text, q.by || '']).concat(d.risks.map((x) => ['Risk', x.text, ''])), [12, 70, 26], 4);
    if (d.notes.length) {
      const nt = wb.addWorksheet('Discussion');
      banner(nt, `${title}: discussion notes`, 'Status updates from the meeting.', 2);
      table(nt, 'Notes', ['#', 'Note'], d.notes.map((n, i) => [i + 1, n.text]), [5, 100], 4);
    }

    // Overview
    ov.columns = [{ width: 2 }].concat(Array(10).fill({ width: 13 }));
    banner(ov, `${title}: minutes and actions`, [d.meta.date, d.meta.time, d.meta.location].filter(Boolean).join(' · ') || 'Made with Meeting Notes Studio', 11);
    const has = d.actions.length > 0;
    const tiles = [
      ['Actions', has ? { formula: `COUNTA(${rng('B')})` } : 0, 'E0527F'],
      ['Still open', has ? { formula: `COUNTIF(${rng('F')},"<>Done")` } : 0, '5371D1'],
      ['High priority open', has ? { formula: `COUNTIFS(${rng('E')},"High",${rng('F')},"<>Done")` } : 0, 'E88F30'],
      ['No owner', has ? { formula: `COUNTIF(${rng('C')},"Unassigned")` } : 0, '7A96EA'],
      ['Decisions', d.decisions.length, A],
    ];
    tiles.forEach(([label, val, col], k) => {
      const c0 = 2 + k * 2;
      ov.mergeCells(4, c0, 4, c0 + 1); ov.mergeCells(5, c0, 6, c0 + 1);
      const l = ov.getCell(4, c0), v = ov.getCell(5, c0);
      l.value = label; v.value = val;
      l.font = { size: 10, bold: true, color: { argb: 'FFFFFFFF' } }; v.font = { size: 24, bold: true, color: { argb: 'FFFFFFFF' } };
      l.alignment = v.alignment = { horizontal: 'center', vertical: 'middle' };
      for (let rr = 4; rr <= 6; rr++) for (let cc = c0; cc <= c0 + 1; cc++) ov.getCell(rr, cc).fill = fill(col);
    });
    const head = (row, text) => { const c = ov.getCell(row, 2); c.value = text; c.font = { size: 13, bold: true, color: { argb: 'FF' + DARK } }; for (let cc = 2; cc <= 11; cc++) ov.getCell(row, cc).border = { bottom: { style: 'medium', color: { argb: 'FF' + A } } }; };
    head(8, 'Summary');
    ov.mergeCells('B9:K11');
    const s = ov.getCell('B9'); s.value = d.summary; s.alignment = { wrapText: true, vertical: 'top' };
    head(13, 'Open actions per owner');
    const owners = [...new Set(d.actions.map((a) => a.owner || 'Unassigned'))];
    ['Owner', 'Open', 'Done'].forEach((h, j) => { const c = ov.getCell(14, 2 + j); c.value = h; c.fill = fill(DARK); c.font = { bold: true, color: { argb: 'FFFFFFFF' } }; });
    owners.forEach((o, i) => {
      const row = 15 + i;
      ov.getCell(row, 2).value = o;
      ov.getCell(row, 3).value = { formula: `COUNTIFS(${rng('C')},B${row},${rng('F')},"<>Done")` };
      ov.getCell(row, 4).value = { formula: `COUNTIFS(${rng('C')},B${row},${rng('F')},"Done")` };
      [2, 3, 4].forEach((cc) => { ov.getCell(row, cc).border = box; });
    });
    if (owners.length) ov.addConditionalFormatting({ ref: `C15:C${14 + owners.length}`, rules: [{ type: 'dataBar', minLength: 0, maxLength: 100, cfvo: [{ type: 'num', value: 0 }, { type: 'max' }], color: { argb: 'FF' + A }, gradient: false }] });
    const pr = 16 + owners.length;
    head(pr, 'Decisions');
    d.decisions.forEach((x, i) => { ov.mergeCells(pr + 1 + i, 2, pr + 1 + i, 11); const c = ov.getCell(pr + 1 + i, 2); c.value = `✔  ${x.text}`; c.alignment = { wrapText: true }; });
    const qrow = pr + 2 + d.decisions.length;
    head(qrow, 'Open questions and risks');
    d.questions.concat(d.risks).forEach((x, i) => { ov.mergeCells(qrow + 1 + i, 2, qrow + 1 + i, 11); ov.getCell(qrow + 1 + i, 2).value = `${x.type === 'risk' ? '⚑' : '?'}  ${x.text}`; });
    ov.pageSetup = { orientation: 'landscape', fitToPage: true, fitToWidth: 1, fitToHeight: 1, paperSize: 9 };

    const out = await wb.xlsx.writeBuffer();
    download(new Blob([out], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), `${safeName(title)} - action tracker.xlsx`);
  }

  // ---------------- export: Word (.doc that Word opens and edits) ----------------
  function word(d, tpl) {
    const e = T().esc, A = tpl.accent || '#1F3A5F';
    const th = `style="background:${A};color:#fff;text-align:left;padding:5px 8px;border:1px solid ${A}"`;
    const td = 'style="padding:5px 8px;border:1px solid #d9d9d9;vertical-align:top"';
    const h2 = (t) => `<h2 style="color:${A};font-size:14pt;border-bottom:1px solid ${A};margin:14pt 0 6pt">${t}</h2>`;
    const ul = (arr) => `<ul>${arr.map((x) => `<li>${e(x)}</li>`).join('')}</ul>`;
    const m = d.meta;
    const html = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word"><head><meta charset="utf-8"><title>${e(m.title)}</title>
      <!--[if gte mso 9]><xml><w:WordDocument><w:View>Print</w:View><w:Zoom>100</w:Zoom></w:WordDocument></xml><![endif]-->
      <style>@page{size:${tpl.orient === 'landscape' ? '29.7cm 21cm;mso-page-orientation:landscape' : '21cm 29.7cm'};margin:2cm}body{font-family:Calibri,Arial,sans-serif;font-size:11pt;color:#222}</style></head><body>
      <h1 style="color:${A};font-size:22pt;margin:0">${e(m.title || 'Meeting minutes')}</h1>
      <p style="color:#666">${e([m.date, m.time, m.location].filter(Boolean).join(' · '))}</p>
      <table style="border-collapse:collapse;width:100%">
        <tr><td ${td} width="120" nowrap><b>Present</b></td><td ${td}>${e((m.attendees || []).join(', '))}</td></tr>
        ${m.chair ? `<tr><td ${td}><b>Chair</b></td><td ${td}>${e(m.chair)}</td></tr>` : ''}
        ${m.minuteTaker ? `<tr><td ${td}><b>Minutes by</b></td><td ${td}>${e(m.minuteTaker)}</td></tr>` : ''}
      </table>
      ${m.agenda && m.agenda.length ? h2('Agenda') + `<ol>${m.agenda.map((a) => `<li>${e(a)}</li>`).join('')}</ol>` : ''}
      ${h2('Summary')}<p>${e(d.summary)}</p>
      ${d.notes.length ? h2('Discussion') + ul(d.notes.map((n) => n.text)) : ''}
      ${h2('Decisions')}${d.decisions.length ? ul(d.decisions.map((x) => x.text + (x.by ? ` (agreed by ${x.by})` : ''))) : '<p>None recorded.</p>'}
      ${h2('Actions')}<table style="border-collapse:collapse;width:100%"><tr><th ${th}>#</th><th ${th}>Action</th><th ${th}>Owner</th><th ${th}>Due</th><th ${th}>Priority</th><th ${th}>Status</th></tr>
      ${d.actions.map((a, i) => `<tr><td ${td}>${i + 1}</td><td ${td}>${e(a.text)}</td><td ${td}>${e(a.owner || 'To be assigned')}</td><td ${td}>${e(a.due || '–')}</td><td ${td}>${e(a.priority)}</td><td ${td}>${e(a.status)}</td></tr>`).join('')}</table>
      ${d.questions.length ? h2('Open questions') + ul(d.questions.map((q) => q.text)) : ''}
      ${d.risks.length ? h2('Risks') + ul(d.risks.map((x) => x.text)) : ''}
      <p style="margin-top:14pt"><b>Next meeting:</b> ${e(m.nextMeeting || 'To be confirmed')}</p></body></html>`;
    download(new Blob(['﻿', html], { type: 'application/msword' }), `${safeName(m.title)} - minutes.doc`);
  }

  // ---------------- copy for email (rich text) ----------------
  async function copyEmail(d) {
    const html = T().render('email', d).replace(/<div class="mailhead">[\s\S]*?<\/div><\/div>/, '');
    const box = document.createElement('div');
    box.innerHTML = html;
    // inline the few styles mail clients need
    box.querySelectorAll('table').forEach((t) => t.setAttribute('style', 'border-collapse:collapse;font-family:Arial,sans-serif;font-size:13px'));
    box.querySelectorAll('th').forEach((t) => t.setAttribute('style', 'background:#E8F0FE;color:#1a3e8a;border:1px solid #D2DCF0;padding:6px;text-align:left'));
    box.querySelectorAll('td').forEach((t) => t.setAttribute('style', 'border:1px solid #E3E6EA;padding:6px;vertical-align:top'));
    const rich = `<div style="font-family:Arial,sans-serif;font-size:14px;color:#202124">${box.querySelector('.mail').innerHTML}</div>`;
    box.style.cssText = 'position:fixed;left:-9999px;top:0;width:700px';
    document.body.appendChild(box);
    const plain = box.querySelector('.mail').innerText.replace(/\n{3,}/g, '\n\n').trim();
    box.remove();
    try {
      await navigator.clipboard.write([new ClipboardItem({ 'text/html': new Blob([rich], { type: 'text/html' }), 'text/plain': new Blob([plain], { type: 'text/plain' }) })]);
      return true;
    } catch (err) {
      const tmp = document.createElement('div');
      tmp.innerHTML = rich; tmp.style.position = 'fixed'; tmp.style.left = '-9999px';
      document.body.appendChild(tmp);
      const range = document.createRange(); range.selectNodeContents(tmp);
      const sel = getSelection(); sel.removeAllRanges(); sel.addRange(range);
      const ok = document.execCommand('copy');
      sel.removeAllRanges(); tmp.remove();
      return ok;
    }
  }

  function subjectLine(d) { return `Minutes: ${d.meta.title || 'meeting'}${d.meta.date ? ' (' + d.meta.date + ')' : ''}`; }

  root.Exporters = { readFile, pdf, excel, word, copyEmail, subjectLine, download };
})(typeof window !== 'undefined' ? window : globalThis);
