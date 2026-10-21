// In-page extraction for the ProSites "litesite" template. Evaluated in the page's main world.
// Returns a JSON-serialisable object describing head, hero, nav, main content blocks, plugins,
// every link / image / CSS background / media element / form control, plus style samples.
(() => {
  const out = { errors: [] };
  const SVGNS = 'http://www.w3.org/2000/svg';
  const abs = (u) => { if (u == null || u === '') return null; try { return new URL(u, document.baseURI).href; } catch (e) { return u; } };
  const norm = (s) => (s || '').replace(/[\s ]+/g, ' ').trim();
  const rendered = (el) => { try { return el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden'; } catch (e) { return false; } };
  const sel = (el) => {
    if (!el || el.nodeType !== 1) return '';
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const c = typeof el.className === 'string' ? el.className.trim() : '';
    if (c) s += '.' + c.split(/\s+/).slice(0, 3).join('.');
    return s;
  };
  const pathOf = (el) => { const p = []; for (let e = el; e && e.nodeType === 1 && e !== document.documentElement && p.length < 7; e = e.parentElement) p.unshift(sel(e)); return p.join(' > '); };
  const areaOf = (el) => {
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const id = e.id || '';
      const cl = e.classList;
      if (id === 'ADAButton' || (e.tagName === 'A' && /\/ada\.aspx/i.test(e.getAttribute('href') || ''))) return 'ada-widget';
      if (e.tagName === 'SECTION') {
        if (id === 'content') return 'main';
        if (id === 'form') return 'plugin-contact';
        if (id === 'testiomnials' || cl.contains('testimonials-plugin')) return 'plugin-testimonials';
        if (id === 'address') return 'plugin-address';
        if (id === 'footer') return 'footer';
        return 'section-' + (id || (typeof e.className === 'string' ? e.className.trim().split(/\s+/)[0] : 'unknown'));
      }
      if (id === 'main-menu') return 'nav';
      if (id === 'myCarousel') return 'hero-carousel';
      if (cl && cl.contains('banner')) return 'hero-banner';
      if (cl && cl.contains('menu-icons')) return 'header-icons';
      if (e.tagName === 'HEADER') return 'header';
      if (cl && cl.contains('phone') && e.parentElement && e.parentElement.id === 'aspnetForm') return 'phonebar';
      if (cl && cl.contains('scroll-top-wrapper')) return 'chrome';
    }
    return 'other';
  };
  const hex = (c) => {
    const m = c && c.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
    if (!m) return c;
    const a = m[4] === undefined ? 1 : parseFloat(m[4]);
    const h = '#' + [m[1], m[2], m[3]].map((x) => Math.round(+x).toString(16).padStart(2, '0')).join('').toUpperCase();
    return a < 1 ? h + ' (alpha ' + a + ')' : h;
  };

  // ---------- validators / controls ----------
  let validatorEls = new Set();
  try {
    const pv = window.Page_Validators || [];
    validatorEls = new Set(pv);
    out.validators = pv.map((v) => ({
      id: v.id, controltovalidate: v.controltovalidate || null, errormessage: v.errormessage || norm(v.textContent),
      evaluationfunction: v.evaluationfunction || null, initialvalue: v.initialvalue, validationexpression: v.validationexpression,
      clientvalidationfunction: v.clientvalidationfunction, validationGroup: v.validationGroup, area: areaOf(v),
    }));
  } catch (e) { out.errors.push('validators: ' + e.message); out.validators = []; }
  // validators hooked to extra controls via ValidatorHookupControlID (e.g. "Email or Phone Required")
  const hookups = {};
  try {
    for (const s of document.querySelectorAll('script')) {
      const t = s.textContent || '';
      for (const m of t.matchAll(/ValidatorHookupControlID\("([^"]+)",\s*document\.all\["([^"]+)"\]\)/g)) {
        (hookups[m[1]] = hookups[m[1]] || []).push(m[2]);
      }
    }
  } catch (e) { out.errors.push('hookups: ' + e.message); }

  const isControl = (el) => {
    const t = el.tagName;
    if (t === 'SELECT' || t === 'TEXTAREA' || t === 'BUTTON') return true;
    if (t === 'INPUT') return (el.getAttribute('type') || 'text').toLowerCase() !== 'hidden';
    return false;
  };
  const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'LINK', 'META']);
  const skipEl = (el) => SKIP.has(el.tagName) || validatorEls.has(el) ||
    (el.tagName === 'INPUT' && (el.getAttribute('type') || '').toLowerCase() === 'hidden') ||
    (el.classList && el.classList.contains('cloned')) || el.id === 'phspan' || el.id === 'fs';

  let lastPrevBold = false;
  function precedingText(c) {
    const root = c.closest('table, fieldset, form, section') || document.body;
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    let last = [];
    let lastNode = null;
    let n;
    while ((n = tw.nextNode())) {
      if (n === c) break;
      if (n.nodeType === 1 && isControl(n)) { last = []; lastNode = null; continue; }
      if (n.nodeType === 3) {
        const p = n.parentElement;
        if (!p || SKIP.has(p.tagName) || validatorEls.has(p) || p.closest('script,style')) continue;
        if (validatorEls.has(p.closest('span'))) continue;
        const t = norm(n.nodeValue);
        if (t) { last.push(t); lastNode = n; }
      }
    }
    lastPrevBold = false;
    if (lastNode) { try { const w = getComputedStyle(lastNode.parentElement).fontWeight; lastPrevBold = parseInt(w, 10) >= 600 || w === 'bold'; } catch (e) {} }
    return last.slice(-3).join(' ');
  }
  function nextText(c) {
    let s = c.nextSibling, t = '';
    while (s && !t) {
      if (s.nodeType === 3) t = norm(s.nodeValue);
      else if (s.nodeType === 1) { if (isControl(s)) break; t = norm(s.innerText || s.textContent); }
      s = s.nextSibling;
    }
    return t;
  }
  const allControls = [...document.querySelectorAll('input, select, textarea, button')].filter(isControl);
  function fieldInfo(c, i) {
    const tag = c.tagName.toLowerCase();
    const type = (c.getAttribute('type') || (tag === 'input' ? 'text' : tag)).toLowerCase();
    const id = c.id || '';
    let labelFor = '';
    try { if (id) labelFor = [...document.querySelectorAll('label[for="' + CSS.escape(id) + '"]')].map((l) => norm(l.innerText || l.textContent)).join(' | '); } catch (e) {}
    const wrap = c.closest('label');
    const cell = c.closest('td');
    const vals = (out.validators || []).filter((v) => v.controltovalidate === id || (hookups[id] || []).includes(v.id));
    const f = {
      i, area: areaOf(c), tag, type, id, name: c.getAttribute('name') || '',
      labelFor: labelFor || undefined,
      wrapLabel: wrap ? norm(wrap.innerText || wrap.textContent) : undefined,
      placeholder: c.getAttribute('placeholder') || undefined,
      ariaLabel: c.getAttribute('aria-label') || undefined,
      title: c.getAttribute('title') || undefined,
      prevText: precedingText(c) || undefined,
      prevTextBold: lastPrevBold || undefined,
      rowLabel: cell && cell.previousElementSibling ? norm(cell.previousElementSibling.innerText || cell.previousElementSibling.textContent) || undefined : undefined,
      htmlRequired: c.required || c.getAttribute('aria-required') === 'true' || undefined,
      validators: vals.length ? vals.map((v) => ({ id: v.id, fn: v.evaluationfunction, message: v.errormessage, expr: v.validationexpression || undefined, clientfn: v.clientvalidationfunction || undefined })) : undefined,
      visible: rendered(c),
      value: (type === 'submit' || type === 'button' || type === 'reset' || tag === 'button') ? (c.value || norm(c.innerText)) : undefined,
      checked: (type === 'radio' || type === 'checkbox') ? c.checked : undefined,
      optionLabel: (type === 'radio' || type === 'checkbox') ? (labelFor || nextText(c)) : undefined,
      maxlength: c.maxLength > 0 ? c.maxLength : undefined,
      rows: tag === 'textarea' ? c.rows : undefined,
      cls: (typeof c.className === 'string' && c.className) || undefined,
      onclick: c.getAttribute('onclick') ? c.getAttribute('onclick').slice(0, 200) : undefined,
    };
    if (tag === 'select') {
      f.options = [...c.querySelectorAll('option, optgroup')].map((o) => o.tagName === 'OPTGROUP' ? { optgroup: o.label } : { value: o.value, text: norm(o.textContent), selected: o.selected || undefined });
      f.multiple = c.multiple || undefined;
    }
    f.required = !!(f.htmlRequired || (f.validators || []).some((v) => /RequiredField/i.test(v.fn || '')));
    return f;
  }
  out.fields = allControls.map(fieldInfo);
  const fieldIndex = new Map(allControls.map((c, i) => [c, i]));
  const fieldRef = (c) => { const f = out.fields[fieldIndex.get(c)]; return f ? { i: f.i, type: f.type, name: f.name } : { i: -1 }; };

  // ---------- media / images ----------
  function largestFromSrcset(ss) {
    if (!ss) return null;
    let best = null, bestW = -1;
    for (const part of ss.split(/,\s+/)) {
      const bits = part.trim().split(/\s+/);
      const u = bits[0];
      if (!u) continue;
      let w = 1;
      if (bits[1]) { const m = bits[1].match(/^([\d.]+)([wx])$/); if (m) w = parseFloat(m[1]) * (m[2] === 'x' ? 1000 : 1); }
      if (w > bestW) { bestW = w; best = u; }
    }
    return best;
  }
  function imgInfo(el) {
    if (el.namespaceURI === SVGNS) {
      const r = el.getBoundingClientRect();
      return { type: 'img', svg: true, src: null, alt: el.getAttribute('aria-label') || '', renderedWidth: Math.round(r.width), renderedHeight: Math.round(r.height), outer: el.outerHTML.slice(0, 300) };
    }
    const srcAttr = el.getAttribute('src');
    const pic = el.closest('picture');
    let srcset = el.getAttribute('srcset') || '';
    if (pic) srcset = [srcset, ...[...pic.querySelectorAll('source')].map((s) => s.getAttribute('srcset') || '')].filter(Boolean).join(', ');
    const lazy = el.getAttribute('data-src') || el.getAttribute('data-lazy-src') || el.getAttribute('data-original') || null;
    const best = largestFromSrcset(srcset) || lazy || (srcAttr ? el.currentSrc || srcAttr : null);
    const a = el.closest('a[href]');
    const r = el.getBoundingClientRect();
    return {
      type: 'img', src: srcAttr ? abs(srcAttr) : null, rawSrc: srcAttr, currentSrc: el.currentSrc || null, srcset: srcset || undefined,
      best: best ? abs(best) : null, alt: el.getAttribute('alt'), title: el.getAttribute('title') || undefined,
      naturalWidth: el.naturalWidth, naturalHeight: el.naturalHeight, renderedWidth: Math.round(r.width), renderedHeight: Math.round(r.height),
      href: a ? abs(a.getAttribute('href')) : undefined, linkTarget: a ? a.getAttribute('target') || undefined : undefined,
      hidden: !rendered(el) || undefined, id: el.id || undefined, cls: (typeof el.className === 'string' && el.className) || undefined,
      style: el.getAttribute('style') || undefined,
    };
  }
  const hasImgSource = (el) => el.namespaceURI === SVGNS || !!(el.getAttribute('src') || el.getAttribute('srcset') || el.getAttribute('data-src'));
  function mediaInfo(el) {
    const tag = el.tagName.toLowerCase();
    const r = el.getBoundingClientRect();
    const base = { tag, renderedWidth: Math.round(r.width), renderedHeight: Math.round(r.height), hidden: !rendered(el) || undefined, id: el.id || undefined, cls: (typeof el.className === 'string' && el.className) || undefined };
    if (tag === 'iframe') {
      const src = el.getAttribute('src') || el.getAttribute('data-src') || '';
      const kind = /youtube|youtu\.be|vimeo|wistia|brightcove|jwplayer|video/i.test(src) ? 'video' : /google\.[^/]+\/maps|maps\.google|maps\.app/i.test(src) ? 'map' : 'iframe';
      return Object.assign(base, { type: kind, src: abs(src), title: el.getAttribute('title') || undefined, name: el.getAttribute('name') || undefined, width: el.getAttribute('width') || undefined, height: el.getAttribute('height') || undefined, allow: el.getAttribute('allow') || undefined });
    }
    if (tag === 'video' || tag === 'audio') {
      return Object.assign(base, { type: tag, src: abs(el.getAttribute('src')) || el.currentSrc || null, currentSrc: el.currentSrc || undefined, sources: [...el.querySelectorAll('source')].map((s) => ({ src: abs(s.getAttribute('src')), type: s.getAttribute('type') || undefined })), tracks: [...el.querySelectorAll('track')].map((t) => ({ src: abs(t.getAttribute('src')), kind: t.kind, label: t.label })), poster: abs(el.getAttribute('poster')), title: el.getAttribute('title') || el.getAttribute('aria-label') || undefined, dataSetup: el.getAttribute('data-setup') || undefined });
    }
    return Object.assign(base, { type: 'embed', src: abs(el.getAttribute('data') || el.getAttribute('src') || ''), mime: el.getAttribute('type') || undefined, params: [...el.querySelectorAll('param')].map((p) => ({ name: p.getAttribute('name'), value: p.getAttribute('value') })), flashvars: el.getAttribute('flashvars') || undefined });
  }

  // ---------- inline text collection ----------
  const BLOCK_TAGS = new Set(['ADDRESS', 'ARTICLE', 'ASIDE', 'BLOCKQUOTE', 'CENTER', 'DD', 'DIV', 'DL', 'DT', 'FIELDSET', 'FIGCAPTION', 'FIGURE', 'FOOTER', 'FORM', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'HEADER', 'HR', 'LI', 'MAIN', 'NAV', 'OL', 'P', 'PRE', 'SECTION', 'TABLE', 'TBODY', 'THEAD', 'TFOOT', 'TR', 'TD', 'TH', 'UL', 'CAPTION', 'LEGEND', 'DETAILS', 'SUMMARY']);
  const isBlock = (el) => {
    if (BLOCK_TAGS.has(el.tagName)) return true;
    try { return ['block', 'flex', 'grid', 'list-item', 'table', 'flow-root', 'table-row', 'table-cell'].includes(getComputedStyle(el).display); } catch (e) { return false; }
  };
  const BLOCK_DESC = 'p,div,ul,ol,h1,h2,h3,h4,h5,h6,table,blockquote,section,article,hr,dl,form,fieldset,iframe,video,object,embed,center,address,pre,figure';
  const newBuf = () => ({ text: '', md: '', links: [], hidden: false });
  const endsWS = (s) => s.length === 0 || /[ \n]$/.test(s);
  const mdEsc = (t) => t.replace(/([*\\`])/g, '\\$1');
  function trimTrail(b) { b.text = b.text.replace(/ +$/, ''); b.md = b.md.replace(/ +$/, ''); }
  function addText(b, t) {
    if (!t) return;
    if (/^ +$/.test(t)) { if (!endsWS(b.text)) { b.text += ' '; b.md += ' '; } return; }
    if (t[0] === ' ' && endsWS(b.text)) t = t.replace(/^ +/, '');
    b.text += t; b.md += mdEsc(t);
  }
  function addBr(b) { trimTrail(b); if (!b.text) return; if (!/\n\n$/.test(b.text)) { b.text += '\n'; b.md += '\n'; } }
  function addPara(b) { trimTrail(b); if (!b.text) return; while (!/\n\n$/.test(b.text)) { b.text += '\n'; b.md += '\n'; } }
  function wrapLines(s, pre, post) {
    return s.split('\n').map((line) => { const m = line.match(/^(\s*)(.*?)(\s*)$/); return m[2] ? m[1] + pre + m[2] + post + m[3] : line; }).join('\n');
  }
  function collect(node, sink, fmt) {
    if (node.nodeType === 3) { addText(sink.b, node.nodeValue.replace(/[\s ]+/g, ' ')); return; }
    if (node.nodeType !== 1) return;
    const el = node, tag = el.tagName;
    if (skipEl(el)) return;
    if (tag === 'BR') { addBr(sink.b); return; }
    if (tag === 'IMG' || (el.namespaceURI === SVGNS && tag.toLowerCase() === 'svg')) { if (hasImgSource(el)) sink.onImage(el); return; }
    if (tag === 'PICTURE') { const img = el.querySelector('img'); if (img && hasImgSource(img)) sink.onImage(img); return; }
    if (['IFRAME', 'VIDEO', 'AUDIO', 'OBJECT', 'EMBED'].includes(tag)) { sink.onMedia(el); return; }
    if (isControl(el)) { sink.onControl(el); return; }
    if (tag === 'HR') { addPara(sink.b); return; }
    const block = isBlock(el);
    if (block) addPara(sink.b);
    const isLink = tag === 'A' && el.hasAttribute('href');
    const isBold = !fmt.bold && (tag === 'STRONG' || tag === 'B');
    const isItal = !fmt.ital && (tag === 'EM' || (tag === 'I' && !/\bfa\b/.test(el.className || '')));
    const b0 = sink.b, t0 = b0.text.length, m0 = b0.md.length;
    const f2 = { bold: fmt.bold || isBold, ital: fmt.ital || isItal };
    for (const c of el.childNodes) collect(c, sink, f2);
    if (sink.b === b0 && (isBold || isItal || isLink)) {
      let seg = b0.md.slice(m0);
      if (isBold) seg = wrapLines(seg, '**', '**');
      if (isItal) seg = wrapLines(seg, '*', '*');
      if (isLink) {
        const href = abs(el.getAttribute('href'));
        const lt = norm(b0.text.slice(t0));
        if (lt) { b0.links.push({ text: lt, href, target: el.getAttribute('target') || undefined }); seg = wrapLines(seg, '[', '](' + href + ')'); }
      }
      b0.md = b0.md.slice(0, m0) + seg;
    }
    if (block) addPara(sink.b);
  }
  const tidy = (s) => s.replace(/[ ]*\n[ ]*/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
  function textOf(el) {
    if (!el) return null;
    const b = newBuf();
    const sink = { b, onImage() {}, onMedia() {}, onControl() {} };
    for (const c of el.childNodes) collect(c, sink, {});
    return tidy(b.text);
  }
  function assignLinks(paras, links) {
    let pi = 0, pos = 0;
    const outL = paras.map(() => []);
    for (const l of links) {
      let found = false;
      for (let k = pi; k < paras.length; k++) {
        const at = paras[k].indexOf(l.text, k === pi ? pos : 0);
        if (at >= 0) { outL[k].push(l); pi = k; pos = at + l.text.length; found = true; break; }
      }
      if (!found) { const k = Math.min(pi, paras.length - 1); if (k >= 0) outL[k].push(Object.assign({ unplaced: true }, l)); }
    }
    return outL;
  }

  // ---------- main content walker ----------
  let blocks = [];
  let buf = newBuf();
  function emitParas(b, type) {
    const text = tidy(b.text), md = tidy(b.md);
    if (!text) return;
    const tp = text.split(/\n\n/), mp = md.split(/\n\n/);
    const linkSets = assignLinks(tp, b.links);
    tp.forEach((t, i) => {
      if (!t.trim()) return;
      const blk = { type, text: t.trim(), md: (mp[i] || '').trim() };
      if (linkSets[i].length) blk.links = linkSets[i];
      if (b.hidden) blk.hidden = true;
      blocks.push(blk);
    });
  }
  function flush() { const b = buf; buf = newBuf(); emitParas(b, 'p'); }
  const mainSink = {
    get b() { return buf; },
    onImage(el) { flush(); blocks.push(imgInfo(el)); },
    onMedia(el) { flush(); blocks.push(mediaInfo(el)); },
    onControl(el) { flush(); blocks.push({ type: 'field', field: fieldRef(el) }); },
  };
  function localSink(b, media) {
    return { b, onImage: (i) => media.push(imgInfo(i)), onMedia: (m) => media.push(mediaInfo(m)), onControl: (c) => media.push({ type: 'field', field: fieldRef(c) }) };
  }
  function emitHeading(el) {
    const b = newBuf(), media = [];
    const sink = localSink(b, media);
    for (const c of el.childNodes) collect(c, sink, {});
    const raw = tidy(b.text);
    if (raw) {
      const blk = { type: el.tagName.toLowerCase(), text: raw.replace(/\n+/g, ' '), md: tidy(b.md).replace(/\n+/g, ' ') };
      if (raw.includes('\n')) blk.lines = raw.split(/\n+/);
      if (b.links.length) blk.links = b.links;
      if (!rendered(el)) blk.hidden = true;
      if (typeof el.className === 'string' && el.className) blk.cls = el.className;
      blocks.push(blk);
    }
    media.forEach((m) => blocks.push(m));
  }
  function listInfo(el) {
    const items = [];
    for (const li of el.children) {
      if (skipEl(li)) continue;
      const b = newBuf(), media = [], children = [];
      const sink = localSink(b, media);
      for (const c of li.childNodes) {
        if (c.nodeType === 1 && (c.tagName === 'UL' || c.tagName === 'OL')) { children.push(listInfo(c)); continue; }
        collect(c, sink, {});
      }
      const text = tidy(b.text);
      const item = { text, md: tidy(b.md) };
      if (b.links.length) item.links = b.links;
      if (media.length) item.media = media;
      if (children.length) item.children = children;
      if (!rendered(li)) item.hidden = true;
      if (li.tagName !== 'LI') item.nonLi = li.tagName.toLowerCase();
      if (text || media.length || children.length) items.push(item);
    }
    return { type: el.tagName.toLowerCase(), items };
  }
  function quoteInfo(el) {
    const b = newBuf(), media = [];
    const sink = localSink(b, media);
    for (const c of el.childNodes) collect(c, sink, {});
    const q = { type: 'blockquote', text: tidy(b.text), md: tidy(b.md) };
    if (b.links.length) q.links = b.links;
    if (media.length) q.media = media;
    if (!rendered(el)) q.hidden = true;
    return q;
  }
  function tableInfo(el) {
    const rows = [];
    for (const tr of el.querySelectorAll('tr')) {
      if (tr.closest('table') !== el) continue;
      const cells = [];
      for (const td of tr.children) {
        const b = newBuf(), media = [];
        const sink = localSink(b, media);
        for (const c of td.childNodes) collect(c, sink, {});
        const cell = { text: tidy(b.text), md: tidy(b.md) };
        if (b.links.length) cell.links = b.links;
        if (media.length) cell.media = media;
        if (td.tagName === 'TH') cell.th = true;
        if (td.colSpan > 1) cell.colspan = td.colSpan;
        cells.push(cell);
      }
      if (cells.some((c) => c.text || c.media)) rows.push(cells);
    }
    const t = { type: 'table', rows };
    if (!rendered(el)) t.hidden = true;
    return t;
  }
  function handle(node) {
    if (node.nodeType === 3) { collect(node, mainSink, {}); return; }
    if (node.nodeType !== 1) return;
    const el = node, tag = el.tagName;
    if (skipEl(el)) return;
    if (/^H[1-6]$/.test(tag)) { flush(); emitHeading(el); return; }
    if (tag === 'UL' || tag === 'OL') { flush(); blocks.push(listInfo(el)); return; }
    if (tag === 'BLOCKQUOTE') { flush(); blocks.push(quoteInfo(el)); return; }
    if (tag === 'TABLE') { flush(); blocks.push(tableInfo(el)); return; }
    if (tag === 'HR') { flush(); blocks.push({ type: 'hr' }); return; }
    if (tag === 'BR') { addBr(buf); return; }
    if (tag === 'IMG' || tag === 'PICTURE' || (el.namespaceURI === SVGNS && tag.toLowerCase() === 'svg') || ['IFRAME', 'VIDEO', 'AUDIO', 'OBJECT', 'EMBED'].includes(tag) || isControl(el)) { collect(el, mainSink, {}); return; }
    const hasBlockKids = !!el.querySelector(BLOCK_DESC);
    if (tag === 'P' || (isBlock(el) && !hasBlockKids)) {
      flush();
      const hiddenBefore = !rendered(el);
      collect(el, mainSink, {});
      if (hiddenBefore) buf.hidden = true;
      flush();
      return;
    }
    if (hasBlockKids) {
      flush();
      for (const c of el.childNodes) handle(c);
      flush();
      return;
    }
    collect(el, mainSink, {});
  }

  const main = document.querySelector('section#content');
  out.hasMainSection = !!main;
  try {
    const root = main || document.body;
    for (const c of root.childNodes) handle(c);
    flush();
  } catch (e) { out.errors.push('main walk: ' + e.message + ' ' + e.stack); }
  out.blocks = blocks;
  out.mainText = main ? main.innerText : null;
  out.mainTextContent = main ? norm(main.textContent) : null;

  // ---------- head ----------
  const meta = (n) => [...document.querySelectorAll('meta[name="' + n + '"]')].map((m) => m.getAttribute('content'));
  out.head = {
    title: norm(document.title), lang: document.documentElement.lang,
    descriptions: meta('description'), keywords: meta('keywords'), metaIndex: meta('index'), robots: meta('robots'),
    canonical: (document.querySelector('link[rel=canonical]') || {}).href || null,
    og: [...document.querySelectorAll('meta[property^="og:"], meta[name^="twitter:"], meta[property^="article:"]')].map((m) => [m.getAttribute('property') || m.getAttribute('name'), m.getAttribute('content')]),
    icons: [...document.querySelectorAll('link[rel~="icon"], link[rel^="apple-touch"], link[rel="shortcut icon"], link[rel="mask-icon"]')].map((l) => ({ rel: l.getAttribute('rel'), href: l.href, sizes: l.getAttribute('sizes') || undefined, type: l.getAttribute('type') || undefined })),
    stylesheets: [...document.querySelectorAll('link[rel="stylesheet"]')].map((l) => l.href),
    scripts: [...document.querySelectorAll('script[src]')].map((s) => s.src),
    jsonld: [...document.querySelectorAll('script[type="application/ld+json"]')].map((s) => s.textContent),
    bodyClass: document.body.className,
    formAction: (document.querySelector('#aspnetForm') || {}).getAttribute ? document.querySelector('#aspnetForm').getAttribute('action') : null,
  };
  out.inlineStyles = [...document.querySelectorAll('style')].map((s) => s.textContent).filter((t) => t && t.length < 50000);
  out.headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map((h) => ({ tag: h.tagName.toLowerCase(), text: norm(h.textContent), area: areaOf(h), hidden: !rendered(h) || undefined }));
  out.h1 = out.headings.filter((h) => h.tag === 'h1');
  const sh = main ? main.querySelector('h2.section-heading') : null;
  out.sectionHeading = sh ? norm(sh.textContent) : null;

  // ---------- header / hero / nav / chrome ----------
  try {
    out.header = {
      compTitles: [...document.querySelectorAll('#pnlheader > div')].map((d) => ({ id: d.id, cls: d.className, text: textOf(d) })),
      homeLink: (document.querySelector('.navbar-brand a') || {}).href || null,
      headerImages: [...document.querySelectorAll('header img')].filter((i) => !i.closest('.banner, #myCarousel') && hasImgSource(i)).map(imgInfo),
      menuIcons: [...document.querySelectorAll('.menu-icons a')].map((a) => ({ id: a.id, href: a.getAttribute('href') ? abs(a.getAttribute('href')) : null, title: a.getAttribute('title') || undefined, dataIcon: a.getAttribute('data-icon') || undefined, onclick: a.getAttribute('onclick') || undefined })),
      hiddenPhone: textOf(document.querySelector('.menu-icons .hiddenPhone')),
    };
  } catch (e) { out.errors.push('header: ' + e.message); }
  try {
    const hero = {};
    const car = document.querySelector('#myCarousel');
    if (car) {
      hero.carousel = [...car.querySelectorAll('.carousel-inner > .item')].map((it, i) => {
        const bgEl = it.querySelector('.itembg');
        const cs = bgEl ? getComputedStyle(bgEl) : null;
        return {
          index: i + 1, active: it.classList.contains('active'),
          leadIn: textOf(it.querySelector('.intro-lead-in')), heading: textOf(it.querySelector('.intro-heading')),
          phone: textOf(it.querySelector('.phone .seoPhone')) || textOf(it.querySelector('.phone')),
          phoneHref: (it.querySelector('.phone a[href]') || { getAttribute: () => null }).getAttribute('href'),
          bgClass: bgEl ? bgEl.className : null, bgImage: cs ? cs.backgroundImage : null, bgSize: cs ? cs.backgroundSize : null, bgPosition: cs ? cs.backgroundPosition : null,
          comment: [...it.childNodes].filter((n) => n.nodeType === 8).map((n) => n.nodeValue.trim()).join(' | ') || undefined,
          links: [...it.querySelectorAll('a[href]')].map((a) => ({ text: norm(a.textContent), href: abs(a.getAttribute('href')) })),
        };
      });
      hero.carouselInterval = 'see crawl notes';
    }
    const ban = document.querySelector('header .banner');
    if (ban) {
      const img = ban.querySelector('img');
      const a = ban.querySelector('a');
      hero.banner = { img: img ? imgInfo(img) : null, anchorId: a ? a.id : null, anchorHref: a && a.getAttribute('href') ? abs(a.getAttribute('href')) : null, text: textOf(ban) };
    }
    const go = document.querySelector('.gradient-overlay');
    if (go) hero.gradientOverlay = getComputedStyle(go).backgroundImage;
    out.hero = hero;
  } catch (e) { out.errors.push('hero: ' + e.message); }
  try {
    const navTree = (ul) => [...ul.children].filter((li) => li.tagName === 'LI').map((li) => {
      const a = li.querySelector(':scope > a');
      const label = a ? norm([...a.childNodes].filter((n) => !(n.nodeType === 1 && n.classList.contains('sub-arrow'))).map((n) => n.textContent).join('')) : '';
      const sub = li.querySelector(':scope > ul');
      return { label, title: a ? a.getAttribute('title') : null, href: a && a.getAttribute('href') ? abs(a.getAttribute('href')) : null, target: a ? a.getAttribute('target') || undefined : undefined, current: (li.className || '').match(/current|active|selected/) ? li.className : undefined, children: sub ? navTree(sub) : undefined };
    });
    const mm = document.querySelector('#main-menu');
    out.nav = mm ? navTree(mm) : null;
  } catch (e) { out.errors.push('nav: ' + e.message); }
  try {
    const pb = [...document.querySelectorAll('#aspnetForm > .phone')];
    out.phonebar = pb.map((p) => ({ text: textOf(p), links: [...p.querySelectorAll('a[href]')].map((a) => abs(a.getAttribute('href'))) }));
  } catch (e) { out.errors.push('phonebar: ' + e.message); }

  // ---------- plugins ----------
  try {
    const cf = document.querySelector('section#form');
    out.pluginContact = cf ? { present: norm(cf.textContent).length > 0, rendered: rendered(cf) && norm(cf.innerText).length > 0, heading: textOf(cf.querySelector('h2')), intro: textOf(cf.querySelector('.intro')), text: textOf(cf) } : null;
  } catch (e) { out.errors.push('pluginContact: ' + e.message); }
  try {
    const ts = document.querySelector('section#testiomnials, section.testimonials-plugin');
    if (ts) {
      let items = [...ts.querySelectorAll('.owl-item:not(.cloned) .page-item')];
      if (!items.length) items = [...ts.querySelectorAll('.page-item')];
      out.pluginTestimonials = {
        present: true, rendered: rendered(ts), heading: textOf(ts.querySelector('h2')),
        items: items.map((it) => ({ quote: textOf(it.querySelector('blockquote')), source: textOf(it.querySelector('.source')) })),
        moreLink: (ts.querySelector('a.viewmore') || {}).href || null, moreText: textOf(ts.querySelector('a.viewmore')),
      };
    } else out.pluginTestimonials = null;
  } catch (e) { out.errors.push('pluginTestimonials: ' + e.message); }
  try {
    const ad = document.querySelector('section#address');
    if (ad) {
      const q = (s) => textOf(ad.querySelector(s));
      const mapA = ad.querySelector('a.admap, a.mapicon');
      const oc = mapA ? mapA.getAttribute('onclick') || '' : '';
      const mm = oc.match(/window\.open\('([^']+)'/);
      out.pluginAddress = {
        present: true, rendered: rendered(ad), heading: q('h2'), text: textOf(ad),
        offices: [...ad.querySelectorAll('.blockwrap')].map((bw) => {
          const qq = (s) => textOf(bw.querySelector(s));
          const ma = bw.querySelector('a.admap, a.mapicon');
          const occ = ma ? ma.getAttribute('onclick') || '' : '';
          const m2 = occ.match(/window\.open\('([^']+)'/);
          return { cityName: qq('.adcity1'), address: qq('.adadd'), city: qq('[id$=City2]'), state: qq('[id$=_State]'), zip: qq('.adzip'), phone: qq('.office'), phoneLabel: qq('.adph'), mapText: ma ? textOf(ma) : null, mapUrl: m2 ? m2[1] : null, text: textOf(bw) };
        }),
        mapUrl: mm ? mm[1] : null,
      };
    } else out.pluginAddress = null;
  } catch (e) { out.errors.push('pluginAddress: ' + e.message); }
  try {
    const ft = document.querySelector('section#footer');
    out.footer = ft ? { text: textOf(ft), html: ft.innerHTML.replace(/\s+/g, ' ').slice(0, 5000), links: [...ft.querySelectorAll('a[href]')].map((a) => ({ text: norm(a.textContent), href: abs(a.getAttribute('href')), target: a.getAttribute('target') || undefined, img: a.querySelector('img') ? abs(a.querySelector('img').getAttribute('src')) : undefined })), images: [...ft.querySelectorAll('img')].filter(hasImgSource).map(imgInfo) } : null;
  } catch (e) { out.errors.push('footer: ' + e.message); }
  try {
    const formEl = document.querySelector('#aspnetForm');
    out.topSections = formEl ? [...formEl.children].map((c) => ({ el: sel(c), area: areaOf(c), textLen: norm(c.textContent).length, renderedTextLen: norm(c.innerText).length })) : [];
  } catch (e) { out.errors.push('topSections: ' + e.message); }

  // ---------- links / images / backgrounds / media (whole document) ----------
  out.links = [...document.querySelectorAll('a[href], area[href]')].map((a) => {
    const img = a.querySelector('img');
    return {
      text: norm(a.innerText || a.textContent) || (img ? '[img] ' + (img.getAttribute('alt') || img.getAttribute('src') || '') : ''),
      href: abs(a.getAttribute('href')), rawHref: a.getAttribute('href'), target: a.getAttribute('target') || undefined,
      title: a.getAttribute('title') || undefined, area: areaOf(a), onclick: a.getAttribute('onclick') ? a.getAttribute('onclick').slice(0, 400) : undefined,
    };
  });
  out.onclickLinks = [...document.querySelectorAll('[onclick]')].map((e) => ({ el: sel(e), text: norm(e.textContent).slice(0, 80), onclick: e.getAttribute('onclick').slice(0, 400), area: areaOf(e) })).filter((o) => /window\.open|location/.test(o.onclick));
  out.images = [...document.querySelectorAll('img')].filter(hasImgSource).map((i) => Object.assign(imgInfo(i), { area: areaOf(i), path: pathOf(i) }));
  out.backgrounds = [];
  out.gradients = [];
  for (const el of document.querySelectorAll('*')) {
    for (const pseudo of [null, '::before', '::after']) {
      let cs;
      try { cs = getComputedStyle(el, pseudo); } catch (e) { continue; }
      const bi = cs.backgroundImage;
      if (!bi || bi === 'none') continue;
      const urls = [...bi.matchAll(/url\(["']?([^"')]+)["']?\)/g)].map((m) => m[1]);
      const r = el.getBoundingClientRect();
      for (const u of urls) out.backgrounds.push({ url: abs(u), el: sel(el), path: pathOf(el), pseudo: pseudo || undefined, area: areaOf(el), w: Math.round(r.width), h: Math.round(r.height), size: cs.backgroundSize, position: cs.backgroundPosition, rendered: rendered(el) });
      if (!urls.length && /gradient/.test(bi)) out.gradients.push({ el: sel(el), area: areaOf(el), value: bi, pseudo: pseudo || undefined });
    }
  }
  out.media = [...document.querySelectorAll('iframe, video, audio, object, embed')].map((m) => Object.assign(mediaInfo(m), { area: areaOf(m) }));

  // ---------- styles ----------
  const SAMPLE = {
    body: 'body', navbar: 'nav.navbar-default', navbarHeader: '.navbar-header', logoTitle1: '#pnlheader .compTitle1Medium, #pnlheader [id$=CompTitle1]',
    logoTitle2: '#pnlheader [id$=CompTitle2]', tagline: '#pnlheader [id$=CompTitle3]', navTopLink: '#main-menu > li > a', navSubLink: '#main-menu ul a',
    navSubMenu: '#main-menu ul', menuIcon: '.menu-icons a', heroLeadIn: '.intro-lead-in', heroHeading: '.intro-heading', heroSeparator: '.seperator1',
    heroPhoneBtn: '#myCarousel .phone a', banner: 'header .banner', gradientOverlay: '.gradient-overlay', phoneBar: '#aspnetForm > .phone', phoneBarLink: '#aspnetForm > .phone a',
    contentSection: 'section#content', sectionHeading: 'section#content h2.section-heading', contentH2: 'section#content h2:not(.section-heading)', contentH3: 'section#content h3',
    contentP: 'section#content p', contentLink: 'section#content p a, section#content li a', contentLi: 'section#content li', contentStrong: 'section#content strong',
    contactSection: 'section#form', contactHeading: 'section#form h2', contactInput: 'section#form input[type=text]', contactButton: 'section#form input[type=button], section#form .Button',
    testimonialsSection: 'section#testiomnials', testimonialsHeading: 'section#testiomnials h2', testimonialQuote: 'section#testiomnials blockquote', testimonialSource: 'section#testiomnials .source',
    viewMoreBtn: 'a.viewmore', addressSection: 'section#address', addressHeading: 'section#address h2', addressCity: '.adcityname', addressText: 'section#address li', addressMapLink: 'section#address a',
    footer: 'section#footer', footerText: 'section#footer p', btn: '.btn', adaButton: '#ADAButton', scrollTop: '.scroll-top-inner', anyButtonInMain: 'section#content input[type=submit], section#content input[type=button], section#content button, section#content .btn',
  };
  out.styleSamples = {};
  for (const [k, s] of Object.entries(SAMPLE)) {
    let el = null;
    try { el = document.querySelector(s); } catch (e) {}
    if (!el) continue;
    const cs = getComputedStyle(el);
    out.styleSamples[k] = {
      selector: s, el: sel(el), color: hex(cs.color), background: hex(cs.backgroundColor), backgroundImage: cs.backgroundImage !== 'none' ? cs.backgroundImage.slice(0, 300) : undefined,
      fontFamily: cs.fontFamily, fontSize: cs.fontSize, fontWeight: cs.fontWeight, fontStyle: cs.fontStyle !== 'normal' ? cs.fontStyle : undefined,
      textTransform: cs.textTransform !== 'none' ? cs.textTransform : undefined, letterSpacing: cs.letterSpacing !== 'normal' ? cs.letterSpacing : undefined,
      lineHeight: cs.lineHeight, borderColor: hex(cs.borderTopColor), borderWidth: cs.borderTopWidth, borderRadius: cs.borderTopLeftRadius, textShadow: cs.textShadow !== 'none' ? cs.textShadow : undefined,
      boxShadow: cs.boxShadow !== 'none' ? cs.boxShadow.slice(0, 120) : undefined, opacity: cs.opacity !== '1' ? cs.opacity : undefined, padding: cs.padding,
    };
  }
  const textColors = {}, bgColors = {}, fontsUsed = {}, borderColors = {};
  for (const el of document.querySelectorAll('body *')) {
    if (SKIP.has(el.tagName)) continue;
    if (!rendered(el)) continue;
    const cs = getComputedStyle(el);
    const hasText = [...el.childNodes].some((n) => n.nodeType === 3 && n.nodeValue.trim());
    const r = el.getBoundingClientRect();
    const ar = areaOf(el);
    if (hasText) {
      const k = hex(cs.color);
      textColors[k] = textColors[k] || { count: 0, areas: {} };
      textColors[k].count++; textColors[k].areas[ar] = (textColors[k].areas[ar] || 0) + 1;
      const fk = cs.fontFamily + ' | ' + cs.fontWeight + (cs.fontStyle !== 'normal' ? ' ' + cs.fontStyle : '');
      fontsUsed[fk] = fontsUsed[fk] || { count: 0, areas: {} };
      fontsUsed[fk].count++; fontsUsed[fk].areas[ar] = (fontsUsed[fk].areas[ar] || 0) + 1;
    }
    const bg = cs.backgroundColor;
    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
      const k = hex(bg);
      bgColors[k] = bgColors[k] || { area: 0, examples: [] };
      bgColors[k].area += Math.round(r.width * r.height);
      if (bgColors[k].examples.length < 6) bgColors[k].examples.push(ar + ':' + sel(el));
    }
    if (parseFloat(cs.borderTopWidth) > 0 && cs.borderTopStyle !== 'none') {
      const k = hex(cs.borderTopColor);
      borderColors[k] = borderColors[k] || { count: 0, examples: [] };
      borderColors[k].count++;
      if (borderColors[k].examples.length < 4) borderColors[k].examples.push(ar + ':' + sel(el));
    }
  }
  out.colorCensus = { text: textColors, background: bgColors, border: borderColors };
  out.fontCensus = fontsUsed;
  try { out.fontsLoaded = [...document.fonts].map((f) => ({ family: f.family, weight: f.weight, style: f.style, status: f.status })); } catch (e) { out.fontsLoaded = []; }

  out.fullText = document.body.innerText;
  out.url = location.href;
  out.docHeight = document.documentElement.scrollHeight;
  return out;
})()
