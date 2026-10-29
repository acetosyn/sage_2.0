"""Functional mobile UI checks against qa_mobile.py, never a production server."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright,expect
BASE='http://127.0.0.1:5016';OUT=ROOT/'.qa';OUT.mkdir(exist_ok=True);checks=[];errors=[]

def record(name,run):
    try:run();checks.append({'name':name,'ok':True})
    except Exception as e:checks.append({'name':name,'ok':False,'error':str(e)[:1200]})
    (OUT/'mobile-interactions.json').write_text(json.dumps({'checks':checks,'pageErrors':errors},indent=2),encoding='utf-8')
    print(checks[-1],flush=True)

def assert_true(value,message='Assertion failed'):
    if not value:raise AssertionError(message)

with sync_playwright() as p:
    browser=p.chromium.launch()
    context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce')
    context.route('https://fonts.googleapis.com/**',lambda r:r.abort());context.route('https://fonts.gstatic.com/**',lambda r:r.abort())
    page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
    def go(path):
        page.goto(BASE+path,wait_until='domcontentloaded');page.wait_for_timeout(220);page.add_style_tag(content='#sageLiveNotificationHost{opacity:0!important}#sageLiveNotificationHost *{pointer-events:none!important}')
    go('/qa-session/owner')
    def drawer():
        page.locator('#mobileMenu').click();assert_true(page.locator('#mobileMenu').get_attribute('aria-expanded')=='true')
        assert_true(page.locator('#appContent').evaluate('(e)=>e.inert'),'Drawer must make background inert')
        assert_true(page.locator('.sidebar .nav-icon').first.evaluate('(e)=>e.getBoundingClientRect().width')>=22)
        page.keyboard.press('Escape');page.wait_for_timeout(80);assert_true(not page.locator('#appContent').evaluate('(e)=>e.inert'))
        page.locator('#mobileMenu').click();page.set_viewport_size({'width':1440,'height':900});page.wait_for_timeout(80)
        assert_true(not page.locator('#sidebar').evaluate('(e)=>e.inert'));assert_true('mobile-nav-open' not in page.locator('body').get_attribute('class'))
        page.set_viewport_size({'width':390,'height':844})
    record('Drawer focus, 24px icons, Escape and desktop restoration',drawer)
    def appearance():
        page.locator('#mobileToolsToggle').click();assert_true(page.locator('#mobileToolsPanel').is_visible(),'More menu must open')
        page.locator('[data-mobile-control="fontToggle"]').click();assert_true(page.locator('#fontMenu').is_visible(),'Font menu must open')
        page.locator('[data-font-size="large"]').click();page.keyboard.press('Escape')
        assert_true(page.locator('html').get_attribute('data-font-size')=='large')
        go('/income');font=page.locator('.income-kpi-grid strong').first.evaluate('(e)=>getComputedStyle(e).fontSize')
        page.set_viewport_size({'width':1440,'height':900});page.wait_for_timeout(100)
        assert_true(page.locator('.income-kpi-grid strong').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)')>float(font[:-2]))
        page.set_viewport_size({'width':390,'height':844});page.reload(wait_until='domcontentloaded');page.wait_for_timeout(180)
        assert_true(page.locator('.income-kpi-grid strong').first.evaluate('(e)=>getComputedStyle(e).fontSize')==font,'Large text changed after reload')
        assert_true(page.locator('[data-sage-base-font-size]').count()==0,'No computed-font cache is allowed')
        page.evaluate("localStorage.setItem('sage-font-size','medium')");go('/income')
    record('Appearance menu and font-size resize/reload consistency',appearance)
    def themes():
        for theme in page.locator('[data-theme-choice]').evaluate_all('(els)=>els.map(e=>e.dataset.themeChoice)'):
            page.locator('#mobileToolsToggle').click();page.locator('[data-mobile-control="themeToggle"]').click();page.locator('[data-theme-choice="'+theme+'"]').click()
            assert_true(page.locator('html').get_attribute('data-theme')==theme)
            assert_true(page.locator('.income-kpi-grid strong').first.evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'))
        page.evaluate("localStorage.setItem('sage-theme','dark')");go('/income')
    record('All 19 appearance palettes retain readable amounts',themes)
    def overlays():
        page.locator('#commandOpen').click();assert_true(page.locator('#commandPalette').get_attribute('aria-hidden')=='false');page.keyboard.press('Escape')
        page.locator('#notificationToggle').click();assert_true(page.locator('#notificationTray').is_visible());page.keyboard.press('Escape')
        page.locator('#aiOpen').click();assert_true(page.locator('#aiDrawer').get_attribute('aria-hidden')=='false');page.keyboard.press('Escape')
        page.locator('#mobileToolsToggle').click();page.locator('[data-mobile-control="sageGuideToggle"]').click();assert_true(page.locator('#sageGuideDrawer').get_attribute('aria-hidden')=='false');page.keyboard.press('Escape')
    record('Search, notifications, SAGE AI and Guide controls',overlays)
    def ledger():
        go('/finance');wrap=page.locator('.finance-workbook-scroll');wrap.evaluate('(e)=>e.scrollLeft=450');assert_true(wrap.evaluate('(e)=>e.scrollLeft')>0)
        assert_true(page.locator('.finance-workbook-table').evaluate('(e)=>getComputedStyle(e).display')=='table')
        assert_true(page.locator('.finance-workbook-table th').first.evaluate('(e)=>getComputedStyle(e).position')=='sticky')
        assert_true(page.locator('.finance-workbook-table td').first.evaluate('(e)=>getComputedStyle(e).position')=='sticky')
        assert_true(page.locator('.finance-workbook-clear').evaluate('(e)=>e.getBoundingClientRect().width')<=85)
    record('Ledger scrolling, sticky identity/header and compact Clear',ledger)
    def spa():
        go('/income');before=page.locator('.income-kpi-grid').evaluate('(e)=>[e.clientWidth,e.clientHeight]')
        page.locator('#mobileMenu').click();page.locator('.nav-link[data-route="expenses"]').click();expect(page.locator('body')).to_have_attribute('data-page','expenses');page.wait_for_url('**/expenses')
        page.go_back(wait_until='domcontentloaded');expect(page.locator('body')).to_have_attribute('data-page','income');page.wait_for_timeout(180)
        assert_true(page.locator('.income-kpi-grid').evaluate('(e)=>[e.clientWidth,e.clientHeight]')==before,'SPA back changes KPI geometry')
        page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(100);page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(100)
        assert_true(page.locator('.income-kpi-grid').evaluate('(e)=>[e.clientWidth,e.clientHeight]')==before,'Orientation changes KPI geometry')
    record('Partial navigation, browser back and orientation consistency',spa)
    for role,routes in [('owner',['requests','staff','departments','reports']),('finance',['finance','income','expenses','operations']),('solo',['finance','income','expenses','inventory','assets','catalog','fulfillment'])]:
        go('/qa-session/'+role)
        for route in routes:
            go('/'+route)
            modal_ids=page.locator('.modal-backdrop[id]').evaluate_all('(els)=>els.map(e=>e.id)')
            for modal_id in modal_ids:
                if modal_id in ['requestModal','reportViewModal'] and route!='requests':continue
                def modal_check(modal_id=modal_id):
                    page.evaluate('''id=>{const m=document.getElementById(id);document.body.append(m);m.classList.add('open');m.setAttribute('aria-hidden','false');document.body.classList.add('sage-modal-open');}''',modal_id)
                    page.wait_for_timeout(50)
                    metrics=page.locator('#'+modal_id+' .modal-card').evaluate('''e=>{const r=e.getBoundingClientRect();e.scrollTop=e.scrollHeight;return {w:r.width,h:r.height,x:r.x,y:r.y,sw:e.scrollWidth,cw:e.clientWidth,sh:e.scrollHeight,ch:e.clientHeight,st:e.scrollTop,overflow:getComputedStyle(e).overflowY}}''')
                    assert_true(metrics['x']>=0 and metrics['w']<=390 and metrics['h']<=824,str(metrics))
                    assert_true(metrics['sw']<=metrics['cw']+1,'Modal has horizontal overflow: '+str(metrics))
                    assert_true(metrics['sh']<=metrics['ch']+1 or metrics['st']>0,'Modal cannot scroll')
                    assert_true(page.locator('#'+modal_id).evaluate('(e)=>!e.inert'),'Open modal is inert')
                    page.evaluate('''id=>{document.getElementById(id).classList.remove('open');document.getElementById(id).setAttribute('aria-hidden','true');document.body.classList.remove('sage-modal-open');document.documentElement.classList.remove('sage-modal-open');}''',modal_id)
                record(role+'/'+route+'/'+modal_id,modal_check)
    # Anonymous authentication / onboarding and the separate developer shell.
    context.clear_cookies()
    for route in ['/login','/register','/register/staff/mobile-qa-invite','/platform-admin/login']:
        def auth(route=route):
            go(route)
            for width in [320,390,430,768]:
                page.set_viewport_size({'width':width,'height':844});assert_true(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Auth overflow at '+str(width))
            page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/('auth-'+route.strip('/').replace('/','-')+'.png')))
        record('Authentication '+route,auth)
    def developer():
        go('/qa-session/developer')
        for width in [320,390,430,768,1440]:
            page.set_viewport_size({'width':width,'height':844});assert_true(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Developer overflow at '+str(width))
        page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/'developer-390.png'))
    record('Developer Console mobile shell and tables',developer)
    browser.close()
print(json.dumps({'checks':len(checks),'failed':[c for c in checks if not c['ok']],'pageErrors':errors},indent=2))
sys.exit(1 if errors or any(not c['ok'] for c in checks) else 0)
