import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { preview } from './preview.mjs';
const server=preview(0);
await new Promise(r=>server.on('listening',r));
const base=`http://127.0.0.1:${server.address().port}/ns-designer/`;
let browser;
try {
 browser=await chromium.launch({args:['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const viewport of [{width:1440,height:1000},{width:390,height:844}]) {
  await page.setViewportSize(viewport);
  await page.goto(base);
  assert.equal(await page.locator('nav.toc a').count(),11);
  assert(await page.locator('#readiness').innerText().then(t=>t.includes('not a validated build kit')));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth+1),'Page overflows viewport');
  await page.locator('[data-cw="chalk"]').click();
  assert((await page.locator('#hero-shot').getAttribute('src')).endsWith('hero-chalk.png'));
  await page.locator('nav a[href="#readiness"]').click();
  assert(new URL(page.url()).hash==='#readiness');
 }
 for(const variant of ['', '?case=enclosed']) {
  await page.goto(base);
  await page.locator(`[data-load="${variant}"]`).click();
  const frame=page.frameLocator('#viewer iframe');
  await frame.locator('.stage').waitFor();
  await page.waitForFunction(()=>document.querySelector('#viewer iframe')?.contentWindow?.keeb?.ready(),null,{timeout:60000});
 }
 assert.deepEqual(errors,[],'Browser JavaScript errors');
 // A blocked module/CDN must leave usable static navigation, even before module code can execute.
 const offline=await browser.newPage();
 await offline.route('https://cdn.jsdelivr.net/**',route=>route.abort());
 await offline.goto(base+'viewer/index.html');
 await offline.locator('#viewer-fallback a').waitFor({state:'visible'});
 await offline.locator('#viewer-fallback a').click();
 assert.equal(new URL(offline.url()).hash,'#model');
 // A failed binary request should show a useful message and retain fallback.
 const missing=await browser.newPage();
 await missing.route('**/*.glb',route=>route.fulfill({status:404,body:'Missing'}));
 await missing.goto(base+'viewer/index.html');
 await missing.getByText('The model file could not be loaded.',{exact:false}).waitFor();
 assert(await missing.locator('#viewer-fallback a').isVisible());
 console.log('Browser checks passed: desktop/mobile, navigation, colorway, both models, CDN and model failure fallbacks.');
} finally {await browser?.close();await new Promise(r=>server.close(r));}
