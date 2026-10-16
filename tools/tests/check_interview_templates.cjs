/* Local browser QA against real Jekyll output. Requires Playwright (NODE_PATH
   may point at the bundled runtime); no external requests or content writes. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '../..');
const preview = path.resolve(process.argv.slice(2).find(arg => !arg.startsWith('--')) || path.join(root, '.preview-build/interview-templates'));
const manifest = JSON.parse(fs.readFileSync(path.join(preview, 'manifest.json'), 'utf8'));
const mime = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.gif':'image/gif','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2'};
const server = http.createServer((req, res) => {
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); }
  catch { res.writeHead(400).end(); return; }
  if (manifest.baseurl && pathname.startsWith(manifest.baseurl + '/')) pathname = pathname.slice(manifest.baseurl.length);
  for (const base of [preview, root]) {
    if (base === root && !pathname.startsWith('/assets/')) continue;
    const file = path.resolve(base, '.' + pathname);
    const relative = path.relative(base, file);
    if (relative.startsWith('..') || path.isAbsolute(relative)) continue;
    if (fs.existsSync(file) && fs.statSync(file).isFile()) {
      res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
      fs.createReadStream(file).pipe(res); return;
    }
  }
  res.writeHead(404).end();
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  if (process.argv.includes('--serve')) {
    console.log(`Template preview: ${origin}/index.html`);
    return;
  }
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  const failures = [];
  const checks = [];
  try {
    for (const width of [1440, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 }, reducedMotion: 'reduce' });
      await context.route('**/*', route => {
        const url = route.request().url();
        if (url.startsWith(origin) || url.startsWith('data:')) return route.continue();
        return route.abort();
      });
      const page = await context.newPage();
      for (const [form] of Object.entries(manifest.examples)) {
        await page.goto(`${origin}/${form}.html`, {waitUntil: 'load'});
        await page.evaluate(() => document.fonts.ready);
        // Eager only in QA: lazy images can otherwise leave a white frame in
        // a screenshot taken immediately after scrolling to a dialogue turn.
        await page.evaluate(async () => {
          const images = [...document.querySelectorAll('main img[src]')];
          images.forEach(img => { img.loading = 'eager'; });
          await Promise.all(images.map(img => img.decode().catch(() => {})));
        });
        const tools = page.locator('.ed-tools');
        const setToolsOpen = async () => { if (!await tools.getAttribute('open').then(x => x !== null)) await tools.locator('summary').click(); };
        const views = await page.locator('[data-view-choice]').count() ? ['translation', 'parallel', 'original'] : ['translation'];
        for (const view of views) {
          await setToolsOpen();
          if (views.length > 1) await page.locator(`[data-view-choice="${view}"]`).click();
          for (const theme of ['auto', 'dark', 'clean']) {
            await page.locator(`[data-theme-choice="${theme}"]`).click();
            const result = await page.evaluate(() => {
              const root = document.querySelector('main[data-interview-template]');
              const turn = root.querySelector('.ed-turn');
              const original = root.querySelector('.parallel-text__cell--original');
              const text = root.querySelector('.ed-trans');
              const themeButton = root.querySelector('[data-theme-choice].is-active');
              const rgb = value => value.match(/[\d.]+/g)?.slice(0, 3).map(Number);
              const luminance = value => rgb(value).map(x => {x /= 255; return x <= .04045 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4);}).reduce((sum, x, i) => sum + x * [.2126, .7152, .0722][i], 0);
              const contrast = element => {
                let bg = 'rgb(255,255,255)';
                for (let node = element; node; node = node.parentElement) {
                  const color = getComputedStyle(node).backgroundColor;
                  if (!color.endsWith(', 0)') && color !== 'transparent') { bg = color; break; }
                }
                const l = [luminance(getComputedStyle(element).color), luminance(bg)].sort((a,b) => b-a);
                return (l[0] + .05) / (l[1] + .05);
              };
              const speakerContrast = [...root.querySelectorAll('.ed-turn__who')].filter(el => el.getClientRects().length).slice(0, 5).map(contrast);
              return { form: root.dataset.interviewTemplate, view: root.dataset.view,
                overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                originalOpen: original?.hasAttribute('open'),
                border: turn ? getComputedStyle(turn).borderTopWidth : null,
                font: text ? parseFloat(getComputedStyle(text).fontSize) : null,
                themePressed: themeButton?.getAttribute('aria-pressed'), speakerContrast };
            });
            checks.push({form, width, view, theme, ...result});
            try {
              assert.equal(result.form, manifest.expected_forms?.[form] || form);
              assert.equal(result.view, view);
              assert.ok(result.overflow <= 1, `horizontal overflow ${result.overflow}px`);
              if (result.originalOpen !== undefined) assert.equal(result.originalOpen, view !== 'translation');
              if (result.border !== null) assert.equal(result.border, '0px', 'paragraph must not be a card');
              if (result.font !== null) assert.ok(result.font >= 15, `small body type: ${result.font}px`);
              assert.equal(result.themePressed, 'true');
              assert.ok(result.speakerContrast.every(c => c >= 4.5), `low speaker-name contrast: ${result.speakerContrast.join(', ')}`);
            } catch (error) { failures.push({form, width, view, theme, error: error.message}); }
          }
        }
        if (views.length > 1) await page.locator('[data-view-choice="translation"]').click();
        await page.locator('[data-theme-choice="auto"]').click();
        const chips = page.locator('.parallel-cast-chip');
        if (await chips.count()) {
          await chips.first().click();
          assert.equal(await chips.first().getAttribute('aria-pressed'), 'true');
          assert.ok(await page.locator('.parallel-text').evaluate(el => el.classList.contains('is-filtering')));
          await chips.first().click();
        }
        await tools.locator('summary').click();
        const note = page.locator('[data-note-toggle]').first();
        if (await note.count() && await note.isVisible()) {
          await note.click();
          assert.equal(await note.getAttribute('aria-expanded'), 'true');
          await note.click();
        }
        if (width !== 320) {
          await page.evaluate(() => window.scrollTo(0, 0));
          await page.screenshot({path: path.join(preview, `${form}-${width}.png`)});
          await page.evaluate(() => window.scrollTo(0, document.querySelector('#parallel-reading').getBoundingClientRect().top + window.scrollY - 24));
          await page.screenshot({path: path.join(preview, `${form}-body-${width}.png`)});
          if ((manifest.expected_forms?.[form] || form) === 'roundtable') {
            await page.locator('.ed-turn[data-speaker]').first().scrollIntoViewIfNeeded();
            await page.screenshot({path: path.join(preview, `${form}-dialogue-${width}.png`)});
          }
          if (form === 'annotated') {
            await page.locator('.ed-turn--commentary').first().scrollIntoViewIfNeeded();
            await page.screenshot({path: path.join(preview, `${form}-commentary-${width}.png`)});
          }
        }
        console.log(`Checked ${form} at ${width}px`);
      }
      await context.close();
    }
    fs.writeFileSync(path.join(preview, 'browser-checks.json'), JSON.stringify({cases: checks.length, failures, checks}, null, 2));
    console.log(JSON.stringify({cases: checks.length, failures: failures.slice(0, 20)}, null, 2));
    if (failures.length) process.exitCode = 1;
  } finally { await browser.close(); server.close(); }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
