import { chromium } from 'playwright';
import fs from 'fs';
const vid=fs.readFileSync('/tmp/vid.jpg'), ph=fs.readFileSync('/tmp/ph.jpg'), php=fs.readFileSync('/tmp/ph.png');
const root='/home/claude/fonodia/site-build/';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage({ viewport:{width:1900,height:1000} });
await pg.route('**', r=>{const u=r.request().url();
  if(u.startsWith('file:')) return r.continue();
  if(/\.mp4/.test(u)) return r.fulfill({body:vid,contentType:'image/jpeg'});
  if(/\.png/i.test(u)) return r.fulfill({body:php,contentType:'image/png'});
  if(/\.(jpe?g|webp)/i.test(u)) return r.fulfill({body:ph,contentType:'image/jpeg'});
  return r.abort();});
// crawl every internal link from home, 2 levels
const seen=new Set(); const queue=['index.html']; const bad=[];
while(queue.length){
  const rel=queue.shift(); if(seen.has(rel)) continue; seen.add(rel);
  const url='file://'+root+rel;
  const resp=await pg.goto(url,{waitUntil:'load'}).catch(e=>null);
  if(!resp){ bad.push([rel,'LOAD FAIL']); continue; }
  const info=await pg.evaluate(()=>{
    const probe=document.createElement('div'); probe.className='lc_swp_boxed'; document.body.appendChild(probe);
    const cssOk = getComputedStyle(probe).maxWidth==='1200px'; probe.remove();
    const links=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).filter(h=>h&&!/^(https?:|mailto:|#)/.test(h));
    const hero=document.getElementById('hero');
    return {cssOk, links, title:document.title,
      hero: hero? {w:hero.getBoundingClientRect().width, pos:getComputedStyle(hero).position}:null,
      headerFixed: getComputedStyle(document.getElementById('lc_page_header')).position};
  });
  if(!info.cssOk) bad.push([rel,'NO CSS']);
  const dir=rel.includes('/')?rel.slice(0,rel.lastIndexOf('/')+1):'';
  for(const l of info.links){
    let t=new URL(l, 'http://x/'+dir).pathname.slice(1);
    const disk=decodeURIComponent(t);
    if(t.endsWith('index.html') && fs.existsSync(root+disk)) { if(!seen.has(t)) queue.push(t); }
    else if(t.endsWith('index.html')) bad.push([rel,'BROKEN LINK -> '+disk]);
  }
}
console.log('pages visited:', seen.size);
console.log('problems:', bad.length); bad.slice(0,20).forEach(x=>console.log('  ',x.join(' | ')));
await b.close();
