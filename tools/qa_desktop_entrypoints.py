"""Auth/console surfaces and theme contrast; uses only qa_desktop's temporary DB."""
import json,re,sys
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright,expect
from PIL import Image,ImageChops
BASE='http://127.0.0.1:5016';OUT=ROOT/'.qa/desktop';results=[];errors=[]
SIZES=[(1024,768),(1280,720),(1366,768),(1440,900),(1536,864),(1920,1080),(390,844),(430,932)]
STILL='*,*::before,*::after{animation:none!important;transition:none!important}'
with sync_playwright() as p:
    browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce')
    ctx.route('https://fonts.googleapis.com/**',lambda r:r.abort());ctx.route('https://fonts.gstatic.com/**',lambda r:r.abort())
    q=ctx.new_page();q.on('pageerror',lambda e:errors.append(str(e)))
    for name,path,sources in [('login','/login',['vision']),('register','/register',['vision','market']),('staff-register','/register/staff/mobile-qa-invite',['vision']),('developer-login','/platform-admin/login',['vision']),('developer','/qa-session/developer',['vision','platform_console'])]:
        q.set_viewport_size({'width':1440,'height':900});response=q.goto(BASE+path,wait_until='domcontentloaded');expect(q.locator('html')).to_have_attribute('data-sage-style-mode','desktop');q.add_style_tag(content=STILL)
        if name=='developer':q.locator('#platformLivePause').click()
        for w,h in SIZES:
            q.set_viewport_size({'width':w,'height':h});expect(q.locator('html')).to_have_attribute('data-sage-style-mode','desktop' if w>900 else 'mobile');q.wait_for_timeout(100)
            overflow=q.evaluate('()=>document.documentElement.scrollWidth>innerWidth+1');results.append({'surface':name,'size':[w,h],'overflow':overflow})
            if w in [1440,390]:q.screenshot(path=str(OUT/f'entry-{name}-{w}.png'))
        if name=='register':
            q.set_viewport_size({'width':1024,'height':768});q.locator('[name=first_name]').fill('Desktop');q.locator('[name=last_name]').fill('QA');q.locator('[name=email]').fill('desktop@example.test');q.locator('[name=password]').fill('isolated-qa-only')
            for step in [2,3,4]:
                q.locator('.register-step.active [data-next-step]').click()
                if step==3:q.locator('[name=organization_name]').fill('Desktop QA');q.locator('#businessType').select_option(index=1)
                results.append({'surface':'register-step-'+str(step),'size':[1024,768],'overflow':q.evaluate('()=>document.documentElement.scrollWidth>innerWidth+1')})
            q.screenshot(path=str(OUT/'entry-register-step4-1024.png'))
        if name=='login':
            q.set_viewport_size({'width':1440,'height':900});q.locator('#changePasswordOpen').click();expect(q.locator('#changePasswordModal')).to_be_visible();q.screenshot(path=str(OUT/'entry-password-modal.png'));q.locator('#changePasswordClose').click()
        if name=='developer':
            q.set_viewport_size({'width':1440,'height':900})
            for theme in ['dark','light','ocean','emerald','violet','amber']:
                q.evaluate('t=>document.documentElement.dataset.platformTheme=t',theme);q.screenshot(path=str(OUT/f'entry-console-{theme}.png'));results.append({'surface':'console-'+theme,'overflow':q.evaluate('()=>document.documentElement.scrollWidth>innerWidth+1')})
        # Same HTML content and original styles, compared at the protected phone width.
        q.goto(BASE+path,wait_until='domcontentloaded');q.set_viewport_size({'width':390,'height':844});q.add_style_tag(content=STILL);html=q.content();old=ctx.new_page();old.set_viewport_size({'width':390,'height':844})
        base_links=''.join(f'<link rel="stylesheet" href="/static/css/{s}.css">' for s in sources)
        html=re.sub(r'<link[^>]+href="/static/css/workspace_presence\.css[^"]*"[^>]*>.*?</noscript>',base_links,html,flags=re.S,count=1)
        html=re.sub(r'<link[^>]+data-sage-mode="[^"]+"[^>]*>','',html)
        def old_asset(route):
            file=ROOT/'.qa/desktop_before'/urlparse(route.request.url).path.lstrip('/')
            if file.is_file():route.fulfill(path=str(file))
            else:route.continue_()
        (OUT/f'entry-before-{name}.html').write_text(html,encoding='utf-8');old.route('**/static/**',old_asset);old.route(BASE+'/qa-entry-before',lambda r:r.fulfill(body=html,content_type='text/html'));old.goto(BASE+'/qa-entry-before',wait_until='domcontentloaded');old.add_style_tag(content=STILL);old.wait_for_timeout(150)
        a=OUT/f'entry-mobile-before-{name}.png';b=OUT/f'entry-mobile-after-{name}.png';old.screenshot(path=str(a));q.screenshot(path=str(b));diff=ImageChops.difference(Image.open(a).convert('RGB'),Image.open(b).convert('RGB'));changed=sum(any(c>3 for c in pixel) for pixel in diff.getdata());results.append({'surface':name,'mobile_changed_pixels':changed,'before_styles':old.locator('link[rel=stylesheet]').evaluate_all('(es)=>es.map(e=>[e.href,!!e.sheet])')});old.close()
        if name=='developer':ctx.clear_cookies()
    browser.close()
result={'cases':results,'errors':errors};(OUT/'entrypoints.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)
sys.exit(1 if errors or any(r.get('overflow') for r in results) else 0)
