"""Onboarding, inline operational forms, money stress and exact-size captures."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright,expect
OUT=ROOT/'.qa';OUT.mkdir(exist_ok=True);BASE='http://127.0.0.1:5016';results=[]
def check(name,fn):
    try:fn();results.append({'name':name,'ok':True})
    except Exception as e:results.append({'name':name,'ok':False,'error':str(e)[:1400]})
    (OUT/'onboarding-stress.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(results[-1],flush=True)
def ok(condition,message):
    if not condition:raise AssertionError(message)
with sync_playwright() as p:
    browser=p.chromium.launch();context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce')
    context.route('https://fonts.googleapis.com/**',lambda r:r.abort());context.route('https://fonts.gstatic.com/**',lambda r:r.abort());page=context.new_page()
    def go(path):
        page.goto(BASE+path,wait_until='domcontentloaded');page.wait_for_timeout(220);page.add_style_tag(content='#sageLiveNotificationHost{opacity:0!important}#sageLiveNotificationHost *{pointer-events:none!important}')
    for mode in ['organization','individual']:
        def onboarding(mode=mode):
            go('/register');page.locator('[name=first_name]').fill('Mobile');page.locator('[name=last_name]').fill('QA');page.locator('[name=email]').fill('onboarding-'+mode+'@mobile-qa.test');page.locator('[name=password]').fill('isolated-mobile-qa-only')
            page.locator('.register-step.active [data-next-step]').click();page.locator('.workspace-mode-card:has(input[value="'+mode+'"])').click();page.locator('.register-step.active [data-next-step]').click()
            page.locator('[name=organization_name]').fill('Mobile QA '+mode)
            select=page.locator('#businessType' if mode=='organization' else '#individualBusinessType');ok(select.is_visible(),'Native business picker must be visible');select.select_option(index=1)
            page.locator('#organizationLogoInput').set_input_files(str(ROOT/'static/img/sage.png'));page.locator('.register-step.active [data-next-step]').click()
            expect(page.locator('.register-step.active')).to_have_attribute('data-step','4')
            for width in [320,390,430]:
                page.set_viewport_size({'width':width,'height':844});ok(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Onboarding overflow at '+str(width))
            page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/('onboarding-'+mode+'-step4.png')))
            # Exercise each welcome stage without creating a real user or delaying navigation.
            for stage in ['setup-stage','welcome-stage','handoff-stage']:
                page.evaluate('''stage=>{const e=document.getElementById('registrationSuccess');e.className='launch-overlay launch-premium-overlay open '+stage;e.setAttribute('aria-hidden','false');}''',stage)
                page.wait_for_timeout(60)
                ok(page.locator('.launch-premium-scene').evaluate('(e)=>e.getBoundingClientRect().width<=innerWidth'),'Welcome scene exceeds viewport')
                page.screenshot(path=str(OUT/('welcome-'+mode+'-'+stage+'.png')))
        check('Four-step '+mode+' onboarding, native picker, logo and welcome stages',onboarding)
    for role,routes in [('finance',['customers','daily_close','bills','payroll']),('solo',['customers','suppliers','branches','imprest','stock','events','bills','compliance','payroll'])]:
        go('/qa-session/'+role)
        for route in routes:
            def forms(route=route):
                go('/'+route);page.locator('details.control-disclosure').evaluate_all('(els)=>els.forEach(e=>e.open=true)');page.wait_for_timeout(100)
                bad=page.locator('.v4-form input,.v4-form select,.v4-form textarea').evaluate_all('''els=>els.filter(e=>e.getClientRects().length&&!e.closest('.table-wrap')&&e.type!=='hidden'&&e.type!=='checkbox'&&e.type!=='radio').filter(e=>{const r=e.getBoundingClientRect();return r.x<0||r.right>innerWidth+1||r.height<40}).map(e=>e.name)''')
                ok(not bad,'Operational form fields overflow or have small hit areas: '+str(bad))
            check(role+'/'+route+' inline operational fields',forms)
    go('/qa-session/owner')
    def money():
        go('/income')
        for width in [320,360,375,390,412,430,480,600,768,820]:
            page.set_viewport_size({'width':width,'height':844})
            for value in ['₦0','₦250,000.00','₦12,500,000.00','₦999,999,999,999.99']:
                for font in ['manrope','plus-jakarta','dm-sans','nunito-sans','outfit','urbanist','rubik','lato','source-sans','ibm-plex']:
                    page.evaluate('''({value,font})=>{document.documentElement.dataset.font=font;document.documentElement.dataset.fontSize='large';document.querySelectorAll('.income-kpi-grid strong').forEach(e=>e.textContent=value);}''',{'value':value,'font':font})
                    ok(page.locator('.income-kpi-grid strong').evaluate_all('(els)=>els.every(e=>e.scrollWidth<=e.clientWidth+1&&parseFloat(getComputedStyle(e).fontSize)>=20)'),'Money overflow at '+str((width,value,font)))
    check('400 amount, viewport and font combinations at Large text size',money)
    def captures():
        page.evaluate("localStorage.setItem('sage-font-size','medium')")
        for route in ['dashboard','requests','income','expenses','finance']:
            go('/'+route)
            for width,height in [(390,844),(430,932),(768,1024),(1440,900)]:
                page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(100);page.screenshot(path=str(OUT/('final-'+route+'-'+str(width)+'x'+str(height)+'.png')),animations='disabled')
    check('Exact 390x844, 430x932, 768x1024 and 1440x900 visual captures',captures)
    def fab():
        page.set_viewport_size({'width':390,'height':844});go('/dashboard');ok(not page.locator('#floatingAI').is_visible(),'Floating menu should start collapsed')
        page.locator('#mobileFabToggle').click();ok(page.locator('#floatingAI').is_visible(),'Floating actions must expand');page.locator('#floatingAI').click();expect(page.locator('#aiDrawer')).to_have_attribute('aria-hidden','false');page.keyboard.press('Escape')
    check('Compact floating action menu retains SAGE AI',fab)
    browser.close()
print(json.dumps({'checks':len(results),'failed':[r for r in results if not r['ok']]},indent=2));sys.exit(1 if any(not r['ok'] for r in results) else 0)
