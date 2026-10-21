// For downloaded images whose names carry a size suffix (_lg, _md, _sm, _th...), probe for larger/original variants.
// Saves any variant that exists and is a different file into harvest/images/ as <name>__variant<suffix>.<ext>.
import { chromium } from 'file:///C:/Users/Admin/Desktop/killer-b/node_modules/playwright-core/index.mjs';
import fs from 'node:fs';
import crypto from 'node:crypto';

const H = 'C:/Users/Admin/Desktop/porter-family-dentistry/harvest';
const log = JSON.parse(fs.readFileSync(H + '/raw/_crawl/crawl_log.json', 'utf8'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const browser = await chromium.launch({ executablePath: 'C:/Users/Admin/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe', headless: true });
const major = browser.version().split('.')[0];
const context = await browser.newContext({ userAgent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${major}.0.0.0 Safari/537.36` });
const results = [];
const SUFFIXES = ['', '_xl', '_xlg', '_orig', '_original', '_full', '_lg', '_md', '_sm'];
for (const d of log.downloads) {
  if (!d.file) continue;
  const m = d.url.match(/^(.*?)(_(?:lg|md|sm|th|thumb|med|small|large))(\.[a-z]+)$/i);
  if (!m) continue;
  const origHash = crypto.createHash('sha1').update(fs.readFileSync(H + '/' + d.file)).digest('hex');
  for (const s of SUFFIXES) {
    const v = m[1] + s + m[3];
    if (v === d.url) continue;
    let status = null, bytes = 0, ct = '', saved = null;
    try {
      const r = await context.request.get(v, { timeout: 30000, failOnStatusCode: false, headers: { Referer: 'https://www.porterfamilydentistry.com/' } });
      status = r.status();
      ct = r.headers()['content-type'] || '';
      if (status === 200 && /image/.test(ct)) {
        const body = await r.body();
        bytes = body.length;
        const hsh = crypto.createHash('sha1').update(body).digest('hex');
        if (hsh !== origHash) {
          const base = d.file.replace(/^images\//, '').replace(/(\.[a-z]+)$/i, '');
          saved = `images/${base}__variant${s || '_nosuffix'}${m[3]}`;
          fs.writeFileSync(H + '/' + saved, body);
        } else saved = 'identical to original';
      }
    } catch (e) { status = 'ERR ' + e.message; }
    results.push({ original: d.url, variant: v, status, contentType: ct, bytes, saved });
    console.log(status, bytes, v, saved || '');
    await sleep(300);
  }
}
fs.writeFileSync(H + '/raw/_crawl/variant_probe.json', JSON.stringify(results, null, 1));
await browser.close();
