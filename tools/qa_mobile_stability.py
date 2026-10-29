"""Same-content desktop CSS comparison and no-JS/initialized mobile geometry."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright
from qa_mobile_browser import PAGES,MEASURE,STILL
OUT=ROOT/'.qa';OUT.mkdir(exist_ok=True);BASE='http://127.0.0.1:5016';results=[]
parser=argparse.ArgumentParser();parser.add_argument('--mobile-only',action='store_true');parser.add_argument('--original-css',type=Path,default=OUT/'original_css');args=parser.parse_args()
ORIGINAL=args.original_css
NAMES=['vision','dashboard','control','premium','market','business','sage5','sage_mobile_ledger']

def save():
    (OUT/'layout-stability.json').write_text(json.dumps(results,indent=2),encoding='utf-8')

with sync_playwright() as p:
    browser=p.chromium.launch()
    context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce')
    context.route('https://fonts.googleapis.com/**',lambda r:r.abort());context.route('https://fonts.gstatic.com/**',lambda r:r.abort())
    context.route('**/api/activity/page-view',lambda r:r.fulfill(status=200,content_type='application/json',body='{"ok":true}'))
    page=context.new_page()
    for role in ([] if args.mobile_only else ['owner','staff','finance','solo']):
        page.goto(BASE+'/qa-session/'+role,wait_until='domcontentloaded')
        routes=page.locator('.nav-link[data-route]').evaluate_all('(els)=>els.map(e=>e.dataset.route)')
        for route in PAGES:
            if route not in routes:continue
            page.goto(BASE+'/'+route,wait_until='domcontentloaded');page.wait_for_timeout(180);page.add_style_tag(content=STILL)
            # Save CSS in the same order as the original application shell.
            widths=[1024,1366,1440,1920] if route in ['dashboard','income','expenses','finance','requests','audit'] else [1440]
            current={}
            for width in widths:
                page.set_viewport_size({'width':width,'height':900});page.wait_for_timeout(100);current[width]=page.evaluate(MEASURE)
                if role=='owner' and route in ['dashboard','income','expenses','finance','requests'] and width==1440:page.screenshot(path=str(OUT/('fixed-after-'+route+'.png')),animations='disabled')
            page.evaluate("() => {document.querySelectorAll('link[rel=stylesheet][href*=\"/static/css/\"]').forEach(el=>el.disabled=true);}")
            for name in NAMES:page.add_style_tag(content=(ORIGINAL/(name+'.css')).read_text(encoding='utf-8-sig'))
            page.add_style_tag(content='.mobile-tools-toggle,.mobile-tools-panel{display:none}')
            for width in widths:
                page.set_viewport_size({'width':width,'height':900});page.wait_for_timeout(100);before=page.evaluate(MEASURE);after=current[width]
                if role=='owner' and route in ['dashboard','income','expenses','finance','requests'] and width==1440:page.screenshot(path=str(OUT/('fixed-before-'+route+'.png')),animations='disabled')
                results.append({'kind':'desktop','role':role,'page':route,'width':width,'equal':before==after,'diff':[(a,b) for a,b in zip(before,after) if a!=b][:3]});save()
            print(role+'/'+route,flush=True)
    # Initial server HTML should already have the correct mobile component sizes.
    for role in ['owner','staff','solo']:
        for width in [320,390,430,768]:
            nojs=browser.new_context(java_script_enabled=False,viewport={'width':width,'height':844})
            nojs.route('https://fonts.googleapis.com/**',lambda r:r.abort());nojs.route('https://fonts.gstatic.com/**',lambda r:r.abort())
            beforepage=nojs.new_page();beforepage.goto(BASE+'/qa-session/'+role,wait_until='domcontentloaded')
            normal=browser.new_context(viewport={'width':width,'height':844},reduced_motion='reduce');normal.route('https://fonts.googleapis.com/**',lambda r:r.abort());normal.route('https://fonts.gstatic.com/**',lambda r:r.abort())
            afterpage=normal.new_page();afterpage.goto(BASE+'/qa-session/'+role,wait_until='domcontentloaded')
            for route in ['dashboard','income','expenses','requests','finance']:
                if route not in PAGES:continue
                br=beforepage.goto(BASE+'/'+route,wait_until='domcontentloaded');ar=afterpage.goto(BASE+'/'+route,wait_until='domcontentloaded')
                if br.status!=200 or ar.status!=200:continue
                # Reproduce the synchronous appearance pre-paint script even when other JS is disabled.
                beforepage.evaluate("()=>{document.documentElement.dataset.font='manrope';document.documentElement.dataset.fontSize='medium';}")
                afterpage.wait_for_timeout(240)
                measure='''()=>[...document.querySelectorAll('.page-heading h1,.dashboard-heading h1,.income-kpi-grid>article,.income-insight-grid>article,.dashboard-summary-card,.finance-kpi,.owner-request-kpis>article')].map(e=>{const r=e.getBoundingClientRect();return [e.tagName,...['x','y','width','height'].map(k=>Math.round(r[k]*100)/100)]})'''
                before=beforepage.evaluate(measure);after=afterpage.evaluate(measure)
                results.append({'kind':'mobile-initialization','role':role,'page':route,'width':width,'equal':before==after,'diff':[(a,b) for a,b in zip(before,after) if a!=b][:4]});save()
            nojs.close();normal.close()
    browser.close()
print(json.dumps({'checks':len(results),'failed':[r for r in results if not r['equal']]},indent=2))
sys.exit(1 if any(not r['equal'] for r in results) else 0)
