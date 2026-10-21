// Polite single-context crawl of porterfamilydentistry.com (ProSites site behind AWS WAF challenge).
// Saves: harvest/raw/<slug>.html (rendered DOM), harvest/raw/_crawl/<slug>.extract.json (structured extraction),
// harvest/raw/_crawl/crawl_log.json, screenshots, CSS files, and downloads every image/doc with the same context.
import { chromium } from 'file:///C:/Users/Admin/Desktop/killer-b/node_modules/playwright-core/index.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const H = 'C:/Users/Admin/Desktop/porter-family-dentistry/harvest';
const D = {
  pages: H + '/pages', raw: H + '/raw', crawl: H + '/raw/_crawl', css: H + '/raw/css', shots: H + '/shots',
  shotsFull: H + '/raw/_shots_fullsize', images: H + '/images', docs: H + '/docs',
};
for (const d of Object.values(D)) fs.mkdirSync(d, { recursive: true });
const EXTRACT_SRC = fs.readFileSync(path.join(HERE, 'extract_inpage.js'), 'utf8');

const START = 'https://www.porterfamilydentistry.com/';
const HOSTS = new Set(['www.porterfamilydentistry.com', 'porterfamilydentistry.com']);
const SHOTS = new Map([
  ['/', 'home'], ['/our-practice/meet-the-team/', 'meet-the-team'], ['/our-services/', 'our-services'],
  ['/our-services/endodontics/root-canal-therapy/', 'service_root-canal-therapy'], ['/patient-information/', 'patient-information'], ['/contact-us/', 'contact-us'],
]);
const EXCLUDE = [/\/ada\.aspx$/i]; // accessibility-mode toggle: would switch the session into the ADA template
const FILE_RE = /\.(pdf|docx?|xlsx?|pptx?|rtf|txt|zip|jpe?g|png|gif|webp|svg|bmp|ico|mp4|m4v|mov|wmv|avi|webm|mp3|flv|swf)(\?|#|$)/i;
const MAX_PAGES = 300;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const LOGF = D.crawl + '/crawl.log';
fs.writeFileSync(LOGF, '');
const log = (...a) => { const s = `[${new Date().toISOString().slice(11, 19)}] ` + a.join(' '); console.log(s); fs.appendFileSync(LOGF, s + '\n'); };

function slugFor(u) {
  const x = new URL(u);
  let p = decodeURIComponent(x.pathname).replace(/^\/+|\/+$/g, '');
  if (!p) p = 'home';
  let s = p.toLowerCase().replace(/\//g, '__').replace(/\.aspx$/, '_aspx').replace(/[^a-z0-9_.-]+/g, '-');
  if (x.search) s += '_q-' + x.search.slice(1).toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 60);
  return s;
}
function keyOf(u) {
  const x = new URL(u);
  x.hash = '';
  return 'https://' + x.host.toLowerCase() + x.pathname.toLowerCase() + x.search;
}
function fixUrl(u) {
  if (!u) return null;
  if (u.startsWith('//')) u = 'https:' + u;
  try { const x = new URL(u); x.host = x.host.toLowerCase(); return x.href; } catch { return null; }
}

async function load(page, url) {
  const nav = [];
  const onResp = (r) => {
    try {
      if (r.frame() === page.mainFrame() && r.request().isNavigationRequest()) {
        nav.push({ status: r.status(), url: r.url(), location: r.headers()['location'] || undefined, type: r.headers()['content-type'] || undefined });
      }
    } catch {}
  };
  page.on('response', onResp);
  let err = null;
  try { await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }); } catch (e) { err = String(e.message || e).split('\n')[0]; }
  const t0 = Date.now();
  let ready = false;
  while (Date.now() - t0 < 45000) {
    ready = await page.evaluate(() => !!document.querySelector('#aspnetForm') || !!(document.body && document.body.innerText.trim().length > 400)).catch(() => false);
    if (ready) break;
    const last = nav[nav.length - 1];
    if (last && last.status !== 202 && Date.now() - t0 > 6000) {
      const rs = await page.evaluate(() => document.readyState).catch(() => '');
      if (rs === 'complete') break;
    }
    await sleep(1000);
  }
  try { await page.waitForLoadState('networkidle', { timeout: 15000 }); } catch {}
  await sleep(2000 + Math.floor(Math.random() * 2000));
  page.off('response', onResp);
  return { nav, err, ready, finalUrl: page.url() };
}

