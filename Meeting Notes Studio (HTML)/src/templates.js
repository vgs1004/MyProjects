/* Meeting Notes Studio: 12 output templates.
 * Each template turns the reviewed data into its own page layout and palette.
 * d = { meta, summary, actions, decisions, questions, risks, notes }
 */
(function (root) {
  'use strict';
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const first = (n) => (n || '').split(' ')[0];
  const initials = (n) => (n || '?').split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join('') || '?';
  const AV = ['#E0527F', '#5371D1', '#E88F30', '#2E9E8F', '#8E5BD6', '#C2453D', '#3F8F4A', '#B8860B'];
  const avColor = (n) => { let h = 0; for (const c of n || '') h = (h * 31 + c.charCodeAt(0)) >>> 0; return AV[h % AV.length]; };
  const or = (v, alt) => (v && String(v).trim() ? esc(v) : `<span class="muted">${alt}</span>`);
  const list = (arr, fn, empty) => (arr.length ? arr.map(fn).join('') : `<p class="muted empty">${empty}</p>`);
  const dateLine = (m) => [m.date, m.time].filter(Boolean).join(' · ');
  const DAY = ['today', 'tonight', 'tomorrow', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'end of', 'next'];
  function dueRank(d) {
    const s = (d || '').toLowerCase();
    if (!s) return 999;
    const i = DAY.findIndex((k) => s.includes(k));
    return i < 0 ? 100 : i;
  }
  const people = (d) => {
    const out = [];
    (d.meta.attendees || []).forEach((p) => p && !out.includes(p) && out.push(p));
    d.actions.forEach((a) => a.owner && !out.includes(a.owner) && out.push(a.owner));
    return out;
  };
  const prioClass = (p) => 'p-' + (p || 'Medium').toLowerCase();
  const statusClass = (s) => 's-' + (s || 'Open').toLowerCase().replace(/\s+/g, '-');
  const avatar = (n, size) => `<span class="av" style="background:${n ? avColor(n) : '#9a9a9a'};${size ? `width:${size}px;height:${size}px;font-size:${Math.round(size * 0.4)}px` : ''}">${n ? initials(n) : '?'}</span>`;

  const T = [];

  // 1 ---------------------------------------------------------------- Formal minutes
  T.push({
    id: 'formal', name: 'Formal minutes', group: 'Documents', orient: 'portrait', accent: '#1F3A5F',
    blurb: 'Classic minutes of meeting: details, agenda, numbered sections, action table, sign-off.',
    render: (d) => `
      <header class="hd">
        <div class="mark">MINUTES</div>
        <div><h1>${esc(d.meta.title || 'Meeting minutes')}</h1><p class="sub">${esc(dateLine(d.meta))}</p></div>
      </header>
      <table class="meta">
        <tr><th>Date</th><td>${or(d.meta.date, 'Not recorded')}</td><th>Time</th><td>${or(d.meta.time, '–')}</td></tr>
        <tr><th>Location</th><td>${or(d.meta.location, '–')}</td><th>Chair</th><td>${or(d.meta.chair, '–')}</td></tr>
        <tr><th>Present</th><td colspan="3">${or((d.meta.attendees || []).join(', '), '–')}</td></tr>
        ${d.meta.absent ? `<tr><th>Apologies</th><td colspan="3">${esc(d.meta.absent)}</td></tr>` : ''}
        <tr><th>Minutes by</th><td colspan="3">${or(d.meta.minuteTaker, '–')}</td></tr>
      </table>
      ${d.meta.agenda && d.meta.agenda.length ? `<h2><span>1</span>Agenda</h2><ol class="agenda">${d.meta.agenda.map((a) => `<li>${esc(a)}</li>`).join('')}</ol>` : ''}
      <h2><span>2</span>Summary</h2><p>${esc(d.summary)}</p>
      ${d.notes.length ? `<h2><span>3</span>Discussion</h2><ul>${d.notes.map((n) => `<li>${esc(n.text)}</li>`).join('')}</ul>` : ''}
      <h2><span>4</span>Decisions</h2>
      ${list(d.decisions, (x, i) => `<div class="dec"><b>D${i + 1}</b><div>${esc(x.text)}${x.by ? `<small>Agreed by ${esc(x.by)}</small>` : ''}</div></div>`, 'No decisions recorded.')}
      <h2><span>5</span>Actions</h2>
      <table class="grid"><thead><tr><th>#</th><th>Action</th><th>Owner</th><th>Due</th><th>Priority</th></tr></thead><tbody>
      ${d.actions.map((a, i) => `<tr><td>A${i + 1}</td><td>${esc(a.text)}</td><td>${or(a.owner, 'To be assigned')}</td><td>${or(a.due, '–')}</td><td>${esc(a.priority)}</td></tr>`).join('') || '<tr><td colspan="5" class="muted">No actions.</td></tr>'}
      </tbody></table>
      ${d.questions.length ? `<h2><span>6</span>Open questions</h2><ul>${d.questions.map((q) => `<li>${esc(q.text)}${q.by ? ` <small>(${esc(first(q.by))})</small>` : ''}</li>`).join('')}</ul>` : ''}
      ${d.risks.length ? `<h2><span>7</span>Risks</h2><ul>${d.risks.map((r) => `<li>${esc(r.text)}</li>`).join('')}</ul>` : ''}
      <p class="next"><b>Next meeting:</b> ${or(d.meta.nextMeeting, 'To be confirmed')}</p>
      <div class="sign"><div>Minutes approved by</div><div>Date</div></div>`,
  });

  // 2 ---------------------------------------------------------------- Steering committee
  T.push({
    id: 'steering', name: 'Steering committee', group: 'Documents', orient: 'portrait', accent: '#1E4D3A',
    blurb: 'For senior meetings: overall status, decisions taken, risks and escalations, decisions needed next.',
    render: (d) => {
      const highOpen = d.actions.filter((a) => a.priority === 'High' && a.status !== 'Done');
      const unowned = d.actions.filter((a) => !a.owner);
      const rag = d.risks.length >= 2 || unowned.some((a) => a.priority === 'High') ? ['Red', 'Needs attention'] : d.risks.length || unowned.length || highOpen.length > 2 ? ['Amber', 'Watch closely'] : ['Green', 'On track'];
      return `
      <header class="band"><div><p class="kick">Steering committee</p><h1>${esc(d.meta.title || 'Steering committee minutes')}</h1><p class="sub">${esc(dateLine(d.meta))}${d.meta.chair ? ' · Chair: ' + esc(d.meta.chair) : ''}</p></div>
        <div class="rag rag-${rag[0].toLowerCase()}"><b>${rag[0]}</b><span>${rag[1]}</span></div></header>
      <section class="exec"><h3>Executive summary</h3><p>${esc(d.summary)}</p></section>
      <div class="two">
        <section><h3>Decisions taken</h3>${list(d.decisions, (x) => `<div class="tick">✔<span>${esc(x.text)}</span></div>`, 'None this time.')}</section>
        <section><h3>Decisions needed next</h3>${list(d.questions, (q) => `<div class="ask">?<span>${esc(q.text)}</span></div>`, 'Nothing pending.')}</section>
      </div>
      <h3>Risks and escalations</h3>
      <table class="grid"><thead><tr><th>Risk</th><th>Severity</th><th>Next step</th></tr></thead><tbody>
      ${d.risks.map((r) => { const step = d.actions.find((a) => a.text.toLowerCase().includes((r.text.split(' ').slice(1, 3).join(' ') || '###').toLowerCase())); return `<tr><td>${esc(r.text)}</td><td><span class="sev">High</span></td><td>${step ? esc(step.text) + (step.owner ? ' (' + esc(first(step.owner)) + ')' : '') : '<span class="muted">To be agreed</span>'}</td></tr>`; }).join('') || '<tr><td colspan="3" class="muted">No risks raised.</td></tr>'}
      </tbody></table>
      <h3>Actions</h3>
      <table class="grid"><thead><tr><th>Action</th><th>Owner</th><th>Due</th><th>Priority</th></tr></thead><tbody>
      ${d.actions.map((a) => `<tr><td>${esc(a.text)}</td><td>${or(a.owner, 'Unassigned')}</td><td>${or(a.due, '–')}</td><td><span class="pp ${prioClass(a.priority)}">${esc(a.priority)}</span></td></tr>`).join('')}
      </tbody></table>
      <p class="foot">Present: ${esc((d.meta.attendees || []).join(', '))}${d.meta.nextMeeting ? ' · Next: ' + esc(d.meta.nextMeeting) : ''}</p>`;
    },
  });

  // 3 ---------------------------------------------------------------- Client recap
  T.push({
    id: 'client', name: 'Client recap', group: 'Documents', orient: 'portrait', accent: '#D9644A',
    blurb: 'A friendly follow-up letter for clients or partners: what we agreed, next steps, what is still open.',
    render: (d) => `
      <div class="top"><div class="dot"></div><p>Meeting recap</p><span>${esc(d.meta.date || '')}</span></div>
      <h1>${esc(d.meta.title || 'Our meeting')}</h1>
      <p class="hi">Hi all,</p>
      <p>Thank you for your time today. Here is a short recap so we are all on the same page.</p>
      <div class="ccard sum"><p>${esc(d.summary)}</p></div>
      <h2>What we agreed</h2>
      ${list(d.decisions, (x) => `<div class="agreed"><span>✓</span>${esc(x.text)}</div>`, 'No formal decisions this time.')}
      <h2>Next steps</h2>
      <div class="nsteps">${d.actions.map((a, i) => `<div class="step"><div class="num">${i + 1}</div><div><p>${esc(a.text)}</p><small>${a.owner ? esc(a.owner) : 'Owner to be confirmed'}${a.due ? ' · by ' + esc(a.due) : ''}</small></div></div>`).join('') || '<p class="muted">No next steps.</p>'}</div>
      ${d.questions.length ? `<h2>Still open</h2><ul>${d.questions.map((q) => `<li>${esc(q.text)}</li>`).join('')}</ul>` : ''}
      <p>If anything here does not match your notes, just reply and we will update it.</p>
      <p class="bye">Best regards,<br><b>${esc(d.meta.chair || d.meta.minuteTaker || '')}</b></p>`,
  });

  // 4 ---------------------------------------------------------------- Workshop wall
  T.push({
    id: 'workshop', name: 'Workshop wall', group: 'Visual boards', orient: 'landscape', accent: '#F2B705',
    blurb: 'Sticky notes on a board, coloured by type. Good for workshops and brainstorming sessions.',
    render: (d) => {
      const notes = [].concat(
        d.decisions.map((x) => ['dec', 'Decision', x.text, x.by]),
        d.actions.map((x) => ['act', 'Action', x.text, [x.owner && first(x.owner), x.due].filter(Boolean).join(' · ')]),
        d.questions.map((x) => ['que', 'Question', x.text, first(x.by)]),
        d.risks.map((x) => ['risk', 'Risk', x.text, '']),
        d.notes.map((x) => ['note', 'Note', x.text, ''])
      );
      return `<header><h1>${esc(d.meta.title || 'Workshop')}</h1><p>${esc(dateLine(d.meta))} · ${esc((d.meta.attendees || []).map(first).join(', '))}</p>
        <div class="legend"><span class="w-dec">Decision</span><span class="w-act">Action</span><span class="w-que">Question</span><span class="w-risk">Risk</span><span class="w-note">Note</span></div></header>
        <div class="wall">${notes.map((n, i) => `<div class="sticky w-${n[0]}" style="transform:rotate(${((i * 37) % 7) - 3}deg)"><small>${n[1]}</small><p>${esc(n[2])}</p>${n[3] ? `<em>${esc(n[3])}</em>` : ''}</div>`).join('')}</div>`;
    },
  });

  // 5 ---------------------------------------------------------------- Action tracker
  T.push({
    id: 'tracker', name: 'Action tracker', group: 'Trackers', orient: 'landscape', accent: '#E0527F',
    blurb: 'KPI tiles, actions per owner and a full action table with priority and status. Pairs with the Excel export.',
    render: (d) => {
      const open = d.actions.filter((a) => a.status !== 'Done');
      const owners = {};
      d.actions.forEach((a) => { const k = a.owner || 'Unassigned'; owners[k] = (owners[k] || 0) + 1; });
      const max = Math.max(1, ...Object.values(owners));
      return `<header><div><h1>${esc(d.meta.title || 'Action tracker')}</h1><p>${esc(dateLine(d.meta))}</p></div></header>
      <div class="kpis">
        <div style="--c:#E0527F"><b>${d.actions.length}</b><span>Actions</span></div>
        <div style="--c:#5371D1"><b>${open.length}</b><span>Still open</span></div>
        <div style="--c:#E88F30"><b>${open.filter((a) => a.priority === 'High').length}</b><span>High priority open</span></div>
        <div style="--c:#7A96EA"><b>${d.actions.filter((a) => !a.owner || !a.due).length}</b><span>Missing owner or date</span></div>
        <div style="--c:#3A1E4A"><b>${d.decisions.length}</b><span>Decisions</span></div>
      </div>
      <div class="split">
        <table class="grid"><thead><tr><th>#</th><th>Action</th><th>Owner</th><th>Due</th><th>Priority</th><th>Status</th></tr></thead><tbody>
        ${d.actions.map((a, i) => `<tr class="${a.status === 'Done' ? 'done' : ''}"><td>${i + 1}</td><td>${esc(a.text)}</td><td>${a.owner ? avatar(a.owner, 20) + ' ' + esc(a.owner) : '<span class="warn">Unassigned</span>'}</td><td>${a.due ? esc(a.due) : '<span class="warn">No date</span>'}</td><td><span class="pp ${prioClass(a.priority)}">${esc(a.priority)}</span></td><td><span class="st ${statusClass(a.status)}">${esc(a.status)}</span></td></tr>`).join('')}
        </tbody></table>
        <aside><h3>Actions per owner</h3>${Object.entries(owners).sort((a, b) => b[1] - a[1]).map(([k, v]) => `<div class="obar"><span>${esc(k)}</span><i style="width:${(v / max) * 100}%"></i><b>${v}</b></div>`).join('')}
        <h3>Summary</h3><p>${esc(d.summary)}</p></aside>
      </div>`;
    },
  });

  // 6 ---------------------------------------------------------------- Kanban
  T.push({
    id: 'kanban', name: 'Kanban board', group: 'Visual boards', orient: 'landscape', accent: '#1F8A8A',
    blurb: 'Actions as cards in To do, In progress and Done columns, with owner avatars and due dates.',
    render: (d) => {
      const col = (name, st) => {
        const cards = d.actions.filter((a) => (a.status || 'Open') === st);
        return `<div class="col"><h3>${name}<span>${cards.length}</span></h3>${cards.map((a) => `<div class="kcard ${prioClass(a.priority)}"><p>${esc(a.text)}</p><div class="krow">${avatar(a.owner, 24)}<span>${a.owner ? esc(first(a.owner)) : 'Unassigned'}</span>${a.due ? `<em>${esc(a.due)}</em>` : ''}</div></div>`).join('') || '<p class="muted">Nothing here.</p>'}</div>`;
      };
      return `<header><h1>${esc(d.meta.title || 'Board')}</h1><p>${esc(dateLine(d.meta))}</p></header>
      <div class="board">${col('To do', 'Open')}${col('In progress', 'In progress')}${col('Done', 'Done')}
      <div class="col kside"><h3>Decided</h3>${list(d.decisions, (x) => `<div class="mini">${esc(x.text)}</div>`, 'No decisions.')}<h3>Open questions</h3>${list(d.questions, (x) => `<div class="mini q">${esc(x.text)}</div>`, 'None.')}</div></div>`;
    },
  });

  // 7 ---------------------------------------------------------------- Timeline
  T.push({
    id: 'timeline', name: 'Deadline timeline', group: 'Visual boards', orient: 'portrait', accent: '#4B47B9',
    blurb: 'Actions on a timeline, soonest first, so everyone sees what is due when.',
    render: (d) => {
      const groups = {};
      d.actions.slice().sort((a, b) => dueRank(a.due) - dueRank(b.due)).forEach((a) => { const k = a.due || 'No deadline yet'; (groups[k] = groups[k] || []).push(a); });
      return `<header><p class="kick">What is due when</p><h1>${esc(d.meta.title || 'Timeline')}</h1><p>${esc(dateLine(d.meta))}</p></header>
      <div class="tl">${Object.entries(groups).map(([k, arr]) => `<div class="stop ${k === 'No deadline yet' ? 'nodate' : ''}"><div class="when">${esc(k)}</div><div class="items">${arr.map((a) => `<div class="it ${prioClass(a.priority)}"><p>${esc(a.text)}</p><small>${avatar(a.owner, 18)} ${a.owner ? esc(a.owner) : 'Unassigned'} · ${esc(a.priority)}</small></div>`).join('')}</div></div>`).join('') || '<p class="muted">No actions.</p>'}</div>
      ${d.decisions.length ? `<div class="foot"><b>Decided:</b> ${d.decisions.map((x) => esc(x.text)).join(' · ')}</div>` : ''}`;
    },
  });

  // 8 ---------------------------------------------------------------- Owner matrix
  T.push({
    id: 'raci', name: 'Owner matrix', group: 'Trackers', orient: 'landscape', accent: '#D9822B',
    blurb: 'Who does what: actions against people, with each person\'s workload. Spot gaps and overload.',
    render: (d) => {
      const ppl = people(d);
      const load = ppl.map((p) => d.actions.filter((a) => a.owner === p).length);
      const max = Math.max(1, ...load);
      return `<header><h1>${esc(d.meta.title || 'Owner matrix')}</h1><p>${esc(dateLine(d.meta))} · R = responsible</p></header>
      <table class="mx"><thead><tr><th class="l">Action</th><th>Due</th>${ppl.map((p) => `<th class="pp-h"><div>${avatar(p, 26)}<span>${esc(first(p))}</span></div></th>`).join('')}<th>No owner</th></tr></thead><tbody>
      ${d.actions.map((a) => `<tr><td class="l">${esc(a.text)}</td><td class="due">${esc(a.due || '–')}</td>${ppl.map((p) => `<td>${a.owner === p ? '<span class="r">R</span>' : ''}</td>`).join('')}<td>${a.owner ? '' : '<span class="gap">!</span>'}</td></tr>`).join('')}
      </tbody><tfoot><tr><td class="l">Workload</td><td></td>${load.map((n) => `<td><div class="ld"><i style="height:${(n / max) * 40}px"></i></div><b>${n}</b></td>`).join('')}<td><b>${d.actions.filter((a) => !a.owner).length}</b></td></tr></tfoot></table>`;
    },
  });

  // 9 ---------------------------------------------------------------- Executive one-pager
  T.push({
    id: 'exec', name: 'Executive one-pager', group: 'One-pagers', orient: 'portrait', accent: '#B08D57',
    blurb: 'For busy readers: the headline decision, three numbers, what needs attention, and what happens next.',
    render: (d) => {
      const head = d.decisions[0] ? d.decisions[0].text : d.meta.title || 'Meeting outcome';
      const attention = [].concat(d.risks.map((r) => ['Risk', r.text]), d.actions.filter((a) => !a.owner).map((a) => ['No owner', a.text]), d.actions.filter((a) => a.priority === 'High' && a.owner).map((a) => ['High priority', `${a.text} (${first(a.owner)}${a.due ? ', ' + a.due : ''})`])).slice(0, 5);
      return `<p class="kick">${esc(d.meta.title || 'Meeting')} · ${esc(d.meta.date || '')}</p>
      <h1>${esc(head)}</h1>
      <div class="nums"><div><b>${d.decisions.length}</b><span>decisions</span></div><div><b>${d.actions.length}</b><span>actions</span></div><div><b>${d.questions.length + d.risks.length}</b><span>open issues</span></div></div>
      <div class="cols"><section><h3>In short</h3><p>${esc(d.summary)}</p>${d.decisions.length > 1 ? `<h3>Also decided</h3><ul>${d.decisions.slice(1).map((x) => `<li>${esc(x.text)}</li>`).join('')}</ul>` : ''}</section>
      <section class="att"><h3>Needs attention</h3>${list(attention, (x) => `<div><small>${esc(x[0])}</small><p>${esc(x[1])}</p></div>`, 'Nothing urgent.')}</section></div>
      <div class="nextb"><b>Next</b><span>${or(d.meta.nextMeeting, 'Next meeting to be confirmed')}</span></div>`;
    },
  });

  // 10 ---------------------------------------------------------------- Email
  T.push({
    id: 'email', name: 'Email summary', group: 'One-pagers', orient: 'portrait', accent: '#2563EB',
    blurb: 'Plain, email-friendly layout. Use "Copy for email" to paste it straight into Outlook or Gmail.',
    render: (d) => `
      <div class="mailhead"><div><b>To:</b> ${esc((d.meta.attendees || []).join('; '))}</div><div><b>Subject:</b> Minutes: ${esc(d.meta.title || 'meeting')}${d.meta.date ? ' (' + esc(d.meta.date) + ')' : ''}</div></div>
      <div class="mail">
      <p>Hi all,</p><p>Thanks for joining. Here are the key points from today.</p>
      <p><b>Summary</b><br>${esc(d.summary)}</p>
      ${d.decisions.length ? `<p><b>Decisions</b></p><ul>${d.decisions.map((x) => `<li>${esc(x.text)}</li>`).join('')}</ul>` : ''}
      <p><b>Actions</b></p>
      <table class="mt" cellpadding="6" cellspacing="0"><tr><th align="left">Action</th><th align="left">Owner</th><th align="left">Due</th></tr>
      ${d.actions.map((a) => `<tr><td>${esc(a.text)}</td><td>${a.owner ? esc(a.owner) : '<i>to be assigned</i>'}</td><td>${esc(a.due || '–')}</td></tr>`).join('')}</table>
      ${d.questions.length ? `<p><b>Open questions</b></p><ul>${d.questions.map((q) => `<li>${esc(q.text)}</li>`).join('')}</ul>` : ''}
      ${d.risks.length ? `<p><b>Risks</b></p><ul>${d.risks.map((q) => `<li>${esc(q.text)}</li>`).join('')}</ul>` : ''}
      <p>Please reply if anything is missing or wrong.${d.meta.nextMeeting ? ' Next meeting: ' + esc(d.meta.nextMeeting) + '.' : ''}</p>
      <p>Best regards,<br>${esc(d.meta.minuteTaker || d.meta.chair || '')}</p></div>`,
  });

  // 11 ---------------------------------------------------------------- Stand-up cards
  T.push({
    id: 'standup', name: 'Stand-up cards', group: 'Trackers', orient: 'landscape', accent: '#7C4DCC',
    blurb: 'One card per person with what they will do, by when, and what they raised. Great for team syncs.',
    render: (d) => {
      const ppl = people(d);
      const un = d.actions.filter((a) => !a.owner);
      return `<header><h1>${esc(d.meta.title || 'Team sync')}</h1><p>${esc(dateLine(d.meta))}</p></header>
      <div class="cards">${ppl.map((p) => {
        const mine = d.actions.filter((a) => a.owner === p), qs = d.questions.filter((q) => q.by === p);
        return `<div class="pc"><div class="who">${avatar(p, 38)}<div><b>${esc(p)}</b><small>${mine.length} action${mine.length === 1 ? '' : 's'}</small></div></div>
          <h4>Will do</h4>${list(mine, (a) => `<div class="do ${prioClass(a.priority)}"><span>${esc(a.text)}</span>${a.due ? `<em>${esc(a.due)}</em>` : ''}</div>`, 'Nothing assigned.')}
          ${qs.length ? `<h4>Raised</h4>${qs.map((q) => `<div class="rq">${esc(q.text)}</div>`).join('')}` : ''}</div>`;
      }).join('')}
      ${un.length ? `<div class="pc unc"><div class="who">${avatar('', 38)}<div><b>Needs an owner</b><small>${un.length} open</small></div></div>${un.map((a) => `<div class="do"><span>${esc(a.text)}</span></div>`).join('')}</div>` : ''}</div>`;
    },
  });

  // 12 ---------------------------------------------------------------- Retro board
  T.push({
    id: 'retro', name: 'Retro board', group: 'Visual boards', orient: 'landscape', accent: '#F28C8C',
    blurb: 'Four pastel columns: updates, agreed, worries and actions. Works for retrospectives and reviews.',
    render: (d) => {
      const col = (cls, title, icon, items) => `<div class="rc ${cls}"><h3><span>${icon}</span>${title}</h3>${list(items, (x) => `<div class="ri">${esc(x[0])}${x[1] ? `<small>${esc(x[1])}</small>` : ''}</div>`, 'Nothing yet.')}</div>`;
      return `<header><h1>${esc(d.meta.title || 'Retrospective')}</h1><p>${esc(dateLine(d.meta))}</p></header>
      <div class="rb">
        ${col('c1', 'Updates', '☀', d.notes.map((n) => [n.text, '']))}
        ${col('c2', 'Agreed', '✔', d.decisions.map((x) => [x.text, x.by]))}
        ${col('c3', 'Worries', '⚑', d.risks.map((x) => [x.text, 'Risk']).concat(d.questions.map((x) => [x.text, 'Open question'])))}
        ${col('c4', 'Actions', '➜', d.actions.map((a) => [a.text, [a.owner && first(a.owner), a.due].filter(Boolean).join(' · ') || 'No owner yet']))}
      </div>`;
    },
  });

  const CSS = `
.paper{background:#fff;color:#222;box-sizing:border-box;font-family:"Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif;font-size:13px;line-height:1.5;padding:16mm 15mm;position:relative}
.paper.portrait{width:210mm;min-height:297mm}.paper.landscape{width:297mm;min-height:210mm;padding:12mm 13mm}
.paper *{box-sizing:border-box}.paper h1,.paper h2,.paper h3,.paper h4,.paper p{margin:0}
.paper .muted{color:#8a8a8a}.paper .empty{font-style:italic}
.paper .av{display:inline-flex;align-items:center;justify-content:center;border-radius:50%;color:#fff;font-weight:700;width:22px;height:22px;font-size:9px;flex:none;vertical-align:middle}
.paper .pp{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:700}
.paper .pp.p-high{background:#FBE3EA;color:#A3264F}.paper .pp.p-medium{background:#FCEBD9;color:#9A5410}.paper .pp.p-low{background:#E3F2E6;color:#2E7D45}
.paper table{border-collapse:collapse;width:100%}

/* 1 formal */
.tpl-formal{font-family:Georgia,"Times New Roman",serif;color:#1d2733}
.tpl-formal .hd{display:flex;gap:16px;align-items:center;border-bottom:3px double #1F3A5F;padding-bottom:12px;margin-bottom:14px}
.tpl-formal .mark{background:#1F3A5F;color:#fff;font:700 11px/1 "Segoe UI",Arial,sans-serif;letter-spacing:3px;padding:14px 10px;writing-mode:vertical-rl;transform:rotate(180deg)}
.tpl-formal h1{font-size:26px;color:#1F3A5F;font-weight:700}.tpl-formal .sub{color:#5c6b7a;font-style:italic}
.tpl-formal .meta{margin-bottom:14px;font-size:12.5px}.tpl-formal .meta th{text-align:left;width:90px;color:#1F3A5F;padding:4px 8px;background:#EEF2F7;border:1px solid #D5DDE7}.tpl-formal .meta td{padding:4px 8px;border:1px solid #D5DDE7}
.tpl-formal h2{font-size:15px;color:#1F3A5F;margin:16px 0 6px;display:flex;align-items:center;gap:8px;border-bottom:1px solid #D5DDE7;padding-bottom:3px}
.tpl-formal h2 span{background:#1F3A5F;color:#fff;font:700 11px/20px Arial;width:20px;height:20px;text-align:center;border-radius:2px}
.tpl-formal ul,.tpl-formal ol{margin:4px 0;padding-left:22px}.tpl-formal li{margin:2px 0}
.tpl-formal .dec{display:flex;gap:10px;margin:5px 0}.tpl-formal .dec b{color:#1F3A5F;min-width:26px}.tpl-formal .dec small{display:block;color:#6b7785;font-style:italic}
.tpl-formal .grid th{background:#1F3A5F;color:#fff;text-align:left;padding:5px 8px;font:600 12px "Segoe UI",Arial}.tpl-formal .grid td{border-bottom:1px solid #D5DDE7;padding:5px 8px;vertical-align:top}.tpl-formal .grid tr:nth-child(even) td{background:#F6F8FB}
.tpl-formal .next{margin-top:16px}.tpl-formal .sign{display:flex;gap:40px;margin-top:40px}.tpl-formal .sign div{flex:1;border-top:1px solid #1d2733;padding-top:4px;font-size:11px;color:#5c6b7a}

/* 2 steering */
.tpl-steering{color:#1c2b24}
.tpl-steering .band{background:#1E4D3A;color:#fff;margin:-16mm -15mm 16px;padding:14mm 15mm 10mm;display:flex;justify-content:space-between;align-items:flex-end;gap:20px;border-bottom:5px solid #C9A227}
.tpl-steering .kick{text-transform:uppercase;letter-spacing:2px;font-size:11px;color:#C9A227;font-weight:700}.tpl-steering h1{font-size:24px}.tpl-steering .sub{opacity:.8}
.tpl-steering .rag{border-radius:8px;padding:8px 14px;text-align:center;min-width:120px;background:#fff}.tpl-steering .rag b{display:block;font-size:18px}.tpl-steering .rag span{font-size:11px;color:#555}
.tpl-steering .rag-red b{color:#C0392B}.tpl-steering .rag-amber b{color:#D68910}.tpl-steering .rag-green b{color:#1E8449}
.tpl-steering h3{color:#1E4D3A;font-size:14px;margin:14px 0 6px;text-transform:uppercase;letter-spacing:1px}
.tpl-steering .exec{background:#F3F7F4;border-left:4px solid #C9A227;padding:10px 14px}.tpl-steering .exec h3{margin-top:0}
.tpl-steering .two{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.tpl-steering .tick,.tpl-steering .ask{display:flex;gap:8px;margin:5px 0}.tpl-steering .tick{color:#1E8449}.tpl-steering .tick span,.tpl-steering .ask span{color:#1c2b24}.tpl-steering .ask{color:#C9A227;font-weight:700}
.tpl-steering .grid th{text-align:left;background:#E7EFEA;color:#1E4D3A;padding:6px 8px;font-size:12px}.tpl-steering .grid td{padding:6px 8px;border-bottom:1px solid #DCE5DF;vertical-align:top}
.tpl-steering .sev{background:#FADBD8;color:#A93226;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:700}
.tpl-steering .foot{margin-top:16px;font-size:11px;color:#5a6b62}

/* 3 client */
.tpl-client{font-family:"Segoe UI",system-ui,sans-serif;color:#3b2a26;background:#FFFBF8}
.tpl-client .top{display:flex;align-items:center;gap:8px;color:#D9644A;font-weight:700;text-transform:uppercase;letter-spacing:2px;font-size:11px}.tpl-client .top span{margin-left:auto;color:#9a7f78;letter-spacing:0;text-transform:none;font-weight:400}
.tpl-client .dot{width:12px;height:12px;border-radius:50%;background:#D9644A}
.tpl-client h1{font-size:30px;margin:10px 0 18px;color:#2b1b17;font-family:Georgia,serif}
.tpl-client p{margin:8px 0}.tpl-client .hi{font-size:15px}
.tpl-client .ccard{background:#fff;border:1px solid #F3D5CC;border-radius:12px;padding:14px 16px;margin:12px 0;box-shadow:0 2px 0 #F3D5CC}
.tpl-client h2{font-size:16px;color:#D9644A;margin:18px 0 8px}
.tpl-client .agreed{display:flex;gap:10px;align-items:flex-start;margin:6px 0}.tpl-client .agreed span{background:#D9644A;color:#fff;border-radius:50%;width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center;font-size:11px;flex:none}
.tpl-client .step{display:flex;gap:12px;background:#fff;border:1px solid #F3D5CC;border-radius:10px;padding:10px 12px;margin:6px 0}.tpl-client .step p{margin:0}.tpl-client .num{font:700 18px Georgia,serif;color:#D9644A;min-width:18px}.tpl-client .step small{color:#9a7f78}
.tpl-client .bye{margin-top:22px}

/* 4 workshop */
.tpl-workshop{background:#F4F1EA radial-gradient(#d9d3c4 1px,transparent 1px) 0 0/18px 18px}
.tpl-workshop header{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px;margin-bottom:14px}.tpl-workshop h1{font:800 26px "Segoe UI",Arial;color:#2d2a24}.tpl-workshop header>p{color:#6c665a}
.tpl-workshop .legend{margin-left:auto;display:flex;gap:6px}.tpl-workshop .legend span{padding:2px 8px;font-size:11px;border-radius:3px}
.tpl-workshop .wall{display:grid;grid-template-columns:repeat(5,1fr);gap:16px}
.tpl-workshop .sticky{padding:10px 12px 12px;min-height:110px;box-shadow:2px 4px 8px rgba(0,0,0,.15);font-family:"Comic Sans MS","Segoe Print","Bradley Hand",cursive;font-size:13px}
.tpl-workshop .sticky small{display:block;font:700 9px "Segoe UI",Arial;text-transform:uppercase;letter-spacing:1px;opacity:.6;margin-bottom:4px}.tpl-workshop .sticky em{display:block;margin-top:6px;font-size:11px;opacity:.75}
.tpl-workshop .w-dec{background:#FFE873}.tpl-workshop .w-act{background:#FFB3C7}.tpl-workshop .w-que{background:#A9D8FF}.tpl-workshop .w-risk{background:#FFC58A}.tpl-workshop .w-note{background:#BDF0B5}

/* 5 tracker */
.tpl-tracker header{background:#3A1E4A;color:#fff;margin:-12mm -13mm 14px;padding:10mm 13mm 8mm;border-bottom:5px solid #E0527F}.tpl-tracker h1{font-size:22px}.tpl-tracker header p{opacity:.75}
.tpl-tracker .kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:14px}.tpl-tracker .kpis div{background:var(--c);color:#fff;border-radius:8px;padding:10px 12px}.tpl-tracker .kpis b{font-size:26px;display:block;line-height:1.1}.tpl-tracker .kpis span{font-size:11px;opacity:.9}
.tpl-tracker .split{display:grid;grid-template-columns:1fr 210px;gap:16px}
.tpl-tracker .grid th{background:#F3EDF6;color:#3A1E4A;text-align:left;padding:6px;font-size:11.5px}.tpl-tracker .grid td{padding:6px;border-bottom:1px solid #EEE7F1;vertical-align:top;font-size:12px}
.tpl-tracker tr.done td{color:#aaa;text-decoration:line-through}.tpl-tracker .warn{color:#B9770E;font-weight:600}
.tpl-tracker .st{font-size:11px;padding:1px 8px;border-radius:10px;background:#EEF1FB;color:#5371D1;font-weight:700}.tpl-tracker .st.s-done{background:#E3F2E6;color:#2E7D45}.tpl-tracker .st.s-in-progress{background:#FFF1C9;color:#8A6500}
.tpl-tracker aside h3{font-size:12px;color:#3A1E4A;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px}.tpl-tracker aside h3+p{font-size:12px;color:#555}
.tpl-tracker .obar{display:grid;grid-template-columns:70px 1fr 16px;align-items:center;gap:6px;font-size:11px;margin-bottom:6px}.tpl-tracker .obar span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.tpl-tracker .obar i{height:10px;background:#E0527F;border-radius:5px;display:block}
.tpl-tracker aside h3:nth-of-type(2){margin-top:16px}

/* 6 kanban */
.tpl-kanban{background:#EEF6F6}.tpl-kanban header{display:flex;align-items:baseline;gap:14px;margin-bottom:12px}.tpl-kanban h1{font-size:22px;color:#14595A}.tpl-kanban header p{color:#5d7d7e}
.tpl-kanban .board{display:grid;grid-template-columns:repeat(3,1fr) 0.8fr;gap:12px;align-items:start}
.tpl-kanban .col{background:#DDEDED;border-radius:10px;padding:10px}.tpl-kanban .col h3{font-size:13px;color:#14595A;display:flex;justify-content:space-between;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px}.tpl-kanban .col h3 span{background:#1F8A8A;color:#fff;border-radius:10px;padding:0 8px;font-size:11px}
.tpl-kanban .kcard{background:#fff;border-radius:8px;padding:9px 10px;margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,.1);border-left:4px solid #ccc}.tpl-kanban .kcard.p-high{border-left-color:#E0527F}.tpl-kanban .kcard.p-medium{border-left-color:#E88F30}.tpl-kanban .kcard.p-low{border-left-color:#3F8F4A}
.tpl-kanban .kcard p{font-size:12.5px;margin-bottom:6px}.tpl-kanban .krow{display:flex;align-items:center;gap:6px;font-size:11px;color:#555}.tpl-kanban .krow em{margin-left:auto;background:#EEF6F6;padding:0 6px;border-radius:6px;font-style:normal;color:#14595A}
.tpl-kanban .kside{background:#fff;border:2px dashed #BCD9D9}.tpl-kanban .kside h3:nth-of-type(2){margin-top:12px}.tpl-kanban .mini{font-size:11.5px;padding:5px 0;border-bottom:1px solid #EEF6F6}.tpl-kanban .mini.q:before{content:"? ";color:#1F8A8A;font-weight:700}

/* 7 timeline */
.tpl-timeline header{text-align:center;margin-bottom:18px}.tpl-timeline .kick{color:#4B47B9;letter-spacing:3px;text-transform:uppercase;font-size:11px;font-weight:700}.tpl-timeline h1{font-size:26px;color:#1d1b4f}.tpl-timeline header p{color:#7a78a6}
.tpl-timeline .tl{position:relative;padding-left:130px}.tpl-timeline .tl:before{content:"";position:absolute;left:112px;top:6px;bottom:6px;width:3px;background:linear-gradient(#4B47B9,#B9B7F0);border-radius:2px}
.tpl-timeline .stop{position:relative;margin-bottom:16px}.tpl-timeline .stop:before{content:"";position:absolute;left:-24px;top:6px;width:13px;height:13px;border-radius:50%;background:#fff;border:3px solid #4B47B9}
.tpl-timeline .when{position:absolute;left:-130px;width:96px;text-align:right;font-weight:700;color:#4B47B9;top:3px;font-size:12.5px}
.tpl-timeline .nodate .when{color:#B9770E}.tpl-timeline .nodate:before{border-color:#E88F30}
.tpl-timeline .it{background:#F4F4FD;border-radius:8px;padding:8px 12px;margin-bottom:6px;border-left:4px solid #B9B7F0}.tpl-timeline .it.p-high{border-left-color:#E0527F}.tpl-timeline .it small{color:#666;display:flex;align-items:center;gap:4px;margin-top:3px}
.tpl-timeline .foot{margin-top:18px;background:#1d1b4f;color:#fff;border-radius:8px;padding:10px 14px;font-size:12px}

/* 8 raci */
.tpl-raci header{border-bottom:3px solid #D9822B;padding-bottom:8px;margin-bottom:14px}.tpl-raci h1{font-size:22px;color:#2F3B48}.tpl-raci header p{color:#7b8794}
.tpl-raci .mx th,.tpl-raci .mx td{border:1px solid #E1E5EA;padding:6px;text-align:center;font-size:12px}.tpl-raci .mx .l{text-align:left}.tpl-raci thead th{background:#2F3B48;color:#fff;font-weight:600}
.tpl-raci .pp-h div{display:flex;flex-direction:column;align-items:center;gap:3px}.tpl-raci .pp-h span{font-size:11px}
.tpl-raci .r{display:inline-block;width:24px;height:24px;line-height:24px;border-radius:50%;background:#D9822B;color:#fff;font-weight:800}.tpl-raci .gap{color:#C0392B;font-weight:800}
.tpl-raci .due{color:#666;white-space:nowrap}.tpl-raci tbody tr:nth-child(even) td{background:#F7F9FB}
.tpl-raci tfoot td{background:#FDF3E8;vertical-align:bottom}.tpl-raci .ld{height:42px;display:flex;align-items:flex-end;justify-content:center}.tpl-raci .ld i{width:16px;background:#D9822B;border-radius:3px 3px 0 0;display:block}

/* 9 exec */
.tpl-exec{background:#FBFAF7;color:#111}.tpl-exec .kick{color:#B08D57;text-transform:uppercase;letter-spacing:3px;font-size:11px;font-weight:700}
.tpl-exec h1{font:700 34px/1.15 Georgia,"Times New Roman",serif;margin:10px 0 22px;max-width:90%}
.tpl-exec .nums{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #111;border-bottom:1px solid #111;margin-bottom:22px}.tpl-exec .nums div{padding:14px 0;text-align:center}.tpl-exec .nums div+div{border-left:1px solid #ddd}.tpl-exec .nums b{font:700 40px Georgia,serif;display:block;color:#B08D57}.tpl-exec .nums span{text-transform:uppercase;font-size:11px;letter-spacing:2px}
.tpl-exec .cols{display:grid;grid-template-columns:1.2fr 1fr;gap:26px}.tpl-exec h3{font-size:12px;text-transform:uppercase;letter-spacing:2px;margin:0 0 8px;color:#B08D57}.tpl-exec p{font-size:14px}.tpl-exec ul{padding-left:18px}
.tpl-exec .att div{border-left:3px solid #B08D57;padding:4px 10px;margin-bottom:10px;background:#fff}.tpl-exec .att small{text-transform:uppercase;font-size:10px;letter-spacing:1px;color:#B08D57;font-weight:700}.tpl-exec .att p{font-size:13px}
.tpl-exec .nextb{margin-top:26px;background:#111;color:#fff;padding:12px 16px;display:flex;gap:14px}.tpl-exec .nextb b{color:#B08D57;text-transform:uppercase;letter-spacing:2px;font-size:12px}

/* 10 email */
.tpl-email{font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#202124}
.tpl-email .mailhead{background:#F1F3F4;border-radius:8px;padding:10px 14px;margin-bottom:16px;font-size:13px;color:#3c4043}.tpl-email .mailhead div{margin:2px 0}
.tpl-email .mail p{margin:10px 0}.tpl-email ul{margin:4px 0;padding-left:22px}.tpl-email b{color:#1a3e8a}
.tpl-email .mt{border-collapse:collapse;width:100%;font-size:13px}.tpl-email .mt th{background:#E8F0FE;color:#1a3e8a;border:1px solid #D2DCF0}.tpl-email .mt td{border:1px solid #E3E6EA;vertical-align:top}

/* 11 standup */
.tpl-standup{background:#F6F2FC}.tpl-standup header{margin-bottom:14px}.tpl-standup h1{font-size:22px;color:#4A2C86}.tpl-standup header p{color:#857aa0}
.tpl-standup .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.tpl-standup .pc{background:#fff;border-radius:12px;padding:12px;box-shadow:0 2px 6px rgba(74,44,134,.08);border-top:4px solid #7C4DCC}.tpl-standup .unc{border-top-color:#E88F30;background:#FFFaF2}
.tpl-standup .who{display:flex;gap:10px;align-items:center;margin-bottom:8px}.tpl-standup .who small{display:block;color:#857aa0}
.tpl-standup h4{font-size:10.5px;text-transform:uppercase;letter-spacing:1.5px;color:#7C4DCC;margin:8px 0 4px}
.tpl-standup .do{display:flex;gap:8px;justify-content:space-between;font-size:12px;padding:5px 8px;background:#F6F2FC;border-radius:6px;margin-bottom:4px}.tpl-standup .do em{font-style:normal;color:#7C4DCC;white-space:nowrap;font-weight:600}.tpl-standup .do.p-high{background:#FBE9F0}
.tpl-standup .rq{font-size:12px;color:#555;padding:3px 0}.tpl-standup .rq:before{content:"? ";color:#7C4DCC;font-weight:700}

/* 12 retro */
.tpl-retro header{text-align:center;margin-bottom:14px}.tpl-retro h1{font-size:24px;color:#4a3b3b}.tpl-retro header p{color:#9b8b8b}
.tpl-retro .rb{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.tpl-retro .rc{border-radius:14px;padding:12px;min-height:150mm}
.tpl-retro .c1{background:#FFF4D6}.tpl-retro .c2{background:#DFF5E4}.tpl-retro .c3{background:#FDE2E2}.tpl-retro .c4{background:#E2ECFD}
.tpl-retro h3{font-size:14px;display:flex;align-items:center;gap:8px;margin-bottom:10px;color:#4a3b3b}.tpl-retro h3 span{background:#fff;width:26px;height:26px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center}
.tpl-retro .ri{background:#fff;border-radius:8px;padding:8px 10px;margin-bottom:8px;font-size:12.5px;box-shadow:0 1px 2px rgba(0,0,0,.06)}.tpl-retro .ri small{display:block;color:#888;font-size:11px;margin-top:2px}
`;

  function render(id, d) {
    const t = T.find((x) => x.id === id) || T[0];
    return `<div class="paper ${t.orient} tpl-${t.id}">${t.render(d)}</div>`;
  }

  root.Templates = { list: T, render, CSS, esc };
})(typeof window !== 'undefined' ? window : globalThis);
