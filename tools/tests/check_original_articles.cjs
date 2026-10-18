/* Real original-article pages, after preview-pages.rb --layout original-article. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../..');
const preview = path.join(root, '.preview-build/pages');
const output = path.join(root, '.preview-build/longform');
const manifest = JSON.parse(fs.readFileSync(path.join(output, 'manifest.json'), 'utf8'));
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  for (const base of [preview, root]) {
    if (base === root && !name.startsWith('/assets/')) continue;
    let file = path.resolve(base, '.' + name);
    if (path.relative(base, file).startsWith('..')) continue;
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
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
  const browser = await chromium.launch({ headless: true, executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  const examples = ['jleague-pokemon', 'live-a-pokemon', 'model-study-part-2', 'kanto-trip', 'swsh-legendary-design-analysis-2', 'pla-first-reveal-frame-notes'];
  const targets = manifest.filter(post => examples.some(example => post.file.includes(example)));
  const checks = [], failures = [];
  const verify = (name, callback) => { try { callback(); } catch (error) { failures.push({ name, message: error.message }); } };
  const network = async route => {
    const url = new URL(route.request().url());
    if (url.origin === origin || url.protocol === 'data:') return route.continue();
    if (url.hostname === 'gallery.pokeamice.com') {
      // These are the existing archived originals, not substitute preview images.
      const local = path.join('P:/weibo/_work/cos', decodeURIComponent(path.basename(url.pathname)));
      if (fs.existsSync(local)) return route.fulfill({ status: 200, contentType: mime[path.extname(local)] || 'image/jpeg', body: fs.readFileSync(local) });
    }
    return route.abort();
  };
  try {
    for (const width of [1440, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 1000 }, reducedMotion: 'reduce' });
      await context.route('**/*', network);
      const page = await context.newPage();
      for (const post of targets) {
        await page.goto(origin + post.url, { waitUntil: 'load' });
        await page.waitForFunction(() => document.querySelectorAll('.original-image-link').length > 0);
        for (const theme of ['white', 'black']) {
          await page.evaluate(theme => {
            document.body.classList.remove('theme-bg-white', 'theme-bg-black');
            document.body.classList.add('theme-bg-' + theme);
          }, theme);
          await page.waitForTimeout(500); // Let the existing site's theme transition settle.
          const result = await page.evaluate(() => {
            const body = document.querySelector('[data-original-content]');
            const main = document.querySelector('[data-original-reader]');
            const rgb = value => (value.match(/[\d.]+/g) || []).slice(0, 3).map(Number);
            const luminance = value => rgb(value).map(x => { x /= 255; return x <= .04045 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); }).reduce((sum, x, i) => sum + x * [.2126, .7152, .0722][i], 0);
            const background = element => {
              for (let current = element; current; current = current.parentElement) {
                const color = getComputedStyle(current).backgroundColor;
                if (color !== 'transparent' && !color.endsWith(', 0)')) return color;
              }
              return 'rgb(255, 255, 255)';
            };
            const contrast = element => {
              const values = [luminance(getComputedStyle(element).color), luminance(background(element))].sort((a, b) => b - a);
              return (values[0] + .05) / (values[1] + .05);
            };
            const text = [...main.querySelectorAll('.original-head :is(h1,p), .original-byline :is(span,time,a), .original-toc a, .original-article__content :is(p,h2,h3,h4,figcaption,font,[style*="color:"]), .crumbs__link, .original-next a')].filter(el => el.checkVisibility() && el.textContent.trim());
            return { overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
              width: body.getBoundingClientRect().width, font: parseFloat(getComputedStyle(body).fontSize),
              contrast: text.map(contrast), lowContrast: text.filter(el => contrast(el) < 4.5).map(el => ({tag: el.tagName, class: el.className, text: el.textContent.slice(0, 28), color: getComputedStyle(el).color, background: background(el)})), h1: main.querySelectorAll('h1').length,
              badToc: [...main.querySelectorAll('.original-toc a')].filter(a => !document.getElementById(decodeURIComponent(a.hash.slice(1)))) .length,
              imageSizes: body.querySelectorAll('img[width][height]').length,
              tocOpen: main.querySelector('[data-original-toc]')?.open,
              outside: [...body.querySelectorAll('figure, p, .wbn-quote')].filter(el => el.getBoundingClientRect().right > innerWidth + 1).length };
          });
          checks.push({ viewport: width, theme, post: post.file, ...result });
          verify(`${width} ${theme} ${post.file}`, () => {
            assert.ok(result.overflow <= 1, `overflow ${result.overflow}`);
            assert.ok(result.width <= 745); assert.ok(result.font >= 17);
            assert.equal(result.h1, 1); assert.equal(result.badToc, 0); assert.equal(result.outside, 0);
            assert.ok(result.contrast.every(value => value >= 4.5), `contrast ${Math.min(...result.contrast)}`);
            assert.ok(result.imageSizes > 0);
            if (result.tocOpen !== undefined) assert.equal(result.tocOpen, width > 1050);
          });
        }
      }

      const featured = targets.find(post => post.file.includes('jleague'));
      await page.goto(origin + featured.url, { waitUntil: 'load' });
      await page.waitForFunction(() => document.querySelector('.original-image-link img')?.complete);
      await page.screenshot({ path: path.join(output, `reader-${width}.png`), animations: 'disabled' });
      await page.evaluate(() => { document.body.classList.remove('theme-bg-white'); document.body.classList.add('theme-bg-black'); });
      await page.screenshot({ path: path.join(output, `reader-${width}-night.png`), animations: 'disabled' });
      await page.evaluate(() => { document.body.classList.remove('theme-bg-black'); document.body.classList.add('theme-bg-white'); });
      const toc = page.locator('[data-original-toc]');
      if (width <= 1050) await toc.locator('summary').click();
      const chapter = toc.locator('a').nth(2);
      const chapterHash = await chapter.getAttribute('href');
      await chapter.click();
      verify(`${width} chapter navigation`, () => assert.equal(new URL(page.url()).hash, chapterHash));
      if (width <= 1050) assert.equal(await toc.evaluate(el => el.open), false);
      await page.waitForTimeout(80);
      assert.ok(await page.locator('[data-original-percent]').textContent());
      const image = page.locator('.original-image-link').first();
      await image.scrollIntoViewIfNeeded();
      await image.focus();
      await page.keyboard.press('Enter');
      const dialog = page.locator('[data-original-viewer]');
      await dialog.waitFor({ state: 'visible' });
      await page.waitForFunction(() => document.querySelector('[data-original-full-image]').complete && !document.querySelector('[data-original-full-image]').hidden);
      if (width === 390) await page.screenshot({ path: path.join(output, 'image-viewer-mobile.png'), animations: 'disabled' });
      await page.keyboard.press('ArrowRight');
      assert.match(await page.locator('[data-original-image-caption]').textContent(), /^2 \/ /);
      await page.evaluate(() => { document.querySelector('[data-original-full-image]').src = '/missing-original-for-check.jpg'; });
      await page.waitForFunction(() => document.querySelector('[data-original-image-status]').textContent.includes('暂时无法载入'));
      assert.ok(await page.locator('[data-original-image-source]').getAttribute('href'));
      await page.keyboard.press('Escape');
      assert.equal(await image.evaluate(el => el === document.activeElement), true);
      await context.close();
    }

    const noScript = await browser.newContext({ viewport: { width: 390, height: 1000 }, javaScriptEnabled: false });
    await noScript.route('**/*', network);
    const page = await noScript.newPage();
    await page.goto(origin + targets[0].url, { waitUntil: 'load' });
    assert.ok(await page.locator('[data-original-content]').innerText());
    await page.locator('[data-original-toc] summary').click();
    assert.ok(await page.locator('[data-original-toc] a').count());
    await page.locator('[data-original-toc] a').first().click();
    assert.ok(new URL(page.url()).hash);
    await noScript.close();
    fs.writeFileSync(path.join(output, 'browser-checks.json'), JSON.stringify({ checks, failures }, null, 2));
    console.log(`${checks.length} responsive/theme checks; ${failures.length} failures; navigation, image keyboard controls and no-script reading checked.`);
    if (failures.length) { console.log(JSON.stringify(failures, null, 2)); process.exitCode = 1; }
  } finally { await browser.close(); server.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; server.close(); });
