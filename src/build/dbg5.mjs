import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage({ viewport:{width:1366,height:900} });
await pg.route('**', r => r.request().url().startsWith('file:')?r.continue():r.abort());
await pg.goto('file:///home/claude/fonodia/site-build/contact-2/index.html');
console.log(await pg.evaluate(()=>{const c=document.querySelector('.canvas_image'); if(!c) return 'NO CANVAS'; const cs=getComputedStyle(c); const r=c.getBoundingClientRect();
 return {display:cs.display,pos:cs.position,z:cs.zIndex,w:r.width,h:r.height,bg:cs.backgroundImage.slice(0,80),bodyBg:getComputedStyle(document.body).backgroundColor,htmlBg:getComputedStyle(document.documentElement).backgroundColor,bodyClass:document.body.className.slice(-40)}}));
await b.close();
