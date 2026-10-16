/* Browser QA / local preview for real Jekyll timeline routes. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../..');
const preview = path.join(root, '.preview-build/timeline');
const manifest = JSON.parse(fs.readFileSync(path.join(preview, 'manifest.json'), 'utf8'));
const mime = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.gif':'image/gif','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2'};
const server = http.createServer((req, res) => {
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); }
  catch { res.writeHead(400).end(); return; }
  if (manifest.baseurl && pathname.startsWith(manifest.baseurl + '/')) pathname = pathname.slice(manifest.baseurl.length);
  if (pathname === '/') { res.writeHead(302, {Location:'/timeline/'}).end(); return; }
  for (const base of [preview, root]) {
    if (base === root && !pathname.startsWith('/assets/')) continue;
    let file = path.resolve(base, '.' + pathname);
    const relative = path.relative(base, file);
    if (relative.startsWith('..') || path.isAbsolute(relative)) continue;
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (fs.existsSync(file) && fs.statSync(file).isFile()) {
      res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
      fs.createReadStream(file).pipe(res); return;
    }
  }
  res.writeHead(404, {'Content-Type':'text/plain; charset=utf-8'}).end('此本地预览只生成时间轴页面；文章、人物与制作名单链接在正式构建中提供。');
});

(async () => {
  const serving = process.argv.includes('--serve');
  await new Promise(resolve => server.listen(serving ? 8763 : 0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  if (serving) { console.log(`Timeline preview: ${origin}/timeline/`); return; }
  const browser = await chromium.launch({headless:true, executablePath:process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const checks = [], failures = [];
  const check = (name, fn) => { try { fn(); } catch (error) { failures.push({name, error:error.message}); } };
  const shots = path.join(preview, 'screenshots');
  fs.mkdirSync(shots, {recursive:true});
  try {
    for (const width of [1440, 1024, 390, 320]) {
      const context = await browser.newContext({viewport:{width, height:1000}, reducedMotion:'reduce'});
      await context.route('**/*', route => route.request().url().startsWith(origin) || route.request().url().startsWith('data:') ? route.continue() : route.abort());
      const page = await context.newPage();
      for (const route of manifest.routes) {
        await page.goto(origin + route, {waitUntil:'load'});
        for (const theme of ['white', 'black']) {
          await page.evaluate(theme => { document.body.classList.remove('theme-bg-white', 'theme-bg-black'); document.body.classList.add('theme-bg-' + theme); }, theme);
          const result = await page.evaluate(() => {
            const root = document.querySelector('[data-tl-root]');
            const title = root.querySelector('.tl-entry__title a, .tl-feature strong');
            const rgb = value => value.match(/[\d.]+/g)?.slice(0,3).map(Number);
            const lum = value => rgb(value).map(x => { x /= 255; return x <= .04045 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); }).reduce((sum,x,i) => sum + x * [.2126,.7152,.0722][i], 0);
            const contrast = element => {
              const bg = getComputedStyle(document.querySelector('.initial-content')).backgroundColor;
              const ls = [lum(getComputedStyle(element).color), lum(bg)].sort((a,b) => b-a);
              return (ls[0]+.05)/(ls[1]+.05);
            };
            return {ready:root.classList.contains('is-ready'), overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
              titleFont:title ? parseFloat(getComputedStyle(title).fontSize) : null,
              contrast:[...root.querySelectorAll('.tl-eyebrow, .tl-entry__title a, .tl-entry__summary, .tl-entry__meta, .tl-search label, .tl-year-picker label, .tl-result-status')].filter(el => el.getClientRects().length).slice(0,18).map(contrast),
              badBar:[...root.querySelectorAll('.tl-column i')].some(el => el.getBoundingClientRect().height > el.parentElement.getBoundingClientRect().height + 1)};
          });
          checks.push({route,width,theme,...result});
          check(`${route} ${width} ${theme}`, () => {
            assert.equal(result.ready,true);
            assert.ok(result.overflow <= 1, `overflow: ${result.overflow}px`);
            if (result.titleFont !== null) assert.ok(result.titleFont >= 15);
            assert.ok(result.contrast.every(c => c >= 4.5), `contrast: ${result.contrast.join(', ')}`);
            assert.equal(result.badBar,false);
          });
        }
      }
      for (const year of [2006, 2017, 2026]) {
        await page.goto(`${origin}/timeline/${year}/`);
        assert.equal(await page.locator('[data-tl-nav-tools]').evaluate(el => el.open),width > 760);
        if (width <= 760) assert.equal(await page.locator('.tl--year .tl-side__label').isVisible(),false);
        const kinds = await page.locator('[data-tl-filter]').evaluateAll(nodes => nodes.map(node => node.dataset.tlFilter));
        for (const kind of kinds) {
          await page.locator(`[data-tl-filter="${kind}"]`).click();
          const stats = await page.evaluate(() => {
            const items = [...document.querySelectorAll('.tl--year .tl-item')];
            const kind = document.querySelector('[data-tl-filter].is-on').dataset.tlFilter;
            return {kind, pressed:document.querySelector('[data-tl-filter].is-on').getAttribute('aria-pressed'),
              mismatches:items.filter(item => item.hidden === (kind === 'all' || item.dataset.kind === kind)).length,
              brokenMonths:[...document.querySelectorAll('[data-tl-month]')].some(month => {
                const n = month.querySelectorAll('.tl-item:not([hidden])').length;
                const link = document.querySelector(`[data-tl-month-link="${month.id}"]`);
                return month.hidden !== (n===0) || link.hidden !== (n===0) || Number(month.querySelector('[data-tl-count]').textContent) !== n;
              })};
          });
          check(`filter ${year} ${width} ${kind}`, () => { assert.equal(stats.pressed,'true'); assert.equal(stats.mismatches,0); assert.equal(stats.brokenMonths,false); });
        }
        await page.locator('[data-tl-filter="all"]').click();
        await page.locator('[data-tl-query]').fill('不存在的资料__QA');
        check(`empty ${year} ${width}`, () => {});
        assert.equal(await page.locator('[data-tl-empty]').isVisible(), true);
        assert.equal(await page.locator('.tl--year .tl-item:not([hidden])').count(), 0);
        await page.locator('[data-tl-reset]').click();
        assert.equal(await page.locator('[data-tl-empty]').isVisible(), false);
        assert.equal(await page.locator('[data-tl-query]').inputValue(), '');
        const text = await page.locator('.tl-entry__title').first().textContent();
        await page.locator('[data-tl-query]').fill(text.trim().slice(0,5));
        assert.ok(await page.locator('.tl-entry:not([hidden])').count() > 0);
        await page.locator('[data-tl-clear-query]').click();
      }
      await page.goto(`${origin}/timeline/2006/?k=scan&q=CONTINUE`);
      assert.equal(await page.locator('[data-tl-filter="scan"]').getAttribute('aria-pressed'),'true');
      assert.equal(await page.locator('[data-tl-query]').inputValue(),'CONTINUE');
      await page.locator('[data-tl-filter="all"]').click();
      await page.locator('[data-tl-clear-query]').click();
      if (width <= 760) await page.locator('[data-tl-nav-tools] > summary').click();
      await page.locator('[data-tl-year-select]').selectOption('/timeline/2000/');
      await Promise.all([page.waitForURL('**/timeline/2000/'),page.locator('[data-tl-year-picker] button').click()]);
      assert.equal(await page.locator('[data-tl-year]').getAttribute('data-tl-year'),'2000');
      await page.goto(origin + '/timeline/');
      await Promise.all([page.waitForURL('**/*interview-time-satoshi-tajiri-ultimate-game-freak/'),page.locator('.tl-feature').click()]);
      assert.equal(await page.locator('main[data-interview-template]').getAttribute('data-interview-template'),'longform');
      for (const [label, route, selector] of [
        ['overview','/timeline/',null], ['era','/timeline/','#era-2'],
        ['year','/timeline/2006/',null], ['entries','/timeline/2006/','[data-tl-month]'],
        ['blogs','/timeline/2017/','[data-tl-streams]']]) {
        await page.goto(origin + route);
        if (label === 'blogs') await page.locator('[data-tl-filter="stream"]').click();
        if (selector) await page.locator(selector).first().scrollIntoViewIfNeeded();
        await page.evaluate(async () => {
          const imgs = [...document.querySelectorAll('[data-tl-root] img')];
          imgs.forEach(img => { img.loading = 'eager'; });
          await Promise.all(imgs.map(img => img.decode().catch(() => {})));
        });
        await page.screenshot({path:path.join(shots, `${label}-${width}.png`)});
        if (label === 'year' && width === 1440) {
          await page.evaluate(() => { document.body.classList.replace('theme-bg-white','theme-bg-black'); });
          await page.screenshot({path:path.join(shots,'year-dark-1440.png')});
        }
      }
      await context.close();
    }
    const context = await browser.newContext({javaScriptEnabled:false, viewport:{width:390,height:1000}});
    await context.route('**/*', route => route.request().url().startsWith(origin) ? route.continue() : route.abort());
    const page = await context.newPage();
    await page.goto(`${origin}/timeline/2017/?k=scan`);
    const expected = manifest.years['2017'];
    assert.equal(await page.locator('.tl--year .tl-item').count(),expected.docs+expected.stream);
    assert.equal(await page.locator('.tl-toolbar').isVisible(),false);
    assert.ok(await page.locator('[data-tl-month] a').count() > 0);
    await context.close();
  } catch (error) { failures.push({name:'interaction/no-JS suite',error:error.stack}); }
  finally { await browser.close(); server.close(); }
  fs.writeFileSync(path.join(preview,'browser-checks.json'),JSON.stringify({checks,failures},null,2));
  console.log(JSON.stringify({cases:checks.length,failures,screenshots:shots},null,2));
  if (failures.length) process.exitCode=1;
})();
