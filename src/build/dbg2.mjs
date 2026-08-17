import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage({ viewport:{width:1366,height:900} });
await pg.route('**', r => r.request().url().startsWith('file:')?r.continue():r.abort());
await pg.goto('file:///home/claude/fonodia/site-build/μέλη/index.html');
const r = await pg.evaluate(()=>{
  const h=document.querySelectorAll('h3.artist_title')[1]; const cs=getComputedStyle(h);
  const t=[...document.querySelectorAll('h3')].find(x=>x.textContent.trim()==='Μέλη'); const tcs=getComputedStyle(t);
  const it=h.closest('.single_artist_item'); const ics=getComputedStyle(it);
  return {h3:{color:cs.color,opacity:cs.opacity,visibility:cs.visibility,display:cs.display,fontSize:cs.fontSize,rect:h.getBoundingClientRect().toJSON()}, a:getComputedStyle(h.parentElement).color, item:{h:ics.height,overflow:ics.overflow,mb:ics.marginBottom},
   title:{color:tcs.color,opacity:tcs.opacity,rect:t.getBoundingClientRect().toJSON(),parent:t.parentElement.parentElement.className}, wrapOpacity:getComputedStyle(t.closest('.wpb_text_column')).opacity};
});
console.log(JSON.stringify(r,null,1)); await b.close();
