import { chromium } from 'playwright';
import fs from 'fs';
const vid=fs.readFileSync('/tmp/vid.jpg'), ph=fs.readFileSync('/tmp/ph.jpg'), php=fs.readFileSync('/tmp/ph.png');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
for (const p of process.argv.slice(2)) {
  const [file,out,w]=p.split('::');
  const pg = await b.newPage({ viewport:{width:parseInt(w||'1900'),height:1000} });
  await pg.route('**', r=>{const u=r.request().url();
    if(u.startsWith('file:')) return r.continue();
    if(/\.mp4/.test(u)) return r.fulfill({body:vid,contentType:'image/jpeg'});
    if(/\.png/i.test(u)) return r.fulfill({body:php,contentType:'image/png'});
    if(/\.(jpe?g|webp)/i.test(u)) return r.fulfill({body:ph,contentType:'image/jpeg'});
    return r.abort();});
  await pg.goto('file://'+file,{waitUntil:'load'}); await pg.waitForTimeout(400);
  const info = await pg.evaluate(()=>{const h=document.getElementById('hero'); if(!h) return null; const r=h.getBoundingClientRect(); const cs=getComputedStyle(h);
    const v=h.querySelector('video'); return {hero:{w:r.width,x:r.x,pos:cs.position,disp:cs.display,bg:cs.backgroundColor}, video: v?{rect:v.getBoundingClientRect().toJSON(),pos:getComputedStyle(v).position}:null, bodyBg:getComputedStyle(document.body).backgroundColor};});
  console.log(out, JSON.stringify(info));
  await pg.screenshot({path:out}); await pg.close();
}
await b.close();
