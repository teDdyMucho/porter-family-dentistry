// Re-shoot: home full page with the carousel paused on slide 1; contact-us with the Google map given time to paint.
import { chromium } from 'file:///C:/Users/Admin/Desktop/killer-b/node_modules/playwright-core/index.mjs';
import fs from 'node:fs';

const H = 'C:/Users/Admin/Desktop/porter-family-dentistry/harvest';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const browser = await chromium.launch({ executablePath: 'C:/Users/Admin/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe', headless: true });
const major = browser.version().split('.')[0];
const context = await browser.newContext({ userAgent: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${major}.0.0.0 Safari/537.36`, viewport: { width: 1440, height: 900 }, locale: 'en-US' });
const page = await context.newPage();
async function load(u) {
  await page.goto(u, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
  for (let i = 0; i < 40; i++) { if (await page.evaluate(() => !!document.querySelector('#aspnetForm')).catch(() => false)) break; await sleep(1000); }
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await sleep(3000);
  await page.evaluate(async () => { for (let y = 0; y < document.documentElement.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 150)); } window.scrollTo(0, 0); });
  await sleep(1500);
}
// home: freeze carousel on slide 1 and disable transitions
await load('https://www.porterfamilydentistry.com/');
await page.evaluate(() => {
  try { $('.carousel').carousel('pause'); } catch (e) {}
  const items = [...document.querySelectorAll('#myCarousel .item')];
  items.forEach((it, i) => { it.classList.remove('active', 'next', 'prev', 'left', 'right'); if (i === 0) it.classList.add('active'); });
  const st = document.createElement('style');
  st.textContent = '#myCarousel .item{transition:none!important}';
  document.head.appendChild(st);
});
await sleep(800);
await page.screenshot({ path: `${H}/shots/home_desktop-1440_first-screen_slide1.png` });
await page.screenshot({ path: `${H}/raw/_shots_fullsize/home_desktop-1440_fullpage.png`, fullPage: true });
// contact-us: let the map paint, and report on the Office Location strip
await load('https://www.porterfamilydentistry.com/contact-us/');
const info = await page.evaluate(() => {
  const ad = document.querySelector('section#address');
  const cs = ad ? getComputedStyle(ad) : null;
  const r = ad ? ad.getBoundingClientRect() : null;
  const ifr = document.querySelector('iframe[src*="maps/embed"]');
  const ri = ifr ? ifr.getBoundingClientRect() : null;
  return { address: ad ? { display: cs.display, visibility: cs.visibility, opacity: cs.opacity, height: r.height, top: r.top + scrollY, animation: cs.animationName, cls: ad.className } : null,
    map: ifr ? { top: ri.top + scrollY, left: ri.left, w: ri.width, h: ri.height, parentDisplay: getComputedStyle(ifr.parentElement).display } : null };
});
console.log(JSON.stringify(info));
await page.evaluate(() => { const i = document.querySelector('iframe[src*="maps/embed"]'); if (i) i.scrollIntoView({ block: 'center' }); });
await sleep(5000);
await page.screenshot({ path: `${H}/raw/_shots_fullsize/contact-us_map-viewport.png` });
await page.evaluate(() => window.scrollTo(0, 0));
await sleep(1500);
await page.screenshot({ path: `${H}/raw/_shots_fullsize/contact-us_desktop-1440_fullpage.png`, fullPage: true });
await browser.close();
