// Probe: load home page through the bot check, dump raw HTML + a structural outline.
import { chromium } from 'file:///C:/Users/Admin/Desktop/killer-b/node_modules/playwright-core/index.mjs';
import fs from 'node:fs';
import path from 'node:path';

const OUT = 'C:/Users/Admin/Desktop/porter-family-dentistry/harvest/raw';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
const url = process.argv[2] || 'https://www.porterfamilydentistry.com/';
const name = process.argv[3] || 'probe_home';

const browser = await chromium.launch({
  executablePath: 'C:/Users/Admin/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe',
  headless: true,
});
const context = await browser.newContext({ userAgent: UA, viewport: { width: 1440, height: 900 }, locale: 'en-US' });
const page = await context.newPage();
const statuses = [];
page.on('response', r => { if (r.request().resourceType() === 'document') statuses.push([r.status(), r.url()]); });
const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
console.log('first status', resp && resp.status());
for (let i = 0; i < 20; i++) {
  await page.waitForTimeout(1500);
  const len = await page.evaluate(() => document.body ? document.body.innerText.length : 0);
  const title = await page.title();
  console.log(`t=${(i + 1) * 1.5}s title=${JSON.stringify(title)} textlen=${len} url=${page.url()}`);
  if (len > 2000) break;
}
try { await page.waitForLoadState('networkidle', { timeout: 15000 }); } catch (e) { console.log('networkidle timeout'); }
console.log('doc statuses', JSON.stringify(statuses));
const html = await page.content();
fs.writeFileSync(path.join(OUT, name + '.html'), html);
// structural outline
const outline = await page.evaluate(() => {
  const out = [];
  function walk(el, depth) {
    if (depth > 7) return;
    for (const c of el.children) {
      const tag = c.tagName.toLowerCase();
      if (['script', 'style', 'noscript', 'link', 'meta'].includes(tag)) continue;
      const id = c.id ? '#' + c.id : '';
      const cls = c.className && typeof c.className === 'string' ? '.' + c.className.trim().split(/\s+/).slice(0, 4).join('.') : '';
      const txt = (c.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 60);
      out.push('  '.repeat(depth) + tag + id + cls + '  [' + (c.innerText || '').length + '] ' + txt);
      walk(c, depth + 1);
    }
  }
  walk(document.body, 0);
  return out.join('\n');
});
fs.writeFileSync(path.join(OUT, name + '_outline.txt'), outline);
const cookies = await context.cookies();
console.log('cookies', cookies.map(c => c.name + '@' + c.domain).join(', '));
await browser.close();
