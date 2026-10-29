"""Same live fixture content, old/new templates and assets, protected phone UI."""
import json,sys
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright,expect
from qa_desktop_browser import BASE,OUT,MEASURE,STILL
from PIL import Image,ImageChops
cases=[];pixels=[];shell=[]
with sync_playwright() as p:
    browser=p.chromium.launch()
    for role,routes in [('owner',['dashboard','income','expenses','finance','requests','workspace','inventory','customers','staff','reports','audit','settings']),('finance',['dashboard','catalog']),('staff',['catalog']),('solo',['audit'])]:
        ctx=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce',locale='en-NG',timezone_id='Africa/Lagos');ctx.route('https://fonts.googleapis.com/**',lambda r:r.abort());ctx.route('https://fonts.gstatic.com/**',lambda r:r.abort());ctx.route('**/api/activity/page-view',lambda r:r.fulfill(json={'ok':True}))
        after=ctx.new_page();after.goto(BASE+'/qa-session/'+role,wait_until='domcontentloaded');before=ctx.new_page()
        def old_asset(route):
            file=ROOT/'.qa/desktop_before'/urlparse(route.request.url).path.lstrip('/')
            if file.is_file():route.fulfill(path=str(file))
            else:route.continue_()
        before.route('**/static/**',old_asset)
        for route in routes:
            after.set_viewport_size({'width':1440,'height':900});before.goto(BASE+'/qa-desktop-before/'+route,wait_until='domcontentloaded');after.goto(BASE+'/'+route,wait_until='domcontentloaded');mask=STILL+'.sage-mobile-clock,[data-audit-now]{visibility:hidden!important}'
            before.add_style_tag(content=mask);after.add_style_tag(content=mask)
            for width,height in [(390,844),(430,932)]:
                for q in [before,after]:q.set_viewport_size({'width':width,'height':height});q.wait_for_timeout(200)
                expect(after.locator('html')).to_have_attribute('data-sage-style-mode','mobile');a=before.evaluate(MEASURE);b=after.evaluate(MEASURE);cases.append({'role':role,'page':route,'width':width,'equal':a==b,'diff':[(x,y) for x,y in zip(a,b) if x!=y][:5]})
                if role=='owner' and width==390:
                    aa=OUT/('paired-before-'+route+'.png');bb=OUT/('paired-after-'+route+'.png');before.screenshot(path=str(aa));after.screenshot(path=str(bb));diff=ImageChops.difference(Image.open(aa).convert('RGB'),Image.open(bb).convert('RGB'));changed=sum(any(channel>3 for channel in pixel) for pixel in diff.getdata());pixels.append({'page':route,'changed_pixels':changed,'percent':round(changed/(390*844)*100,4)})
            if role=='owner' and route=='dashboard':
                for width in [1024,1280,1366,1440,1536,1920]:
                    for q in [before,after]:q.set_viewport_size({'width':width,'height':900});q.wait_for_timeout(100)
                    expect(after.locator('html')).to_have_attribute('data-sage-style-mode','desktop');measure="()=>[document.querySelector('#sidebar').getBoundingClientRect().width,document.querySelector('.topbar').getBoundingClientRect().height]";a=before.evaluate(measure);b=after.evaluate(measure);shell.append({'width':width,'before':a,'after':b,'equal':a==b})
                for q in [before,after]:q.set_viewport_size({'width':390,'height':844})
            print(role+'/'+route,flush=True)
        ctx.close()
    browser.close()
result={'cases':cases,'pixels':pixels,'shell':shell};(OUT/'same-content.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'comparisons':len(cases),'failed':[x for x in cases if not x['equal']],'shell_failed':[x for x in shell if not x['equal']],'pixels':pixels}),flush=True);sys.exit(1 if any(not x['equal'] for x in cases+shell) else 0)
