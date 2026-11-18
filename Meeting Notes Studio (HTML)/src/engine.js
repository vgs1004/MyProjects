/* Meeting Notes Studio: extraction engine.
 * Turns a transcript or rough notes into actions, decisions, open questions,
 * risks and discussion notes, using plain rules (no AI, nothing leaves the computer).
 * The result is a first draft: every item carries flags so a person can check it.
 */
(function (root) {
  'use strict';

  // ---------------- word lists ----------------
  const WEEKDAYS = 'monday|tuesday|wednesday|thursday|friday|saturday|sunday';
  const MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec';
  const DUE_SRC =
    `(?:(?:by|before|until|on|due|for)\\s+)?` +
    `(today|tonight|tomorrow(?:\\s+(?:morning|afternoon|evening))?|eod|eow|` +
    `end of (?:the )?(?:day|week|month|sprint|quarter)|` +
    `next (?:week|month|sprint|${WEEKDAYS})|this (?:week|${WEEKDAYS})|` +
    `(?:${WEEKDAYS})(?:\\s+(?:morning|afternoon|evening))?|` +
    `(?:${MONTHS})\\.? \\d{1,2}(?:st|nd|rd|th)?|\\d{1,2}(?:st|nd|rd|th)?(?: of)? (?:${MONTHS})\\b\\.?|` +
    `the \\d{1,2}(?:st|nd|rd|th)|\\d{1,2}[./]\\d{1,2}(?:[./]\\d{2,4})?)` +
    `|((?:before|by|until) (?:go-?live|launch|the (?:next )?(?:steering committee|release|demo|workshop|meeting|review)))`;
  const DUE_RE = new RegExp(`\\b${DUE_SRC}\\b`, 'i');

  const LEAD = /^(?:okay|ok|so|well|then|good|great|fine|perfect|yes|yeah|yep|sure|alright|all right|right|actually|also|and|but|now|plus|one more thing|last point|second point|first point|third point|quick update(?: from \w+)?|from (?:the )?\w+ side|from my side|on my side|good question|thanks)\b[,.:!]?\s*/i;
  const FILLER = /\b(?:um+|uh+|erm+|you know|i mean|basically|kind of|sort of|just|really|probably|maybe|actually|honestly|i think|i guess|i feel like)\b,?\s*/gi;
  const STOP = new Set('the a an to of and or for in on at by with from it this that them is are be will can we i you our your my me us please also just new'.split(' '));
  const NOT_NAMES = new Set(['Action', 'Actions', 'Decision', 'Decisions', 'Note', 'Notes', 'Todo', 'To do', 'Risk', 'Risks', 'Question', 'Questions', 'Open question', 'Agenda', 'Date', 'Time', 'Attendees', 'Participants', 'Present', 'Subject', 'Re', 'Topic', 'Next steps', 'Next meeting', 'Location', 'Summary', 'Issue', 'Issues', 'Update', 'Status', 'Blocker', 'Blockers', 'Follow up', 'Follow-up', 'AI', 'FYI', 'NB', 'Info', 'Title', 'Meeting', 'Project', 'Chair', 'Facilitator', 'Minutes', 'Absent', 'Apologies', 'Where', 'When', 'Owner', 'Due']);
  const LABELS = {
    action: /^(?:action(?: item)?s?|todo|to do|ai|next steps?|follow[- ]?up)$/i,
    decision: /^(?:decision|decisions|decided|agreed)$/i,
    question: /^(?:open question|question|questions|q|tbd)$/i,
    risk: /^(?:risk|risks|blocker|blockers|issue|issues|concern)$/i,
    note: /^(?:note|notes|update|status|fyi|info|nb)$/i,
  };
  const HIGH = /\b(client|customer|release|go-?live|launch|blocker|blocking|blocked|urgent|asap|critical|steering|budget|deadline|escalat\w*|outage|legal|contract|security|bug)\b/i;
  const LOW = /\b(nice to have|when you have time|optional|if possible|someday|low priority|no rush)\b/i;
  const ACCEPT = /^(?:yes|yeah|yep|sure|ok|okay|will do|on it|fine|no problem|of course|absolutely|consider it done|i can|i will|i'll|happy to|sounds good|that works|agreed|done)\b/i;
  const UNSURE = /\b(don'?t know|not sure|no idea|park (?:that|this|it)|let'?s park|good question|tbd|to be decided|need to check|let me check|i'?ll check|come back (?:to|on) (?:you|that|this)|unclear|no answer)\b/i;
  const CONFIRM_Q = /\b(fine with that|agree|okay|ok|right|all good|everyone|any objections|does that work|sound good|clear)\?$/i;

  // ---------------- small helpers ----------------
  const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);
  const clean = (s) => s.replace(/\s+/g, ' ').replace(/\s+([,.;:!?])/g, '$1').trim();
  const words = (s) => (s.toLowerCase().match(/[\p{L}\d]+/gu) || []).filter((w) => !STOP.has(w));
  function jaccard(a, b) {
    const A = new Set(words(a)), B = new Set(words(b));
    if (!A.size || !B.size) return 0;
    let n = 0;
    A.forEach((w) => { if (B.has(w)) n++; });
    return n / (A.size + B.size - n);
  }
  let _id = 0;
  const newId = () => 'i' + Date.now().toString(36) + (++_id).toString(36);

  function stripLead(s) {
    let prev;
    do { prev = s; s = s.replace(LEAD, ''); } while (s !== prev);
    return s;
  }
  function tidyDue(d) {
    if (!d) return '';
    d = d.replace(/^(?:on|due|for)\s+/i, '').trim();
    if (/^eod$/i.test(d)) d = 'End of day';
    if (/^eow$/i.test(d)) d = 'End of week';
    return cap(d.replace(/^(by|until)\s+/i, (m) => m.toLowerCase()));
  }
  function findDue(s) {
    const m = s.match(DUE_RE);
    if (!m) return { due: '', rest: s };
    const rest = s.slice(0, m.index) + s.slice(m.index + m[0].length);
    return { due: m[2] ? cap(m[2]) : tidyDue(m[1]), rest };
  }

  // ---------------- 1. read the transcript ----------------
  const NAME = "[A-ZÄÖÜÉ][\\p{L}'’.-]*(?:\\s(?:van|von|de|da|del|der|di|le)?\\s?[A-ZÄÖÜÉ][\\p{L}'’.-]*){0,2}";
  const SPEAKER_RE = new RegExp(`^(?:\\[?\\(?\\d{1,2}:\\d{2}(?::\\d{2})?(?:\\.\\d+)?\\)?\\]?\\s*[-–]?\\s*)?(${NAME})\\s*(?:\\(\\d{1,2}:\\d{2}(?::\\d{2})?\\))?\\s*:\\s*(.+)$`, 'u');
  const TEAMS_HEAD_RE = new RegExp(`^(${NAME})\\s+(?:\\d{1,2}:)?\\d{1,2}:\\d{2}\\s*$`, 'u');
  const TIME_ONLY = /^\[?\(?\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d+)?\)?\]?$/;

  function fromVtt(text) {
    const out = [];
    text.split(/\n\s*\n/).forEach((block) => {
      block.split('\n').forEach((line) => {
        line = line.trim();
        if (!line || /^WEBVTT/.test(line) || /-->/.test(line) || /^\d+$/.test(line) || /^NOTE\b/.test(line) || /^[0-9a-f-]{20,}(\/\d+-\d+)?$/i.test(line)) return;
        const v = line.match(/^<v\s+([^>]+)>(.*?)(?:<\/v>)?$/);
        if (v) out.push(`${v[1].trim()}: ${v[2].replace(/<[^>]+>/g, '')}`);
        else out.push(line.replace(/<[^>]+>/g, ''));
      });
    });
    return out.join('\n');
  }

  function parse(raw) {
    let text = (raw || '').replace(/\r/g, '').replace(/ /g, ' ');
    if (/^﻿?WEBVTT/.test(text.trim())) text = fromVtt(text);
    const meta = { title: '', date: '', attendees: [], agenda: [], nextMeeting: '', location: '' };
    const utts = [];
    let pending = null, sawSpeaker = false;
    const push = (speaker, t, label) => {
      t = t.trim();
      if (!t) return;
      const last = utts[utts.length - 1];
      if (last && speaker && last.speaker === speaker && !label && !last.label) last.text += ' ' + t;
      else utts.push({ speaker: speaker || '', text: t, label: label || '' });
    };
    text.split('\n').forEach((line0) => {
      let line = line0.trim();
      if (!line || TIME_ONLY.test(line)) return;
      line = line.replace(/^(?:[-*•–·▪◦]|\d+[.)])\s+/, '');
      const lb = line.match(/^([A-Za-z][A-Za-z -]{0,20}?)\s*:\s*(.+)$/);
      if (lb) {
        const lab = Object.keys(LABELS).find((k) => LABELS[k].test(lb[1].trim()));
        if (lab) { push(pending || '', lb[2], lab); return; }
      }
      const th = line.match(TEAMS_HEAD_RE);
      if (th && !NOT_NAMES.has(th[1])) { pending = th[1]; sawSpeaker = true; return; }
      const m = line.match(SPEAKER_RE);
      if (m) {
        const who = m[1].trim(), body = m[2].trim();
        const lab = Object.keys(LABELS).find((k) => LABELS[k].test(who));
        if (lab) { push(pending || '', body, lab); return; }
        if (/^(attendees|participants|present)$/i.test(who)) { meta.attendees = body.split(/\s*[,;]\s*|\s+and\s+/).map((s) => s.trim()).filter(Boolean); return; }
        if (/^date$/i.test(who)) { meta.date = body; return; }
        if (/^(location|where)$/i.test(who)) { meta.location = body; return; }
        if (/^(title|subject|meeting|topic)$/i.test(who)) { meta.title = body; return; }
        if (/^agenda$/i.test(who)) { meta.agenda = body.split(/\s*[,;]\s*/).filter(Boolean).map(cap); return; }
        if (/^next meeting$/i.test(who)) { meta.nextMeeting = body; return; }
        if (!NOT_NAMES.has(who) && who.split(' ').length <= 3) {
          sawSpeaker = true; pending = null; push(who, body); return;
        }
      }
      if (pending) { push(pending, line); return; }
      if (!sawSpeaker && !utts.length && !meta.title && line.length < 90 && !/[.?!]$/.test(line)) { meta.title = line; return; }
      if (!sawSpeaker && /^(invented|example|transcript|recorded|this is a)/i.test(line)) return;
      push('', line);
    });
    return { meta, utts };
  }

  // ---------------- 2. people ----------------
  function people(utts, meta) {
    const full = [];
    utts.forEach((u) => { if (u.speaker && !full.includes(u.speaker)) full.push(u.speaker); });
    meta.attendees.forEach((a) => {
      const k = full.findIndex((f) => f.split(' ')[0] === a.split(' ')[0]);
      if (k < 0) full.push(a);
      else if (a.length > full[k].length) full[k] = a;
    });
    const byFirst = {};
    full.forEach((f) => { byFirst[f.split(' ')[0].toLowerCase()] = f; byFirst[f.toLowerCase()] = f; });
    const lookup = (name) => byFirst[(name || '').toLowerCase()] || byFirst[(name || '').split(' ')[0].toLowerCase()] || '';
    const namesRe = full.length
      ? new RegExp(`\\b(${full.flatMap((f) => [f, f.split(' ')[0]]).sort((a, b) => b.length - a.length).map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`, 'g')
      : null;
    return { list: full, lookup, namesRe };
  }

  // ---------------- 3. rewording ----------------
  function tidyTask(s, speakerFirst) {
    let t = ' ' + s + ' ';
    t = t.replace(FILLER, ' ');
    t = stripLead(clean(t));
    t = t.replace(/^(?:I'?ll|I will|I can|I could|I'm going to|I am going to|I'm gonna|let me|we'?ll|we will|we can|we could|I'll take care of|I'll handle|can you|could you|would you|will you|please)\s+/i, '');
    t = t.replace(/^(?:please|go ahead and|make sure to|make sure you|try to)\s+/i, '');
    t = t.replace(/\byourself\b\s*/gi, '').replace(/,?\s*(?:you know[^,.]*|if that'?s ok(?:ay)?|if you can|if possible|thanks|please)\s*[.?!]?$/i, '');
    t = t.replace(/,?\s+(?:before|so that|because|since|as|otherwise|in case)\s+(?:they|we|he|she|you|I|the client|the customer)\b.*$/i, '');
    t = t.replace(/,?\s+but\s+.*$/i, '');
    if (speakerFirst) t = t.replace(/\bme\b/g, speakerFirst).replace(/\bmy\b/g, speakerFirst + "'s");
    t = clean(t).replace(/[.?!,;:]+$/, '');
    return cap(t);
  }
  function tidySentence(s) {
    let t = stripLead(clean((' ' + s + ' ').replace(FILLER, ' ')));
    t = clean(t);
    if (t && !/[.?!]$/.test(t)) t += '.';
    return cap(t);
  }
  const PRONOUN = /\b(it|this|that|them|those)\b/i;
  function needsRef(t) {
    const m = t.match(PRONOUN);
    if (!m) return false;
    const before = t.slice(0, m.index);
    return !/\b(the|a|an|our|their|his|her)\s+[\p{L}-]+/iu.test(before);
  }
  // find what "it" means by looking back for "<verb> the <thing>" or a bare topic like "the budget for X."
  function antecedent(sentences, upto) {
    for (let i = upto - 1; i >= Math.max(0, upto - 8); i--) {
      const s = stripLead(sentences[i].text.replace(/[.?!]+$/, ''));
      if (/^(?:the|a|an|our)\s+[\p{L}-]+(?:\s+[\p{L}\d-]+){0,7}$/iu.test(s) && !/\b(is|are|was|were|will|can|need|needs|has|have)\b/i.test(s)) return s.toLowerCase();
      const vo = s.match(/\b(?:draft|send|write|prepare|update|share|review|fix|check|call|email|book|order|create|finish|test|deploy|record|schedule|plan|tell|inform|approve|sign)\s+((?:the|a|an|this|our)\s+[\p{L}\d-]+(?:\s+(?:plan|page|email|report|issue|bug|deck|slides|invite|contract|list|build|date|budget|video|notes|minutes|doc|document))?)/iu);
      if (vo) return vo[1].toLowerCase().replace(/^(this|a|an)\s/, 'the ');
    }
    return '';
  }

  // ---------------- 4. classify ----------------
  function extract(raw) {
    const { meta, utts } = parse(raw);
    const ppl = people(utts, meta);
    if (!meta.attendees.length) meta.attendees = ppl.list.slice();
    const sentences = [];
    utts.forEach((u, ui) => {
      const parts = u.text.match(/[^.!?]+(?:[.!?]+|$)/g) || [u.text];
      parts.forEach((p) => { if (p.trim()) sentences.push({ text: p.trim(), speaker: u.speaker, ui, label: u.label }); });
    });
    const items = [];
    const add = (o) => {
      const it = Object.assign({ id: newId(), type: 'note', text: '', owner: '', due: '', priority: 'Medium', status: 'Open', source: '', speaker: '', flags: [], checked: false, by: '', si: -1, ui: -1 }, o);
      items.push(it);
      return it;
    };
    const firstOf = (n) => (n || '').split(' ')[0];
    const nextUtt = (ui) => utts[ui + 1];

    // agenda and next meeting from the conversation
    sentences.forEach((s) => {
      const ag = s.text.match(/\b(?:agenda|topics?|(?:two|three|four|five|six|\d) (?:things|points|topics|items))(?: for)?(?: today)?\s*:\s*(.+)$/i);
      if (ag && !meta.agenda.length) meta.agenda = ag[1].replace(/[.?!]+$/, '').split(/,\s*(?:and\s+)?|\s+and\s+/).map((x) => cap(x.replace(/^the\s+/i, '').trim())).filter(Boolean);
      const nm = s.text.match(/\b(same time next week|next meeting(?: is| on)? [^.?!]+)/i);
      if (nm) meta.nextMeeting = cap(nm[1]);
    });

    sentences.forEach((s, si) => {
      const raw0 = s.text;
      let t = stripLead(raw0);
      const speakerFull = ppl.lookup(s.speaker) || s.speaker;
      const base = { source: raw0, speaker: speakerFull, si, ui: s.ui };

      // "Actually no" cancels what the same person said just before
      if (/^(?:actually,? no|no,? wait|scratch that|on second thought|forget that|correction)\b/i.test(raw0.replace(/^(?:okay|ok|hmm|so),?\s*/i, ''))) {
        for (let k = items.length - 1; k >= 0; k--) {
          const it = items[k];
          if (it.ui === s.ui && it.si === si - 1) items.splice(k, 1);
        }
        t = t.replace(/^(?:no,?\s*|wait,?\s*)/i, '');
      }

      // labelled lines in notes: "Action: ...", "Decision: ..."
      if (s.label) {
        if (s.label === 'action') return actionFrom(t, base, null);
        if (s.label === 'decision') return add(Object.assign({}, base, { type: 'decision', text: tidySentence(t).replace(/\.$/, ''), by: speakerFull }));
        if (s.label === 'question') return add(Object.assign({}, base, { type: 'question', text: tidySentence(t).replace(/\.$/, '?').replace(/\?\?$/, '?'), by: speakerFull }));
        if (s.label === 'risk') return add(Object.assign({}, base, { type: 'risk', text: tidySentence(t).replace(/\.$/, ''), priority: 'High' }));
        return add(Object.assign({}, base, { type: 'note', text: tidySentence(t) }));
      }

      // decisions
      const dec = t.match(/\b(?:let'?s agree|we(?:'ve| have)? agreed|we(?:'ve| have)? decided|decision(?: is)?|it'?s decided|let'?s go with|we'?ll go with|we go with)\b\s*(?:that|to|on)?\s*[:,]?\s*(.*)$/i)
        || t.match(/^(.*\b(?:approved|signed off|confirmed)\b.*)$/i);
      if (dec) {
        const body = (dec[1] || '').replace(/[.?!]+$/, '');
        if (words(body).length >= 2) {
          let txt = body.replace(/^we\s+(?=\w)/i, '');
          const yes = [speakerFull];
          for (let k = 1; k <= 3 && utts[s.ui + k]; k++) {
            const u = utts[s.ui + k];
            if (u.speaker && ACCEPT.test(u.text) && !yes.includes(ppl.lookup(u.speaker) || u.speaker)) yes.push(ppl.lookup(u.speaker) || u.speaker);
          }
          add(Object.assign({}, base, { type: 'decision', text: cap(clean(txt)), by: yes.filter(Boolean).join(', ') }));
          return;
        }
        if (/^(?:good,?\s*)?decided[.!]?$/i.test(t)) return;
      }

      // risks
      if (/^(?:that'?s|this is|it'?s|there'?s)\s+(?:a|an)\s+(?:big |real |serious |potential )?(?:risk|concern|blocker)\b/i.test(t)) {
        const prev = sentences[si - 1];
        const what = prev && prev.ui === s.ui ? stripLead(prev.text.replace(/[.?!]+$/, '')) : t;
        add(Object.assign({}, base, { type: 'risk', text: cap(clean(what.replace(/^the\s+/i, 'The '))), priority: 'High' }));
        const rest = t.replace(/^[^,]*,\s*/, '');
        if (rest !== t && /\b(I'?ll|I will|we'?ll)\b/i.test(rest)) actionFrom(rest.replace(/^.*?\b(?:I'?ll|I will|we'?ll)\s+/i, ''), base, speakerFull);
        return;
      }
      if (/\b(risk|blocker|concern|might delay|could delay|at risk)\b/i.test(t) && !/\?$/.test(t)) {
        add(Object.assign({}, base, { type: 'risk', text: tidySentence(t).replace(/\.$/, ''), priority: 'High' }));
        return;
      }

      // requests: "Tom, can you ...?"  "Markus, just send it ..."
      const nameStart = t.match(new RegExp(`^(${ppl.namesRe ? ppl.namesRe.source.slice(3, -3) : '(?!x)x'}),\\s*(.+)$`));
      const canYou = t.match(/\b(?:can|could|would|will) you\s+(?:please\s+)?(.+?)\??$/i);
      if (nameStart || canYou) {
        let owner = '', body = '';
        if (nameStart) {
          owner = ppl.lookup(nameStart[1]);
          body = nameStart[2];
          const cy = body.match(/^(?:(?:can|could|would|will) you\s+)?(?:please\s+|just\s+)*(.+)$/i);
          body = cy ? cy[1] : body;
        } else if (canYou) {
          body = canYou[1];
          const tail = t.match(new RegExp(`,\\s*(${ppl.namesRe ? ppl.namesRe.source.slice(3, -3) : '(?!x)x'})\\s*\\??$`));
          if (tail) owner = ppl.lookup(tail[1]);
        }
        if (body && /^(?:[a-z]+)\b/i.test(body) && !/^(?:you|we|i|is|are|do|does|did|have|has|what|when|where|who|why|how)\b/i.test(body)) {
          const reply = nextUtt(s.ui);
          if (!owner && reply && reply.speaker && reply.speaker !== s.speaker && ACCEPT.test(reply.text)) owner = ppl.lookup(reply.speaker) || reply.speaker;
          const it = actionFrom(body, base, owner);
          if (it && owner && !(reply && (ppl.lookup(reply.speaker) === owner) && ACCEPT.test(reply.text))) {
            it.flags.push({ level: 'warn', text: `${firstOf(owner)} didn't clearly say yes` });
          }
          return;
        }
      }

      // commitments: "I'll ...", "I can ...", "we can ... by Friday", "Ben to update ...", "Chloe will check ..."
      const named = t.match(new RegExp(`^(${ppl.namesRe ? ppl.namesRe.source.slice(3, -3) : '(?!x)x'})\\s+(?:to|will|is going to|should)\\s+(.+)$`));
      if (named) return actionFrom(named[2], base, ppl.lookup(named[1]));
      const iWill = t.match(/\b(?:I'?ll|I will|I can|I'm going to|I am going to|let me|I'll take care of|I'll handle|we'?ll|we will|we can)\s+(?!be\b|have\b|need\b|see\b|know\b|talk\b|get there\b|try\b|probably\b|think\b|lose\b|miss\b)(.+)$/i);
      if (iWill) {
        let cond = '';
        const ifm = t.match(/^if\s+(.+?),\s*(.+)$/i);
        if (ifm) cond = ifm[1];
        const owner = speakerFull;
        const it = actionFrom(iWill[1], base, owner);
        if (it && cond) it.flags.push({ level: 'warn', text: `Depends on: ${cond}` });
        const but = t.match(/,?\s+but\s+(.+)$/i);
        if (it && but) it.flags.push({ level: 'warn', text: `Caveat: ${but[1].replace(/[.?!]+$/, '')}` });
        if (it && /\bwe\b/i.test(iWill[0].slice(0, 6))) it.flags.push({ level: 'info', text: `Said as "we": confirm ${firstOf(owner) || 'who'} is the owner` });
        return;
      }
      const vague = t.match(/\b(?:someone|somebody|we|you)\s+(?:needs? to|should|must|have to|has to|ought to)\s+(.+)$/i);
      if (vague && !/\?$/.test(t)) {
        const it = actionFrom(vague[1], base, '');
        if (it) {
          // did someone volunteer in the next two turns?
          for (let k = 1; k <= 2 && s.speaker; k++) {
            const u = utts[s.ui + k];
            const head = u ? stripLead(u.text.replace(FILLER, '')) : '';
            if (u && u.speaker && u.speaker !== s.speaker && /^(?:I'?ll|I can|I will|I could)\b/i.test(head) && !/^(?:I'?ll|I can|I will|I could) (?:check|see|think|try)\b/i.test(head)) {
              it.owner = ppl.lookup(u.speaker) || u.speaker;
              it.flags = it.flags.filter((f) => !/No owner/.test(f.text));
              it.flags.push({ level: 'info', text: `${firstOf(it.owner)} volunteered` });
              break;
            }
          }
        }
        return;
      }

      // open questions
      if (/\?$/.test(t) && !CONFIRM_Q.test(t) && !/^(?:so|right|okay)\b/i.test(raw0)) {
        const reply = nextUtt(s.ui);
        const inSameUtt = sentences.slice(si + 1).filter((x) => x.ui === s.ui).map((x) => x.text).join(' ');
        if ((reply && reply.speaker !== s.speaker && UNSURE.test(reply.text)) || UNSURE.test(inSameUtt) || !reply) {
          add(Object.assign({}, base, { type: 'question', text: tidySentence(t).replace(/[.]$/, '?'), by: speakerFull }));
          return;
        }
      }

      // discussion notes: status updates worth keeping
      if (!/\?$/.test(t) && words(t).length >= 4 && /\b(is|are|was|were|has|have|had|need|needs|will|can|got|did|\w+ed)\b/i.test(t) && /\b(fixed|done|finished|completed|ready|still open|open issue|delayed|late|behind|on track|blocked|released|launched|live|need(?:s)? (?:a|an|two|three|more|\d)|more (?:days|weeks|time)|not realistic|budget|over|under|increase|decrease|feedback|approved|waiting|pending)\b/i.test(t)) {
        add(Object.assign({}, base, { type: 'note', text: tidySentence(t) }));
      }
    });

    function actionFrom(body, base, owner) {
      let src = body.replace(/^if\s+.+?,\s*/i, '').replace(/,?\s+but\s+.*$/i, '');
      const { due, rest } = findDue(src);
      let text = tidyTask(rest, firstOf(base.speaker));
      if (!text || words(text).length < 1) return null;
      const flags = [];
      if (needsRef(text)) {
        const ref = antecedent(sentences, base.si + 1 > 0 ? base.si : 0);
        if (ref) {
          const before = text;
          text = text.replace(PRONOUN, ref);
          flags.push({ level: 'info', text: `Read "${before.match(PRONOUN) ? before.match(PRONOUN)[0] : 'it'}" as "${ref}"` });
        } else flags.push({ level: 'warn', text: `Unclear "${text.match(PRONOUN)[0]}": say what it is` });
      }
      const all = base.source + ' ' + body;
      const priority = LOW.test(all) ? 'Low' : HIGH.test(all) ? 'High' : /\b(probably|maybe|could)\b/i.test(base.source) ? 'Low' : 'Medium';
      return add(Object.assign({}, base, { type: 'action', text: cap(text), owner: owner || '', due, priority, flags }));
    }

    // merge repeated actions: same owner, similar wording (later one wins, keeps the most specific deadline)
    const acts = items.filter((i) => i.type === 'action');
    for (let a = 0; a < acts.length; a++) {
      for (let b = a + 1; b < acts.length; b++) {
        const A = acts[a], B = acts[b];
        if (!items.includes(A) || !items.includes(B)) continue;
        if (A.owner && A.owner === B.owner && jaccard(A.text, B.text) >= 0.6) {
          B.due = B.due || A.due;
          B.flags = B.flags.filter((f) => !/didn't clearly say yes/.test(f.text));
          B.flags.push({ level: 'info', text: 'Mentioned twice, merged' });
          B.source = A.source + ' … ' + B.source;
          items.splice(items.indexOf(A), 1);
        }
      }
    }
    // remaining look-alikes for the same person close together
    const acts2 = items.filter((i) => i.type === 'action');
    acts2.forEach((A, a) => acts2.slice(a + 1).forEach((B) => {
      if (A.owner && A.owner === B.owner && Math.abs(A.ui - B.ui) <= 4 && jaccard(A.text, B.text) >= 0.2) {
        [A, B].forEach((x) => x.flags.push({ level: 'warn', text: 'Similar to another action: merge or delete' }));
      }
    }));
    // final flags
    items.forEach((it) => {
      if (it.type === 'action') {
        if (!it.owner) it.flags.unshift({ level: 'warn', text: 'No owner: nobody took this' });
        if (!it.due) it.flags.push({ level: 'warn', text: 'No deadline' });
      }
      if (it.type === 'question' && !it.by) it.by = '';
      delete it.si;
    });

    // de-duplicate decisions and notes
    const seen = [];
    for (let k = items.length - 1; k >= 0; k--) {
      const it = items[k];
      if (it.type === 'action') continue;
      if (seen.some((x) => x.type === it.type && jaccard(x.text, it.text) > 0.7)) items.splice(k, 1);
      else seen.push(it);
    }

    const summary = makeSummary(meta, items, ppl.list);
    return { meta, items, summary, people: ppl.list };
  }

  function makeSummary(meta, items, ppl) {
    const n = (t) => items.filter((i) => i.type === t).length;
    const acts = items.filter((i) => i.type === 'action');
    const noOwner = acts.filter((a) => !a.owner).length;
    const dec = items.find((i) => i.type === 'decision');
    const parts = [];
    const who = ppl.length ? ` with ${ppl.length > 4 ? ppl.length + ' people' : listJoin(ppl.map((p) => p.split(' ')[0]))}` : '';
    parts.push(`${meta.title ? meta.title.replace(/[.:]+$/, '') : 'Meeting'}${who}.`);
    if (meta.agenda.length) parts.push(`Topics: ${listJoin(meta.agenda.map((a) => a.toLowerCase()))}.`);
    if (dec) parts.push(`Main decision: ${dec.text.charAt(0).toLowerCase() + dec.text.slice(1).replace(/\.$/, '')}.`);
    parts.push(`${acts.length} action${acts.length === 1 ? '' : 's'} agreed${noOwner ? `, ${noOwner} still without an owner` : ''}; ${n('question')} open question${n('question') === 1 ? '' : 's'}${n('risk') ? ` and ${n('risk')} risk${n('risk') === 1 ? '' : 's'} raised` : ''}.`);
    return parts.join(' ');
  }
  function listJoin(a) {
    if (a.length <= 1) return a.join('');
    return a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1];
  }

  // Parse an answer pasted back from an approved AI (JSON in the documented shape).
  function fromAiJson(text) {
    const m = text.match(/\{[\s\S]*\}/);
    if (!m) throw new Error('No JSON found in the pasted answer.');
    const j = JSON.parse(m[0]);
    const items = [];
    const mk = (type, o, map) => items.push(Object.assign({ id: newId(), type, owner: '', due: '', priority: 'Medium', status: 'Open', source: '', speaker: '', flags: [{ level: 'info', text: 'From your approved AI: check it' }], checked: false, by: '' }, map(o)));
    (j.action_items || j.actions || []).forEach((o) => mk('action', o, (x) => ({ text: x.task || x.text || '', owner: x.owner || '', due: x.due || '', priority: x.priority || 'Medium', source: x.quote || x.source_quote || '' })));
    (j.decisions || []).forEach((o) => mk('decision', o, (x) => ({ text: x.decision || x.text || '', by: x.decided_by || '', source: x.quote || x.source_quote || '' })));
    (j.open_questions || j.questions || []).forEach((o) => mk('question', o, (x) => ({ text: x.question || x.text || '', by: x.raised_by || '' })));
    (j.risks || []).forEach((o) => mk('risk', o, (x) => ({ text: x.risk || x.text || '', priority: 'High' })));
    (j.notes || j.discussion || []).forEach((o) => mk('note', o, (x) => ({ text: typeof x === 'string' ? x : x.note || x.text || '' })));
    items.forEach((i) => { if (i.type === 'action') { if (!i.owner) i.flags.push({ level: 'warn', text: 'No owner' }); if (!i.due) i.flags.push({ level: 'warn', text: 'No deadline' }); } });
    return { items, summary: j.summary || '' };
  }

  const AI_PROMPT = `You are taking minutes for a business meeting. Read the transcript below and answer ONLY with JSON in exactly this shape:
{
  "summary": "2-3 sentences: what the meeting was about and where it ended",
  "decisions": [{"decision": "", "decided_by": "", "quote": ""}],
  "action_items": [{"task": "short instruction starting with a verb", "owner": "", "due": "as said, e.g. Friday", "priority": "High|Medium|Low", "quote": ""}],
  "open_questions": [{"question": "", "raised_by": ""}],
  "risks": [{"risk": ""}],
  "notes": ["key status updates, one sentence each"]
}
Rules: use only what is in the transcript; never invent names, dates or tasks. If nobody clearly took a task, leave owner empty. If a task was handed to someone else, the owner is the final person. "quote" is 5-15 words copied word for word from the transcript. Write in clear, professional English.

Transcript:
`;

  const api = { extract, parse, tidyTask, tidySentence, fromAiJson, makeSummary, AI_PROMPT, newId };
  root.Engine = api;
  if (typeof module !== 'undefined') module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
