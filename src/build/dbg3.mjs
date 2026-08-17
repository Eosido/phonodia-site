import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage({ viewport:{width:1366,height:900} });
await pg.route('**', r => r.request().url().startsWith('file:')?r.continue():r.abort());
const cdp = await pg.context().newCDPSession(pg);
await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
await pg.goto('file:///home/claude/fonodia/site-build/index.html');
async function who(sel){
  const doc = await cdp.send('DOM.getDocument',{depth:-1});
  const {nodeId} = await cdp.send('DOM.querySelector',{nodeId:doc.root.nodeId, selector:sel});
  const m = await cdp.send('CSS.getMatchedStylesForNode',{nodeId});
  const out=[];
  for (const r of m.matchedCSSRules){ const txt=r.rule.style.cssText||''; if(/(^|;)\s*color:/.test(txt)) out.push([r.rule.selectorList.text.slice(0,120), txt.match(/(^|;)\s*color:[^;]+/)[0], r.rule.origin]); }
  return out;
}
console.log('HOME h3:', JSON.stringify(await who('.vc_custom_1745437792156 h3'),null,1)); console.log('HOME p:', JSON.stringify(await who('.vc_custom_1745437792156 p'),null,1));
await pg.goto('file:///home/claude/fonodia/site-build/μέλη/index.html');
console.log('MEMBERS h3:', JSON.stringify(await who('h3.artist_title'),null,1));
await b.close();
