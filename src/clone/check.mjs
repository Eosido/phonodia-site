import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport:{width:1280,height:1000} });
const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
await p.route('**', r => { const u=r.request().url(); if(u.startsWith('file:')) r.continue(); else r.abort(); });
await p.goto('file:///home/claude/fonodia/clone/fonodia-klonos.html');
await p.waitForTimeout(600);
const stat = await p.evaluate(()=>({
  navItems:document.querySelectorAll('nav a').length,
  events:document.querySelectorAll('.ev').length,
  members:document.querySelectorAll('#meli figure.m').length,
  videos:document.querySelectorAll('.vd').length,
  albums:document.querySelectorAll('.alb').length,
  products:document.querySelectorAll('.pr').length,
  quotes:document.querySelectorAll('blockquote').length,
  imgs:document.querySelectorAll('img').length,
  h1:document.querySelector('h1').textContent,
  sections:[...document.querySelectorAll('section.s h2')].map(h=>h.textContent)
}));
console.log(JSON.stringify(stat,null,1));
await p.click('.lang button[data-l="en"]'); await p.waitForTimeout(300);
console.log('EN h1:', await p.$eval('h1',e=>e.textContent));
console.log('EN sections:', await p.$$eval('section.s h2',ns=>ns.map(n=>n.textContent).join(' | ')));
console.log('EN first quote name:', await p.$eval('blockquote h3',e=>e.textContent));
console.log('EN about first p:', (await p.$eval('#ligalogia .two div:nth-child(2) p',e=>e.textContent)).slice(0,90));
await p.click('.lang button[data-l="el"]'); await p.waitForTimeout(200);
console.log('EL back h1:', await p.$eval('h1',e=>e.textContent));
console.log('pageerrors:', errs);
await b.close();
