"""Verify offered fonts with their existing hosted font assets, without a fallback-only pass."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright,expect
with sync_playwright() as p:
    browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');ctx.route('**/api/activity/page-view',lambda r:r.fulfill(json={'ok':True}));q=ctx.new_page();q.goto('http://127.0.0.1:5016/qa-session/owner',wait_until='domcontentloaded');q.goto('http://127.0.0.1:5016/income',wait_until='domcontentloaded');expect(q.locator('html')).to_have_attribute('data-sage-style-mode','desktop');families=q.locator('[data-font-choice]').evaluate_all('''es=>es.map(e=>{document.documentElement.dataset.font=e.dataset.fontChoice;return [e.dataset.fontChoice,getComputedStyle(document.querySelector('.income-kpi-grid strong')).fontFamily.split(',')[0].replace(/[\"\']/g,'').trim()]})''');loaded=q.evaluate('''async families=>Promise.all(families.map(async([id,name])=>{try{const faces=await Promise.race([document.fonts.load('700 16px "'+name+'"'),new Promise((_,reject)=>setTimeout(()=>reject(Error('Font request timed out')),18000))]);return{id,name,loaded:faces.length>0&&faces.every(f=>f.status==='loaded')}}catch(e){return{id,name,loaded:false,error:e.message}}}))''',families);cases=[]
    for width in [1024,1440]:
        q.set_viewport_size({'width':width,'height':900})
        for font in loaded:
            for size in ['small','medium','large']:
                q.evaluate('([f,s])=>{document.documentElement.dataset.font=f;document.documentElement.dataset.fontSize=s}',[font['id'],size]);bad=q.locator('.income-kpi-grid strong,.income-insight-grid strong').evaluate_all('(es)=>es.filter(e=>e.getClientRects().length&&e.scrollWidth>e.clientWidth+2).map(e=>e.textContent)');cases.append({'width':width,'font':font['id'],'size':size,'bad':bad})
    q.screenshot(path=str(ROOT/'.qa/desktop/hosted-font-income-1440.png'));browser.close()
result={'fonts':loaded,'cases':cases};(ROOT/'.qa/desktop/hosted-fonts.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'fonts':loaded,'cases':len(cases),'failures':[x for x in cases if x['bad']]}));sys.exit(1 if any(x['bad'] for x in cases) else 0)
