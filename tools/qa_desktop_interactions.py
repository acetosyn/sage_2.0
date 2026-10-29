"""SAGE desktop interactions, palettes, dialogs and clock. Temporary QA DB only."""
import json,sys,traceback
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright,expect
BASE='http://127.0.0.1:5016';OUT=ROOT/'.qa/desktop';OUT.mkdir(exist_ok=True);checks=[];errors=[];metrics={}
def ok(value,message='Assertion failed'):
    if not value:raise AssertionError(message)
def record(name,fn):
    if '--only' in sys.argv and not any(part.lower() in name.lower() for part in sys.argv[sys.argv.index('--only')+1].split(',')):return
    try:fn();result={'name':name,'ok':True}
    except Exception as e:result={'name':name,'ok':False,'error':str(e)[:1800],'trace':traceback.format_exc()[-1200:]}
    checks.append(result);print(json.dumps(result),flush=True);(OUT/'interactions.json').write_text(json.dumps({'checks':checks,'errors':errors,'metrics':metrics},indent=2),encoding='utf-8')

with sync_playwright() as p:
    browser=p.chromium.launch()
    def context(width=1440,height=900,zone='Africa/Lagos',fonts=False):
        c=browser.new_context(viewport={'width':width,'height':height},locale='en-NG',timezone_id=zone,reduced_motion='reduce')
        if not fonts:c.route('https://fonts.googleapis.com/**',lambda r:r.abort());c.route('https://fonts.gstatic.com/**',lambda r:r.abort())
        c.route('**/api/activity/page-view',lambda r:r.fulfill(json={'ok':True}));return c
    ctx=context();page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.set_default_timeout(7000)
    def go(route):
        response=page.goto(BASE+route,wait_until='domcontentloaded');ok(response.status==200,str((route,response.status)));expect(page.locator('html')).to_have_attribute('data-sage-style-mode','desktop' if page.viewport_size['width']>900 else 'mobile');page.wait_for_timeout(120);page.add_style_tag(content='*,*::before,*::after{animation:none!important;transition:none!important}#sageLiveNotificationHost{opacity:0!important;pointer-events:none!important}#sageLiveNotificationHost *{pointer-events:none!important}')
    go('/qa-session/owner')
    def saved_views():
        go('/income');field=page.locator('[data-money-search]');ok(field.count()==1,'Income search selector');field.fill('DESK-QA-001');page.locator('[data-desktop-save-view]').click();page.locator('[data-desktop-save-form] input').fill('Review receipts');page.locator('[data-desktop-save-form] button[type=submit]').click();expect(page.locator('[data-desktop-view-feedback]')).to_contain_text('saved');page.locator('[data-desktop-reset-view]').click();expect(field).to_have_value('');page.locator('[data-desktop-saved-views]').select_option(label='Review receipts');expect(field).to_have_value('DESK-QA-001')
        page.reload(wait_until='domcontentloaded');page.locator('[data-desktop-saved-views]').select_option(label='Review receipts');expect(page.locator('[data-money-search]')).to_have_value('DESK-QA-001');page.locator('[data-desktop-reset-view]').click()
        page.evaluate("()=>SAGENavigate('customers')");expect(page.locator('body')).to_have_attribute('data-page','customers');expect(page.locator('[data-desktop-save-view]')).to_be_enabled();search=page.locator('[data-v4-search]');total_contacts=page.locator('[data-v4-search-row]:visible').count();search.fill('Northgate');expect(page.locator('[data-v4-search-row]:visible')).to_have_count(1);page.locator('[data-desktop-save-view]').click();page.locator('[data-desktop-save-form] input').fill('Priority contacts');page.locator('[data-desktop-save-form] button[type=submit]').click();page.locator('[data-desktop-reset-view]').click();expect(page.locator('[data-v4-search-row]:visible')).to_have_count(total_contacts)
        page.evaluate("()=>SAGENavigate('income')");expect(page.locator('[data-desktop-saved-views] option')).to_have_count(2);page.evaluate("()=>SAGENavigate('customers')");page.locator('[data-desktop-saved-views]').select_option(label='Priority contacts');expect(page.locator('[data-v4-search]')).to_have_value('Northgate');expect(page.locator('[data-v4-search-row]:visible')).to_have_count(1);page.locator('[data-desktop-reset-view]').click()
        ctx.clear_cookies();go('/qa-session/staff');go('/income');expect(page.locator('body')).to_have_attribute('data-user-role','staff');expect(page.locator('[data-desktop-saved-views] option')).to_have_count(1);ctx.clear_cookies();go('/qa-session/owner')
    record('Saved views persist, apply/reset, survive partial navigation and stay account-scoped',saved_views)

    def sections_hover():
        go('/finance');options=page.locator('[data-desktop-jump] option').count();ok(options>=5,str(options));page.locator('[data-desktop-jump]').select_option(index=3);page.wait_for_timeout(80);ok(page.evaluate('()=>scrollY')>150,'Section shortcut did not move to content')
        for route,selector in [('dashboard','.dashboard-summary-card'),('income','.income-kpi-grid>article'),('workspace','.job-tool-card'),('departments','.department-card')]:
            go('/'+route);card=page.locator(selector).first
            if not card.count():continue
            card.scroll_into_view_if_needed();before=card.bounding_box();card.hover();after=card.bounding_box();ok(abs(before['y']-after['y'])<.6 and abs(before['x']-after['x'])<.6,'Card moved: '+route)
        for width in [1024,1280,1366,1440,1536,1920]:
            page.set_viewport_size({'width':width,'height':900});ok(page.locator('#sidebar').bounding_box()['width']>=200,'Sidebar footprint too small');ok(page.locator('.topbar').bounding_box()['height']==82,'Header footprint changed')
        page.set_viewport_size({'width':1440,'height':900})
    record('Section shortcuts, steady hover, preserved sidebar/header proportions',sections_hover)

    def adaptive():
        cold=context(390,844);q=cold.new_page();requests=[];q.on('request',lambda r:requests.append(r.url));q.goto(BASE+'/qa-session/owner',wait_until='domcontentloaded');expect(q.locator('html')).to_have_attribute('data-sage-style-mode','mobile');ok(not any('/desktop_foundation' in url or '/sage_desktop.css' in url for url in requests),'Phone downloaded desktop foundation');expect(q.locator('.d8-contextbar')).to_be_hidden();expect(q.locator('.sage-mobile-clock')).to_be_visible()
        for width in [1440,390,1024,430,1440,390]:
            q.set_viewport_size({'width':width,'height':900 if width>900 else 844});expect(q.locator('html')).to_have_attribute('data-sage-style-mode','desktop' if width>900 else 'mobile');ok(q.locator('link[data-sage-mode=desktop]').count()==2);ok(q.locator('link[data-sage-mode=mobile]').count()==7);ok(q.evaluate("()=>{const es=[...document.querySelectorAll('link[rel=stylesheet]')],mobile=es.filter(e=>e.dataset.sageMode==='mobile');return mobile.every(e=>es.indexOf(e)<es.findIndex(a=>a.href.includes('/sage_ai.css')))}"),'Mobile foundation order changed after resizing');ok(q.locator('.d8-contextbar:visible').count()==(1 if width>900 else 0));ok(q.locator('.sage-mobile-clock:visible').count()==(0 if width>900 else 1));ok(q.locator('.sage-analog-clock:visible').count()==(1 if width>900 else 0))
        metrics['cold_mobile_desktop_css_requests']=0;cold.close()
    record('Cold phone avoids desktop bundle; breakpoint changes load once and restore each UI',adaptive)

    def clocks():
        for zone in ['Africa/Lagos','America/Los_Angeles','Pacific/Kiritimati']:
            c=context(390,844,zone);q=c.new_page();q.clock.install(time=datetime(2026,10,28,22,59,50,tzinfo=timezone.utc));q.goto(BASE+'/qa-session/owner',wait_until='domcontentloaded');expect(q.locator('.sage-mobile-clock')).to_be_visible();clock=q.locator('.sage-mobile-clock');before=clock.bounding_box();q.clock.fast_forward(20000);expected=q.evaluate("()=>new Intl.DateTimeFormat('en-NG',{hour:'2-digit',minute:'2-digit',hour12:true}).format(new Date()).replace(/\\b(am|pm)\\b/gi,x=>x.toUpperCase())");expect(q.locator('[data-mobile-clock-time]')).to_have_text(expected);after=clock.bounding_box();ok(before==after,'Clock changed dimensions '+zone);ok(zone in q.locator('[data-mobile-clock-only]').get_attribute('title'));q.evaluate("()=>{window.__clockMutations=0;new MutationObserver(rs=>window.__clockMutations+=rs.length).observe(document.querySelector('.sage-mobile-clock'),{childList:true,subtree:true})}");q.clock.fast_forward(5000);ok(q.evaluate('()=>window.__clockMutations')==0,'Digital clock rewrites every second')
            for route in ['income','dashboard','workspace','dashboard']:
                q.evaluate('(route)=>SAGENavigate(route)',route);expect(q.locator('body')).to_have_attribute('data-page',route)
            expect(q.locator('.sage-mobile-clock:visible')).to_have_count(1);c.close()
        for role in ['owner','staff','finance','solo']:
            c=context(390,844);q=c.new_page();q.goto(BASE+'/qa-session/'+role);q.wait_for_timeout(100);clock=q.locator('.sage-mobile-clock:visible');ok(clock.bounding_box()['x']>240,'Clock is not at right of heading');ok(q.evaluate('''()=>{const c=document.querySelector('.sage-mobile-clock').getBoundingClientRect();return [...document.querySelectorAll('h1,.page-heading .eyebrow,.dashboard-heading .eyebrow')].every(e=>{const r=document.createRange();r.selectNodeContents(e);return [...r.getClientRects()].every(t=>!(Math.min(c.right,t.right)>Math.max(c.left,t.left)&&Math.min(c.bottom,t.bottom)>Math.max(c.top,t.top)))})}'''),'Clock overlaps heading text: '+role);c.close()
    record('Local clock crosses midnight in three zones, remains stable and survives navigation',clocks)

    def palettes():
        go('/dashboard');themes=page.locator('[data-theme-choice]').evaluate_all('(es)=>es.map(e=>e.dataset.themeChoice)');failures=[]
        for route in ['dashboard','income','expenses','finance','inventory','customers','audit','settings']:
            go('/'+route)
            for theme in themes:
                page.evaluate('(theme)=>document.documentElement.dataset.theme=theme',theme)
                result=page.evaluate('''()=>{const bad=[...document.querySelectorAll('.dashboard-summary-amount>strong,.income-kpi-grid strong,.income-insight-grid strong,.finance-kpi strong,.control-metrics>article>strong')].filter(e=>e.getClientRects().length&&e.scrollWidth>e.clientWidth+2);return {overflow:document.documentElement.scrollWidth>innerWidth+1,bad:bad.map(e=>e.textContent)}}''')
                if result['overflow'] or result['bad']:failures.append([route,theme,result])
            page.evaluate("()=>document.documentElement.dataset.theme='dark'")
        metrics['palette_states']=len(themes)*8;ok(not failures,str(failures))
    record('All 19 palettes across eight page families retain bounded readable figures',palettes)

    def fonts():
        go('/income');fonts=page.locator('[data-font-choice]').evaluate_all('(es)=>es.map(e=>e.dataset.fontChoice)');failures=[]
        for width in [1024,1440]:
            page.set_viewport_size({'width':width,'height':900})
            for font in fonts:
                for size in ['small','medium','large']:
                    page.evaluate('([font,size])=>{document.documentElement.dataset.font=font;document.documentElement.dataset.fontSize=size}',[font,size]);bad=page.evaluate("()=>[...document.querySelectorAll('.income-kpi-grid strong,.income-insight-grid strong')].filter(e=>e.getClientRects().length&&e.scrollWidth>e.clientWidth+2).map(e=>e.textContent)")
                    if bad:failures.append([width,font,size,bad])
        metrics['font_size_states']=len(fonts)*3*2;ok(not failures,str(failures));page.evaluate("()=>{document.documentElement.dataset.font='manrope';document.documentElement.dataset.fontSize='medium'}");page.set_viewport_size({'width':1440,'height':900})
    record('Ten font choices and three sizes at laptop/desktop widths',fonts)

    def overlays():
        go('/dashboard');page.locator('#commandOpen').click();expect(page.locator('#commandPalette')).to_have_attribute('aria-hidden','false');page.keyboard.press('Escape');page.locator('#notificationToggle').click();expect(page.locator('#notificationTray')).to_be_visible();page.keyboard.press('Escape');page.locator('#aiOpen').click();expect(page.locator('#aiDrawer')).to_have_attribute('aria-hidden','false');ok(page.locator('#aiBackdrop').evaluate('(e)=>getComputedStyle(e).backdropFilter')=='none');page.keyboard.press('Escape');page.locator('#fontToggle').click();expect(page.locator('#fontMenu')).to_be_visible();page.keyboard.press('Escape');page.locator('#themeToggle').click();expect(page.locator('#themeMenu')).to_be_visible();page.keyboard.press('Escape')
    record('Global search, notifications, AI entry and appearance menus',overlays)

    # Visual surface checks never submit a business form or alter fixture records.
    def modal_surfaces():
        count=0
        for role,routes in [('owner',['requests','staff','departments','reports']),('finance',['finance','income','expenses','operations']),('solo',['events','customers','suppliers','branches','imprest','daily_close','stock','bills','compliance','payroll','inventory','assets','fulfillment'])]:
            ctx.clear_cookies();go('/qa-session/'+role)
            for route in routes:
                go('/'+route)
                for modal_id in page.locator('.modal-backdrop[id]').evaluate_all('(es)=>es.map(e=>e.id)'):
                    if modal_id in ['requestModal','reportViewModal'] and route!='requests':continue
                    if not page.locator('#'+modal_id+' .modal-card').count():continue
                    page.evaluate('''id=>{const m=document.getElementById(id);document.body.append(m);m.classList.add('open');m.setAttribute('aria-hidden','false');document.body.classList.add('sage-modal-open');}''',modal_id);card=page.locator('#'+modal_id+' .modal-card');page.wait_for_timeout(40);r=card.bounding_box();ok(r and r['x']>=0 and r['y']>=0 and r['x']+r['width']<=1441 and r['height']<=890 and r['y']+r['height']<=901,role+'/'+route+'/'+modal_id+' '+str(r));ok(card.evaluate('(e)=>e.scrollWidth<=e.clientWidth+2'),'Modal horizontal overflow '+modal_id);count+=1
                    if modal_id in ['requestFundingModal','purchaseRecordModal','staffInviteModal','incomeEntryModal']:card.screenshot(path=str(OUT/('modal-'+modal_id+'.png')))
                    page.evaluate('''id=>{document.getElementById(id).classList.remove('open');document.getElementById(id).setAttribute('aria-hidden','true');document.body.classList.remove('sage-modal-open');document.documentElement.classList.remove('sage-modal-open');}''',modal_id)
                details=page.locator('details.v4-modal-disclosure').all()
                for detail in details[:6]:
                    detail.locator('summary').first.click();panel=page.locator('body>.v4-modal-panel.v4-dialog-live');expect(panel).to_be_visible();r=panel.bounding_box();ok(r['x']>=0 and r['y']>=0 and r['x']+r['width']<=1441 and r['height']<=900 and r['y']+r['height']<=901,'V4 modal bounds '+route+' '+str(r));ok(panel.evaluate('(e)=>e.scrollWidth<=e.clientWidth+2'),'V4 form horizontal overflow '+route);count+=1;page.keyboard.press('Escape');expect(panel).to_have_count(0)
        metrics['modal_surfaces']=count
    record('Desktop modal surfaces and native V4 form portals',modal_surfaces)
    record('No uncaught JavaScript errors',lambda:ok(not errors,str(errors)))
    browser.close()
print(json.dumps({'passed':sum(x['ok'] for x in checks),'total':len(checks),'metrics':metrics}),flush=True)
sys.exit(1 if any(not x['ok'] for x in checks) else 0)
