"""Browser regression checks; start qa_mobile.py first. Requires Playwright Chromium."""
import argparse,json,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright

PAGES='dashboard requests income expenses finance debtors imprest daily_close workspace catalog operations fulfillment procurement inventory assets events stock customers suppliers branches departments staff reports audit payroll analytics bills compliance business_reports settings'.split()
WIDTHS=[320,360,375,390,412,430,480,600,768,820,1024,1366,1440,1920]
OUT=ROOT/'.qa';OUT.mkdir(exist_ok=True)
STILL='*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}#sageLiveNotificationHost{opacity:0!important;pointer-events:none!important}.dashboard-time-panel,.sage-scroll-progress{visibility:hidden!important}'
MEASURE="""() => {
 const visible=e=>!!e.getClientRects().length && getComputedStyle(e).visibility!=='hidden';
 const selectors='.sidebar,.nav-icon,.topbar,.page-heading h1,.dashboard-heading h1,.panel,.stat-card,.income-kpi-grid>article,.income-insight-grid>article,.dashboard-summary-card,.finance-kpi,.control-metrics>article,.btn,.data-table th,.data-table td';
 return [...document.querySelectorAll(selectors)].filter(visible).map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return [e.tagName,e.className,...['x','y','width','height'].map(k=>Math.round(r[k]*100)/100),s.fontSize,s.padding,s.gap,s.display]});
}"""
MOBILE="""() => {
 const visible=e=>!!e.getClientRects().length && getComputedStyle(e).visibility!=='hidden';
 const tables=[...document.querySelectorAll('main table,.platform-v2-main table')].filter(visible);
 const values=[...document.querySelectorAll('.income-kpi-grid strong,.income-insight-grid strong,.dashboard-summary-amount strong,.finance-kpi strong,.control-metrics strong,.owner-request-kpis strong,.staff-request-wallet-premium strong')].filter(visible);
 return {overflow:document.documentElement.scrollWidth>innerWidth+1,
   badTables:tables.filter(t=>getComputedStyle(t).display!=='table'||!t.querySelector('th')||[...t.querySelectorAll('td')].some(c=>getComputedStyle(c).display!=='table-cell')).map(t=>t.className),
   badValues:values.filter(e=>e.scrollWidth>e.clientWidth+1||parseFloat(getComputedStyle(e).fontSize)<18).map(e=>({text:e.textContent,font:getComputedStyle(e).fontSize,w:e.clientWidth,sw:e.scrollWidth})),
   header:document.querySelector('.topbar')?.getBoundingClientRect().height,
   scrollTables:tables.length};
}"""

def settle(page):
    page.wait_for_timeout(170)
    page.add_style_tag(content=STILL)
    page.evaluate('document.fonts.ready')

def capture(page,label):page.screenshot(path=str(OUT/(label+'.png')),animations='disabled')

def save_json(path,data):
    # Windows indexers can briefly hold a previous result file open.
    payload=json.dumps(data,indent=2)
    for attempt in range(6):
        try:path.write_text(payload,encoding='utf-8');return
        except OSError:
            if attempt==5:raise
            time.sleep(.15)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true');parser.add_argument('--matrix',action='store_true');parser.add_argument('--resume',action='store_true');parser.add_argument('--role',choices=['owner','staff','finance','solo']);args=parser.parse_args()
    results={};errors=[];baseline={}
    if (OUT/'desktop-before.json').exists():baseline=json.loads((OUT/'desktop-before.json').read_text())
    progress=OUT/('mobile-matrix-'+(args.role or 'all')+'.json')
    if args.resume and not args.baseline and progress.exists():
        saved=json.loads(progress.read_text());results=saved['results'];errors=saved.get('errors',[])
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':900},locale='en-NG',timezone_id='Africa/Lagos',reduced_motion='reduce')
        # Use deterministic local fallbacks for offline visual comparison; no font-network timing differences.
        context.route('https://fonts.googleapis.com/**',lambda route:route.abort())
        context.route('https://fonts.gstatic.com/**',lambda route:route.abort())
        context.route('**/api/activity/page-view',lambda route:route.fulfill(json={'ok':True}))
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        for role in [args.role] if args.role else ['owner','staff','finance','solo']:
            page.goto('http://127.0.0.1:5016/qa-session/'+role,wait_until='domcontentloaded')
            routes=page.locator('.nav-link[data-route]').evaluate_all('(els)=>els.map(e=>e.dataset.route)')
            for route in PAGES:
                if route not in routes:continue
                key=role+'/'+route
                if args.resume and key in results:continue
                page.set_viewport_size({'width':1440,'height':900})
                response=page.goto('http://127.0.0.1:5016/'+route,wait_until='domcontentloaded');settle(page)
                if response.status!=200:results[key]={'status':response.status};continue
                geometry=page.evaluate(MEASURE)
                if args.baseline:results[key]=geometry
                else:
                    results[key]={'desktopEqual':geometry==baseline.get(key),'widths':{}}
                    if geometry!=baseline.get(key):results[key]['desktopDiff']=[(a,b) for a,b in zip(baseline.get(key,[]),geometry) if a!=b][:4]
                if role=='owner' and route in ['dashboard','income','expenses','finance','requests']:
                    capture(page,('before-' if args.baseline else 'after-')+route+'-1440')
                if args.baseline:
                    if role=='owner' and route in ['dashboard','income','expenses','finance','requests']:
                        page.set_viewport_size({'width':390,'height':844});settle(page);capture(page,'before-'+route+'-390')
                    continue
                widths=WIDTHS if args.matrix else [390,430,768,1440]
                for width in widths:
                    page.set_viewport_size({'width':width,'height':932 if width==430 else 844 if width<600 else 1024 if width<1000 else 900})
                    page.wait_for_timeout(65)
                    if width<=900:results[key]['widths'][str(width)]=page.evaluate(MOBILE)
                    if role=='owner' and route in ['dashboard','income','expenses','finance','requests'] and width in [390,430,768]:capture(page,'after-'+route+'-'+str(width))
                print(key,flush=True)
                save_json(progress,{'results':results,'errors':errors})
        browser.close()
    name='desktop-before' if args.baseline else 'mobile-matrix'
    save_json(OUT/(name+'.json'),{'results':results,'errors':errors} if not args.baseline else results)
    print(json.dumps({'pages':len(results),'pageErrors':errors},indent=2))

if __name__=='__main__':main()
