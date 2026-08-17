import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage({ viewport:{width:1366,height:900} });
await pg.route('**', r => r.request().url().startsWith('file:')?r.continue():r.abort());
await pg.goto('file:///home/claude/fonodia/site-build/index.html');
const r = await pg.evaluate(()=>{
  const it=document.querySelector('.vc_grid-item'); const cs=getComputedStyle(it);
  const zb=document.querySelector('.vc_gitem-zone-b'); const zcs=getComputedStyle(zb);
  const h3=document.querySelector('.vc_gitem-zone-b h3'); const hcs=getComputedStyle(h3);
  const wrap=document.querySelector('.vc_pageable-slide-wrapper');
  return {item:{w:cs.width,float:cs.float,display:cs.display,position:cs.position,clear:cs.clear}, wrapW:getComputedStyle(wrap).width, wrapDisplay:getComputedStyle(wrap).display,
    zb:{display:zcs.display,visibility:zcs.visibility,opacity:zcs.opacity,height:zcs.height,overflow:zcs.overflow, pos:zcs.position},
    h3:{color:hcs.color,display:hcs.display,visibility:hcs.visibility,opacity:hcs.opacity, rect:h3.getBoundingClientRect().toJSON()},
    parentClasses: it.parentElement.className, gridParent: document.querySelector('.vc_grid').className, gridDisplay:getComputedStyle(document.querySelector('.vc_grid')).display};
});
console.log(JSON.stringify(r,null,1));
await b.close();
