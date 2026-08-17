import { chromium } from 'playwright';
import fs from 'fs';
const ph=fs.readFileSync('/tmp/ph.jpg'), phw=fs.readFileSync('/tmp/ph-wide.jpg'), php=fs.readFileSync('/tmp/ph.png');
const pages = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
for (const p of pages) {
  const [file, out, w] = p.split('::');
  const pg = await b.newPage({ viewport:{width: parseInt(w||'1366'), height:900} });
  const errs=[]; pg.on('pageerror',e=>errs.push(String(e)));
  await pg.route('**', r => { const u=r.request().url();
    if(u.startsWith('file:')) return r.continue();
    if(/\.(png)(\?|$)/i.test(u)) return r.fulfill({body:php,contentType:'image/png'});
    if(/\.(jpe?g|webp)(\?|$)/i.test(u)) return r.fulfill({body:/1024x683|768x512|-\d{3,4}x\d{3}\.jpg/.test(u)&&!/819x1024|724x1024|609x1024/.test(u)?phw:ph,contentType:'image/jpeg'});
    return r.abort(); });
  await pg.goto('file://'+file, {waitUntil:'load'});
  await pg.waitForTimeout(400);
  await pg.screenshot({path: out, fullPage: true});
  console.log(out, 'errors:', errs.slice(0,3));
  await pg.close();
}
await b.close();
