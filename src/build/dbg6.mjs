import { chromium } from 'playwright';
import fs from 'fs';
const ph=fs.readFileSync('/tmp/ph.jpg');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage({ viewport:{width:1366,height:900} });
await pg.route('**', r => { const u=r.request().url(); if(u.startsWith('file:')) return r.continue(); if(/\.jpe?g/i.test(u)) return r.fulfill({body:ph,contentType:'image/jpeg'}); return r.abort();});
await pg.goto('file:///home/claude/fonodia/site-build/contact-2/index.html'); await pg.waitForTimeout(500);
console.log(await pg.evaluate(()=>{
  const c=document.querySelector('.canvas_image'); const cs=getComputedStyle(c);
  const w=document.getElementById('lc_swp_wrapper'); const ws=getComputedStyle(w);
  return {canvas:{z:cs.zIndex,pos:cs.position,disp:cs.display,w:c.getBoundingClientRect().width,h:c.getBoundingClientRect().height,top:c.getBoundingClientRect().top,bgsize:cs.backgroundSize,bgpos:cs.backgroundPosition,clip:cs.clipPath,ovl:(function(){const o=document.querySelector('.canvas_overlay');const s=getComputedStyle(o);return s.backgroundColor+' z'+s.zIndex+' h'+o.getBoundingClientRect().height})(),op:cs.opacity,vis:cs.visibility,bg:cs.backgroundImage.slice(0,50)},
          wrapper:{z:ws.zIndex,pos:ws.position,bg:ws.backgroundColor,op:ws.opacity,transform:ws.transform,filter:ws.filter},
          bodyBg:getComputedStyle(document.body).backgroundColor, htmlBg:getComputedStyle(document.documentElement).backgroundColor,
          topAt:document.elementsFromPoint(60,300).map(e=>e.tagName+'#'+e.id+'.'+String(e.className).slice(0,30)+' bg='+getComputedStyle(e).backgroundColor)};
}));
await b.close();
