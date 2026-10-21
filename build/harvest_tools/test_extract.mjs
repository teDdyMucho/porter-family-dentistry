// Test harness: load the given URLs in one context and write extraction JSON to an output dir.
import { chromium } from 'file:///C:/Users/Admin/Desktop/killer-b/node_modules/playwright-core/index.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SRC = fs.readFileSync(path.join(HERE, 'extract_inpage.js'), 'utf8');
const [outDir, ...urls] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const browser = await chromium.launch({ executablePath: 'C:/Users/Admin/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe', headless: true });
const major = browser.version().split('.')[0];
const context = await browser.newContext({ userAgent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${major}.0.0.0 Safari/537.36`, viewport: { width: 1440, height: 900 }, locale: 'en-US' });
const page = await context.newPage();
for (const u of urls) {
  const nav = [];
  const on = (r) => { try { if (r.frame() === page.mainFrame() && r.request().isNavigationRequest()) nav.push([r.status(), r.url()]); } catch {} };
  page.on('response', on);
  await page.goto(u, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch((e) => console.log('goto err', e.message));
  for (let i = 0; i < 40; i++) { if (await page.evaluate(() => !!document.querySelector('#aspnetForm')).catch(() => false)) break; await sleep(1000); }
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await sleep(2500);
  page.off('response', on);
  const t = Date.now();
  const data = await page.evaluate(SRC);
  const name = new URL(page.url()).pathname.replace(/^\/|\/$/g, '').replace(/\//g, '__') || 'home';
  fs.writeFileSync(path.join(outDir, name + '.json'), JSON.stringify(data, null, 1));
  console.log(JSON.stringify(nav), '->', page.url(), 'extract ms', Date.now() - t, 'blocks', data.blocks.length, 'errors', JSON.stringify(data.errors));
}
await browser.close();