async function scrollThrough(page) {
  await page.evaluate(async () => {
    const h = () => document.documentElement.scrollHeight;
    for (let y = 0; y < h(); y += 450) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 140)); }
    window.scrollTo(0, h());
    await new Promise((r) => setTimeout(r, 600));
    window.scrollTo(0, 0);
  }).catch(() => {});
  await sleep(900);
}

const browser = await chromium.launch({ executablePath: 'C:/Users/Admin/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe', headless: true });
const major = browser.version().split('.')[0];
const UA = `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${major}.0.0.0 Safari/537.36`;
log('browser', browser.version(), 'UA', UA);
const context = await browser.newContext({ userAgent: UA, viewport: { width: 1440, height: 900 }, locale: 'en-US', timezoneId: 'America/Chicago' });
const page = await context.newPage();

const queue = [{ url: START, via: 'start', from: null }];
const queued = new Set([keyOf(START)]);
const linkedFrom = {};   // key -> [{from, text, area}]
const fetches = [];      // one record per GET
const finalToSlug = new Map();
const pageRecords = [];
const fileLinks = new Map(); // url -> [{from, text, area}]
const offsite = new Map();   // url -> [{from,text,area}]
const skipped = [];

function consider(href, fromUrl, text, area, via) {
  if (!href) return;
  let x;
  try { x = new URL(href); } catch { skipped.push({ href, fromUrl, reason: 'bad url' }); return; }
  if (!/^https?:$/.test(x.protocol)) return; // mailto:, tel:, javascript:
  x.hash = '';
  const host = x.host.toLowerCase();
  if (!HOSTS.has(host)) {
    const k = x.href;
    if (!offsite.has(k)) offsite.set(k, []);
    offsite.get(k).push({ from: fromUrl, text, area });
    return;
  }
  if (x.protocol === 'http:') x.protocol = 'https:';
  if (FILE_RE.test(x.pathname)) {
    if (!fileLinks.has(x.href)) fileLinks.set(x.href, []);
    fileLinks.get(x.href).push({ from: fromUrl, text, area });
    return;
  }
  if (EXCLUDE.some((re) => re.test(x.pathname))) { skipped.push({ href: x.href, fromUrl, reason: 'excluded (accessibility-mode toggle)' }); return; }
  const k = keyOf(x.href);
  (linkedFrom[k] = linkedFrom[k] || []).push({ from: fromUrl, text, area });
  if (queued.has(k)) return;
  queued.add(k);
  queue.push({ url: x.href, via, from: fromUrl });
}

