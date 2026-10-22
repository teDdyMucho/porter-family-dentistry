/* David L. Porter, D.D.S., P.C. — site behaviour. No libraries. */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches || root.classList.contains('nomotion');
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------- Office hours: today's row, and the open-now line in the top strip ----------
     Hours come from data-hours on <body>: {"1": ["08:00","17:00"], ...} keyed by weekday (0 = Sunday).
     The practice's clock is America/Chicago (La Porte, Indiana is on Central time). */
  var hours = {};
  try { hours = JSON.parse(document.body.getAttribute('data-hours') || '{}'); } catch (e) { hours = {}; }
  var TZ = document.body.getAttribute('data-tz') || 'America/Chicago';

  function officeNow() {
    var parts = new Intl.DateTimeFormat('en-US', { timeZone: TZ, weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' })
      .formatToParts(new Date()).reduce(function (o, p) { o[p.type] = p.value; return o; }, {});
    var day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(parts.weekday);
    return { day: day, minutes: Number(parts.hour) * 60 + Number(parts.minute) };
  }
  var toMin = function (t) { var p = t.split(':'); return Number(p[0]) * 60 + Number(p[1] || 0); };
  var label = function (t) {
    var m = toMin(t), h = Math.floor(m / 60), mm = m % 60, ap = h >= 12 ? 'pm' : 'am';
    h = h % 12 || 12;
    return h + (mm ? ':' + String(mm).padStart(2, '0') : '') + ap;
  };
  var DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  function renderStatus() {
    if (!Object.keys(hours).length) return;
    var now = officeNow(), today = hours[now.day], text, open = false;
    if (today && now.minutes >= toMin(today[0]) && now.minutes < toMin(today[1])) {
      open = true; text = 'Open today until ' + label(today[1]);
    } else if (today && now.minutes < toMin(today[0])) {
      text = 'Opens today at ' + label(today[0]);
    } else {
      for (var i = 1; i <= 7; i++) {
        var d = (now.day + i) % 7;
        if (hours[d]) { text = 'Closed now · opens ' + (i === 1 ? 'tomorrow' : DAYS[d]) + ' at ' + label(hours[d][0]); break; }
      }
    }
    $$('[data-status]').forEach(function (el) {
      el.classList.toggle('is-open', open);
      var t = $('[data-status-text]', el);
      if (t && text) t.textContent = text;
    });
    $$('.hours tbody tr[data-day]').forEach(function (tr) { tr.classList.toggle('is-today', Number(tr.getAttribute('data-day')) === now.day); });
  }
  renderStatus();
  setInterval(renderStatus, 60000);

  /* ---------- Header: a border once the page moves ---------- */
  var header = $('.site-header');
  if (header) {
    var onScroll = function () { header.classList.toggle('is-stuck', scrollY > 8); };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Desktop dropdowns and the services panel ----------
     Open on click (and Enter/Space), never on hover; Escape closes and returns focus to the trigger;
     an outside click or picking a link closes. */
  var items = $$('.nav__item[data-dropdown]');
  var openItem = null;

  function setOpen(item, open) {
    var trigger = $('.nav__trigger', item);
    item.classList.toggle('is-open', open);
    trigger.setAttribute('aria-expanded', String(open));
    if (open) { if (openItem && openItem !== item) setOpen(openItem, false); openItem = item; }
    else if (openItem === item) openItem = null;
  }
  items.forEach(function (item) {
    var trigger = $('.nav__trigger', item);
    trigger.addEventListener('click', function () { setOpen(item, !item.classList.contains('is-open')); });
    item.addEventListener('click', function (e) { if (e.target.closest('.panel a')) setOpen(item, false); });
    item.addEventListener('focusout', function (e) { if (e.relatedTarget && !item.contains(e.relatedTarget)) setOpen(item, false); });
  });
  document.addEventListener('click', function (e) { if (openItem && !openItem.contains(e.target)) setOpen(openItem, false); });
  addEventListener('scroll', function () { if (openItem && scrollY > 400) setOpen(openItem, false); }, { passive: true });

  /* ---------- Phone and tablet drawer ---------- */
  var drawer = $('#drawer'), menuBtn = $('.menu-btn');
  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle('is-open', open);
    drawer.setAttribute('aria-hidden', String(!open));
    root.classList.toggle('menu-open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    if (open) { var first = $('a, button, summary', drawer); if (first) first.focus(); }
  }
  if (drawer && menuBtn) {
    menuBtn.addEventListener('click', function () { setDrawer(!drawer.classList.contains('is-open')); });
    $$('[data-drawer-close]', drawer).forEach(function (b) { b.addEventListener('click', function () { setDrawer(false); menuBtn.focus(); }); });
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) setDrawer(false); });
    matchMedia('(min-width: 1181px)').addEventListener('change', function (e) { if (e.matches) setDrawer(false); });
  }
  addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (drawer && drawer.classList.contains('is-open')) { setDrawer(false); menuBtn.focus(); return; }
    if (openItem) { var t = $('.nav__trigger', openItem); setOpen(openItem, false); t.focus(); }
  });

  /* ---------- The aurora rests while nobody can see it ---------- */
  var hero = $('.hero');
  if (hero && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { hero.classList.toggle('is-offscreen', !es[0].isIntersecting); }).observe(hero);
  }

  /* ---------- Phone call bar: out of the way where the page already offers the same actions ---------- */
  var callBar = $('.call-bar');
  if (callBar && 'IntersectionObserver' in window) {
    var hiddenBy = new Set();
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.isIntersecting ? hiddenBy.add(e.target) : hiddenBy.delete(e.target); });
      callBar.classList.toggle('is-hidden', hiddenBy.size > 0);
    });
    $$('.hero__cta, .page-head__actions, .closer, .site-footer, .form').forEach(function (el) { io.observe(el); });
  }

  /* ---------- Reveal: below-the-fold blocks arrive gently, once ----------
     Only what starts below the fold is hidden, so nothing on screen blinks; no script or reduced
     motion means nothing is hidden at all. */
  if (!reduced && 'IntersectionObserver' in window) {
    var fold = innerHeight * 0.94;
    var pending = $$('[data-reveal]').filter(function (el) { return el.getBoundingClientRect().top > fold; });
    var reveal = function (el) {
      if (!el.classList.contains('is-pending')) return;
      el.classList.replace('is-pending', 'is-in');
      revealIO.unobserve(el);
      setTimeout(function () { el.classList.remove('is-in'); el.style.removeProperty('--d'); }, 1600);
    };
    var revealIO = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) reveal(e.target); });
    }, { rootMargin: '0px 0px -8% 0px' });
    pending.forEach(function (el) {
      el.classList.add('is-pending');
      var row = Array.prototype.filter.call(el.parentElement.children, function (c) { return pending.indexOf(c) > -1; });
      var i = row.indexOf(el);
      if (i > 0) el.style.setProperty('--d', Math.min(i, 5) * 110 + 'ms');
      revealIO.observe(el);
    });
    var sweep = function () {
      $$('.is-pending').forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < innerHeight * 0.94 && r.bottom > 0) reveal(el);
      });
    };
    addEventListener('scroll', function () { requestAnimationFrame(sweep); }, { passive: true });
    addEventListener('resize', sweep);
  }

  /* ---------- Dental videos: each plays in a dialog, and stops when it closes ---------- */
  var player = $('#player');
  if (player && player.showModal) {
    var video = $('#playerVideo'), ptitle = $('#playerTitle');
    $$('[data-video]').forEach(function (b) {
      b.addEventListener('click', function () {
        video.src = b.getAttribute('data-video');
        ptitle.textContent = b.getAttribute('data-title');
        player.showModal();
        var p = video.play(); if (p && p.catch) p.catch(function () {});
      });
    });
    $('[data-player-close]', player).addEventListener('click', function () { player.close(); });
    player.addEventListener('click', function (e) { if (e.target === player) player.close(); });
    player.addEventListener('close', function () { video.pause(); video.removeAttribute('src'); video.load(); });
  }

  /* ---------- Numbers count up as they arrive ---------- */
  var counters = $$('[data-count]').filter(function (el) { return !reduced && el.getBoundingClientRect().top > innerHeight * 0.94; });
  if (counters.length && 'IntersectionObserver' in window) {
    var countIO = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        countIO.unobserve(en.target);
        var el = en.target, to = Number(el.getAttribute('data-count')), t0 = performance.now(), dur = 1600;
        (function tick(now) {
          var k = Math.min((now - t0) / dur, 1), eased = 1 - Math.pow(1 - k, 4);
          el.textContent = String(Math.round(to * eased));
          if (k < 1) requestAnimationFrame(tick); else el.textContent = String(to);
        })(t0);
      });
    }, { rootMargin: '0px 0px -10% 0px' });
    counters.forEach(function (el) { el.textContent = '0'; countIO.observe(el); });
  }

  /* ---------- The closing headline: words rise out of a mask, once ---------- */
  var heads = $$('[data-words]').filter(function (el) { return !reduced && el.getBoundingClientRect().top > innerHeight * 0.94; });
  if (heads.length && 'IntersectionObserver' in window) {
    heads.forEach(function (el) {
      var text = el.textContent.trim();
      el.setAttribute('aria-label', text);
      el.innerHTML = text.split(/\s+/).map(function (w, i) {
        return '<span class="w" aria-hidden="true" style="--i:' + i + '"><i>' + w.replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }) + '</i></span>';
      }).join(' ');
    });
    var wordsIO = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('words-in'); wordsIO.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -12% 0px' });
    heads.forEach(function (el) { wordsIO.observe(el); });
  }

  /* ---------- Embedded maps and calculators: a ring while the keyboard is inside ----------
     Focus inside another site's frame never reaches :focus-within, so the frame's box is marked
     when a Tab carries focus into it, and unmarked when focus comes back to the page. */
  var tabbedAt = 0;
  addEventListener('keydown', function (e) { if (e.key === 'Tab') tabbedAt = Date.now(); });
  addEventListener('blur', function () {
    setTimeout(function () {
      var frame = document.activeElement;
      if (!frame || frame.tagName !== 'IFRAME' || Date.now() - tabbedAt > 400) return;
      var box = frame.closest('.map, .embed');
      if (box) box.classList.add('is-focused');
    });
  });
  addEventListener('focus', function () { $$('.map.is-focused, .embed.is-focused').forEach(function (el) { el.classList.remove('is-focused'); }); });

  /* ---------- Forms: errors in words, under the field ---------- */
  $$('form[data-form]').forEach(function (form) {
    var status = $('.form__status', form);
    function check(field) {
      var input = $('input, select, textarea', field);
      if (!input) return true;
      var ok = input.checkValidity();
      if (input.type === 'tel' && input.value.trim()) ok = ok && input.value.replace(/\D/g, '').length >= 10;
      var group = $$('input[type=radio], input[type=checkbox]', field);
      if (group.length && field.hasAttribute('data-required')) ok = group.some(function (g) { return g.checked; });
      field.classList.toggle('is-invalid', !ok);
      return ok;
    }
    // "Phone OR email" (the office's own rule): at least one of the named fields must be filled
    var oneOf = (form.getAttribute('data-one-of') || '').split(',').filter(Boolean)
      .map(function (n) { return form.elements[n]; }).filter(Boolean);
    function checkOneOf() {
      if (!oneOf.length) return [];
      var any = oneOf.some(function (i) { return i.value.trim(); });
      if (any) return [];
      return oneOf.map(function (i) { var f = i.closest('.field'); f.classList.add('is-invalid'); return f; });
    }
    function recheck(f) {
      check(f);
      if (oneOf.some(function (i) { return f.contains(i); })) {
        oneOf.forEach(function (i) { check(i.closest('.field')); });
        checkOneOf();
      }
    }
    form.addEventListener('input', function (e) { var f = e.target.closest('.field'); if (f && f.classList.contains('is-invalid')) recheck(f); });
    form.addEventListener('change', function (e) { var f = e.target.closest('.field'); if (f && f.classList.contains('is-invalid')) recheck(f); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var fields = $$('.field', form), bad = fields.filter(function (f) { return !check(f); });
      checkOneOf().forEach(function (f) { if (bad.indexOf(f) < 0) bad.push(f); });
      if (bad.length) {
        status.className = 'form__status is-err';
        status.textContent = 'Please check the ' + (bad.length === 1 ? 'highlighted field.' : bad.length + ' highlighted fields.');
        var first = $('input, select, textarea', bad[0]); if (first) first.focus();
        return;
      }
      var endpoint = form.getAttribute('data-endpoint');
      var data = new FormData(form);
      var btn = $('button[type=submit]', form), label0 = btn.textContent;
      if (endpoint) {
        btn.disabled = true; btn.textContent = 'Sending…';
        fetch(endpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
          .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset(); status.className = 'form__status is-ok'; status.textContent = form.getAttribute('data-success'); })
          .catch(function () { status.className = 'form__status is-err'; status.textContent = 'That didn’t send. Please call us at ' + form.getAttribute('data-phone') + '.'; })
          .finally(function () { btn.disabled = false; btn.textContent = label0; });
        return;
      }
      // No form service connected yet: hand the request to the visitor's email app, addressed to the office.
      var lines = [];
      data.forEach(function (v, k) { if (String(v).trim()) lines.push(k + ': ' + v); });
      location.href = 'mailto:' + form.getAttribute('data-mailto') + '?subject=' + encodeURIComponent(form.getAttribute('data-subject')) +
        '&body=' + encodeURIComponent(lines.join('\n'));
      status.className = 'form__status is-ok';
      status.textContent = 'Your email app should open with your request filled in. If it doesn’t, please call ' + form.getAttribute('data-phone') + '.';
    });
  });
})();
