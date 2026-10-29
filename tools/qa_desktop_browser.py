"""Desktop before/after capture and protected mobile geometry checks."""
import argparse,json,sys,time
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright,expect
BASE='http://127.0.0.1:5016';OUT=ROOT/'.qa/desktop';OUT.mkdir(exist_ok=True)
PAGES='dashboard requests income expenses finance debtors imprest daily_close workspace catalog operations fulfillment procurement inventory assets events stock customers suppliers branches departments staff reports audit payroll analytics bills compliance business_reports settings'.split()
WIDTHS=[(1024,768),(1280,720),(1366,768),(1440,900),(1536,864),(1920,1080)]
STILL='*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}#sageLiveNotificationHost{opacity:0!important;pointer-events:none!important}.sage-scroll-progress{visibility:hidden!important}'
MEASURE='''()=>[...document.querySelectorAll('main .page-heading,main .dashboard-heading,main .dashboard-summary-card,main .panel,main .mini-stat,main .stat-card,main .role-hero,main .data-table,main .income-kpi-grid>article,main .income-insight-grid>article,main .control-metrics>article,main .owner-request-card,main .v4-detail')].filter(e=>e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return [[...e.classList].filter(x=>!x.startsWith('d8-')).sort().join(' '),...['x','y','width','height'].map(k=>Math.round(r[k]*10)/10),s.fontSize,s.padding,s.gap,s.display]})'''
def save(path,data):
    for attempt in range(5):
        try:path.write_text(json.dumps(data,indent=2),encoding='utf-8');return
        except OSError:
            if attempt==4:raise
            time.sleep(.2)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true');parser.add_argument('--role');parser.add_argument('--resume',action='store_true');parser.add_argument('--tag');parser.add_argument('--pages');args=parser.parse_args();results={};errors=[]
    baseline_path=OUT/'before.json';baseline=json.loads(baseline_path.read_text()) if baseline_path.exists() else {}
    path=OUT/('before.json' if args.baseline else 'after'+('-'+args.tag if args.tag else '')+'.json')
    if args.resume and path.exists():results=json.loads(path.read_text())
    with sync_playwright() as p:
        browser=p.chromium.launch()
        for role in [args.role] if args.role else ['owner','staff','finance','solo']:
            ctx=browser.new_context(viewport={'width':1440,'height':900},locale='en-NG',timezone_id='Africa/Lagos',reduced_motion='reduce')
            ctx.route('https://fonts.googleapis.com/**',lambda r:r.abort());ctx.route('https://fonts.gstatic.com/**',lambda r:r.abort());ctx.route('**/api/activity/page-view',lambda r:r.fulfill(json={'ok':True}))
            if args.baseline:
                def old_asset(route):
                    file=ROOT/'.qa/desktop_before'/urlparse(route.request.url).path.lstrip('/')
                    if file.is_file():route.fulfill(path=str(file))
                    else:route.continue_()
                ctx.route('**/static/**',old_asset)
            page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(BASE+'/qa-session/'+role,wait_until='domcontentloaded');routes=page.locator('.nav-link[data-route]').evaluate_all('(es)=>es.map(e=>e.dataset.route)')
            for route in PAGES:
                key=role+'/'+route
                if route not in routes or key in results or (args.pages and route not in args.pages.split(',')):continue
                page.set_viewport_size({'width':1440,'height':900});response=page.goto(BASE+('/qa-desktop-before/' if args.baseline else '/')+route,wait_until='domcontentloaded');page.wait_for_timeout(300);page.add_style_tag(content=STILL);entry={'status':response.status,'mobile':{},'desktop':{}}
                if role=='owner':page.screenshot(path=str(OUT/(('before-' if args.baseline else 'after-')+route+'.png')))
                for w,h in [(390,844),(430,932)]:
                    page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(220);
                    if not args.baseline:expect(page.locator('html')).to_have_attribute('data-sage-style-mode','mobile')
                    geometry=page.evaluate(MEASURE);entry['mobile'][str(w)]={'geometry':geometry,'overflow':page.evaluate('document.documentElement.scrollWidth>innerWidth+1')}
                    if not args.baseline:
                        old=baseline.get(key,{}).get('mobile',{}).get(str(w),{}).get('geometry');entry['mobile'][str(w)]['equal']=old==geometry
                        if old!=geometry:entry['mobile'][str(w)]['diff']=[(a,b) for a,b in zip(old or [],geometry) if a!=b][:8]
                    if role=='owner':page.screenshot(path=str(OUT/(('before-' if args.baseline else 'after-')+route+'-'+str(w)+'.png')))
                for w,h in ([(1440,900)] if args.baseline else WIDTHS):
                    page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(100)
                    if not args.baseline:expect(page.locator('html')).to_have_attribute('data-sage-style-mode','desktop')
                    entry['desktop'][str(w)]=page.evaluate('''()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,sidebar:document.querySelector('#sidebar')?.getBoundingClientRect().width,header:document.querySelector('.topbar')?.getBoundingClientRect().height,badAmounts:[...document.querySelectorAll('.dashboard-summary-amount>strong,.income-kpi-grid strong,.income-insight-grid strong,.finance-kpi strong,.control-metrics>article>strong')].filter(e=>e.getClientRects().length&&e.scrollWidth>e.clientWidth+2).map(e=>({text:e.textContent,w:e.clientWidth,sw:e.scrollWidth})),hiddenHeads:[...document.querySelectorAll('.page-heading h1,.dashboard-heading h1')].filter(e=>getComputedStyle(e).visibility==='hidden'||e.getBoundingClientRect().height===0).length})''')
                results[key]=entry;save(path,results);save(OUT/'errors.json',errors);print(key,flush=True)
            ctx.close()
        browser.close()
    bad=[(k,w,s) for k,e in results.items() for w,s in e['desktop'].items() if s['overflow'] or s['badAmounts'] or s['hiddenHeads']]
    mobile_bad=[(k,w,s.get('diff')) for k,e in results.items() for w,s in e['mobile'].items() if s['overflow'] or (not args.baseline and not s['equal'])]
    print(json.dumps({'pages':len(results),'desktop_failures':bad,'mobile_failures':mobile_bad,'errors':errors}),flush=True)
    if not args.baseline:sys.exit(1 if bad or mobile_bad or errors else 0)
if __name__=='__main__':main()