let first = true;
while (queue.length && pageRecords.length < MAX_PAGES) {
  const item = queue.shift();
  log(`#${fetches.length + 1} (${queue.length} queued) GET ${item.url}  [via ${item.via}]`);
  const res = await load(page, item.url);
  const last = res.nav[res.nav.length - 1];
  const rec = { requested: item.url, via: item.via, from: item.from, nav: res.nav, finalUrl: res.finalUrl, status: last ? last.status : null, error: res.err || undefined, ready: res.ready };
  fetches.push(rec);
  let finalHost = '';
  try { finalHost = new URL(res.finalUrl).host.toLowerCase(); } catch {}
  if (!HOSTS.has(finalHost)) { rec.note = 'final URL off-site or invalid'; log('  -> off-site/invalid', res.finalUrl); continue; }
  const fk = keyOf(res.finalUrl);
  if (finalToSlug.has(fk)) { rec.aliasOf = finalToSlug.get(fk); log(`  -> alias of ${rec.aliasOf} (final ${res.finalUrl})`); continue; }

  if (first) {
    first = false;
    for (const f of ['robots.txt', 'sitemap.xml', 'sitemap.aspx']) {
      try {
        const r = await context.request.get('https://www.porterfamilydentistry.com/' + f, { timeout: 30000, failOnStatusCode: false });
        const body = await r.text();
        fs.writeFileSync(`${D.raw}/_${f.replace(/\./g, '_')}.txt`, `status ${r.status()}\ncontent-type ${r.headers()['content-type']}\n\n` + body);
        log(`  fetched ${f}: ${r.status()} ${body.length} bytes`);
        if (r.status() === 200) for (const m of body.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/gi)) consider(m[1].replace(/&amp;/g, '&'), 'sitemap:' + f, '', 'sitemap', 'sitemap');
        if (f === 'robots.txt' && r.status() === 200) for (const m of body.matchAll(/^sitemap:\s*(\S+)/gim)) log('  robots sitemap:', m[1]);
      } catch (e) { log('  fetch', f, 'failed', e.message); }
    }
  }

  await scrollThrough(page);
  let data;
  try { data = await page.evaluate(EXTRACT_SRC); } catch (e) { log('  EXTRACT ERROR', e.message); data = { errors: ['evaluate failed: ' + e.message] }; }
  data.frames = [];
  for (const f of page.frames()) {
    if (f === page.mainFrame()) continue;
    let text = null;
    try { text = await f.evaluate(() => (document.body ? document.body.innerText : '')); } catch (e) { text = 'ERR ' + e.message; }
    data.frames.push({ url: f.url(), name: f.name(), text });
  }
  const slug = slugFor(res.finalUrl);
  finalToSlug.set(fk, slug);
  rec.slug = slug;
  data.fetch = rec;
  data.slug = slug;
  fs.writeFileSync(`${D.raw}/${slug}.html`, await page.content());
  fs.writeFileSync(`${D.crawl}/${slug}.extract.json`, JSON.stringify(data, null, 1));
  pageRecords.push({ slug, finalUrl: res.finalUrl, requested: item.url, status: rec.status, title: data.head ? data.head.title : null });
  log(`  -> ${rec.status} ${res.finalUrl} slug=${slug} title=${JSON.stringify(data.head && data.head.title)} blocks=${(data.blocks || []).length} imgs=${(data.images || []).length} bgs=${(data.backgrounds || []).length} errs=${(data.errors || []).length}`);
  if (data.errors && data.errors.length) log('  errors:', JSON.stringify(data.errors).slice(0, 500));

  for (const l of data.links || []) consider(l.href, res.finalUrl, l.text, l.area, 'link');
  for (const o of data.onclickLinks || []) { const m = (o.onclick || '').match(/window\.open\('([^']+)'/); if (m) consider(new URL(m[1], res.finalUrl).href, res.finalUrl, o.text, o.area, 'onclick'); }
  for (const m of data.media || []) if (m.src) consider(m.src, res.finalUrl, '[media] ' + (m.title || ''), m.area, 'media');

  const p = new URL(res.finalUrl).pathname.toLowerCase();
  if (SHOTS.has(p)) {
    const name = SHOTS.get(p);
    try {
      await page.evaluate(() => window.scrollTo(0, 0));
      await sleep(1200);
      await page.screenshot({ path: `${D.shots}/${name}_desktop-1440_first-screen.png` });
      await page.screenshot({ path: `${D.shotsFull}/${name}_desktop-1440_fullpage.png`, fullPage: true });
      log('  screenshots saved for', name);
    } catch (e) { log('  screenshot error', e.message); }
  }
}

// mobile first screen of home (same context, narrow viewport)
try {
  await page.setViewportSize({ width: 390, height: 844 });
  await load(page, START);
  await scrollThrough(page);
  await page.evaluate(() => window.scrollTo(0, 0));
  await sleep(1200);
  await page.screenshot({ path: `${D.shots}/home_mobile-390_first-screen.png` });
  await page.screenshot({ path: `${D.shotsFull}/home_mobile-390_fullpage.png`, fullPage: true });
  const mob = await page.evaluate(EXTRACT_SRC).catch(() => null);
  if (mob) fs.writeFileSync(`${D.crawl}/_home_mobile.extract.json`, JSON.stringify({ images: mob.images, backgrounds: mob.backgrounds, styleSamples: mob.styleSamples, hero: mob.hero }, null, 1));
  log('mobile screenshot saved');
  await page.setViewportSize({ width: 1440, height: 900 });
} catch (e) { log('mobile screenshot error', e.message); }

// ---------- CSS files ----------
const cssUrls = new Set();
const allExtracts = pageRecords.map((r) => JSON.parse(fs.readFileSync(`${D.crawl}/${r.slug}.extract.json`, 'utf8')));
for (const ex of allExtracts) for (const s of (ex.head && ex.head.stylesheets) || []) cssUrls.add(fixUrl(s));
const cssRefs = [];
const cssIndex = [];
async function fetchCss(u, depth) {
  if (!u || depth > 2) return;
  try {
    const r = await context.request.get(u, { timeout: 30000, failOnStatusCode: false });
    const body = await r.text();
    const fname = slugFor(u).replace(/\.css$/, '') + '.css';
    fs.writeFileSync(`${D.css}/${fname}`, body);
    cssIndex.push({ url: u, status: r.status(), file: 'raw/css/' + fname, bytes: body.length });
    for (const m of body.matchAll(/url\(\s*["']?([^"')]+?)["']?\s*\)/g)) {
      const ref = m[1];
      if (ref.startsWith('data:')) continue;
      const full = fixUrl(new URL(ref, u).href);
      cssRefs.push({ css: u, ref, url: full });
    }
    for (const m of body.matchAll(/@import\s+(?:url\()?["']?([^"')\s;]+)/g)) await fetchCss(fixUrl(new URL(m[1], u).href), depth + 1);
  } catch (e) { cssIndex.push({ url: u, error: e.message }); }
  await sleep(300);
}
for (const u of cssUrls) await fetchCss(u, 0);
// inline <style> url() refs
for (const ex of allExtracts) for (const st of ex.inlineStyles || []) for (const m of st.matchAll(/url\(\s*["']?([^"')]+?)["']?\s*\)/g)) {
  if (m[1].startsWith('data:')) continue;
  cssRefs.push({ css: 'inline-style:' + ex.slug, ref: m[1], url: fixUrl(new URL(m[1], ex.url || START).href) });
}
log('css files', cssIndex.length, 'css url refs', cssRefs.length);

// ---------- image + doc downloads ----------
const IMG_EXT = /\.(jpe?g|png|gif|webp|svg|bmp|ico|avif)(\?|$)/i;
const want = new Map(); // url -> {sources:[...]}
const addWant = (u, src) => { u = fixUrl(u); if (!u || u.startsWith('data:')) return; if (!want.has(u)) want.set(u, { sources: [] }); want.get(u).sources.push(src); };
for (const ex of allExtracts) {
  for (const i of ex.images || []) { if (i.best) addWant(i.best, { kind: 'img', page: ex.slug, area: i.area }); if (i.src && i.src !== i.best) addWant(i.src, { kind: 'img-src', page: ex.slug, area: i.area }); }
  for (const b of ex.backgrounds || []) addWant(b.url, { kind: 'css-bg', page: ex.slug, area: b.area, el: b.el });
  for (const ic of (ex.head && ex.head.icons) || []) addWant(ic.href, { kind: 'icon', page: ex.slug, rel: ic.rel });
  for (const [k, v] of (ex.head && ex.head.og) || []) if (/image/i.test(k) && v) addWant(v, { kind: 'og', page: ex.slug });
  for (const m of ex.media || []) if (m.poster) addWant(m.poster, { kind: 'video-poster', page: ex.slug });
}
for (const c of cssRefs) if (c.url && IMG_EXT.test(new URL(c.url).pathname)) addWant(c.url, { kind: 'css-ref', css: c.css });
for (const [u, refs] of fileLinks) if (IMG_EXT.test(new URL(u).pathname)) addWant(u, { kind: 'linked-file', page: refs[0].from });
addWant('https://www.porterfamilydentistry.com/favicon.ico', { kind: 'favicon-probe' });

const usedNames = new Map();
function localName(u, dir) {
  const x = new URL(u);
  let base = decodeURIComponent(x.pathname.split('/').filter(Boolean).pop() || 'index');
  base = base.replace(/\s+/g, '-').replace(/[^A-Za-z0-9._-]+/g, '_');
  let name = base;
  const parent = decodeURIComponent(x.pathname.split('/').filter(Boolean).slice(-2, -1)[0] || '').replace(/[^A-Za-z0-9._-]+/g, '_');
  const key = dir + '/' + name.toLowerCase();
  if (usedNames.has(key) && usedNames.get(key) !== u) {
    name = (parent ? parent + '__' : '') + base;
    let n = 2;
    while (usedNames.has(dir + '/' + name.toLowerCase()) && usedNames.get(dir + '/' + name.toLowerCase()) !== u) name = `${n++}__` + base;
  }
  usedNames.set(dir + '/' + name.toLowerCase(), u);
  return name;
}
const downloads = [];
async function download(u, dir, meta) {
  const tries = [u];
  if (u.startsWith('https://') && !/porterfamilydentistry/.test(u)) tries.push(u.replace('https://', 'http://'));
  for (const t of tries) {
    try {
      const r = await context.request.get(t, { timeout: 60000, failOnStatusCode: false, headers: { Referer: START } });
      const status = r.status();
      const ct = r.headers()['content-type'] || '';
      if (status !== 200) { if (t === tries[tries.length - 1]) downloads.push({ url: u, tried: t, status, contentType: ct, ...meta }); continue; }
      const body = await r.body();
      if (/text\/html/i.test(ct) && !/\.html?$/i.test(t)) { downloads.push({ url: u, tried: t, status, contentType: ct, note: 'got HTML instead of file', bytes: body.length, ...meta }); continue; }
      const name = localName(u, dir);
      fs.writeFileSync(`${dir}/${name}`, body);
      downloads.push({ url: u, fetchedFrom: t, status, contentType: ct, bytes: body.length, file: path.relative(H, `${dir}/${name}`).replace(/\\/g, '/'), ...meta });
      return;
    } catch (e) { if (t === tries[tries.length - 1]) downloads.push({ url: u, tried: t, error: e.message, ...meta }); }
  }
}
log('downloading', want.size, 'image urls and', fileLinks.size, 'linked files');
for (const [u, info] of want) { await download(u, D.images, { sources: info.sources }); await sleep(250); }
for (const [u, refs] of fileLinks) { if (IMG_EXT.test(new URL(u).pathname)) continue; await download(u, D.docs, { linkedFrom: refs }); await sleep(250); }

fs.writeFileSync(`${D.crawl}/crawl_log.json`, JSON.stringify({
  started: START, userAgent: UA, browser: browser.version(), finished: new Date().toISOString(),
  fetches, pages: pageRecords, linkedFrom, fileLinks: Object.fromEntries(fileLinks), offsite: Object.fromEntries(offsite), skipped,
  css: cssIndex, cssRefs, downloads,
}, null, 1));
log('DONE pages', pageRecords.length, 'fetches', fetches.length, 'downloads', downloads.length);
await browser.close();
