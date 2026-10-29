"""Follow-up mobile regression checks. Uses only qa_mobile.py's temporary database.

AI responses are intercepted in Chromium; no external model request is made.
"""
import json, sys, time, traceback
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright, expect

BASE='http://127.0.0.1:5016'; OUT=ROOT/'.qa'; checks=[]; errors=[]; metrics={}
STILL='*,*::before,*::after{animation:none!important;transition:none!important}#sageLiveNotificationHost{opacity:0!important;pointer-events:none!important}'
def ok(value, message='Assertion failed'):
    if not value: raise AssertionError(message)
def record(name, fn):
    if '--mobile-only' in sys.argv and name.startswith('10 same-content'):return
    if '--only' in sys.argv and not any(part.lower() in name.lower() for part in sys.argv[sys.argv.index('--only')+1].split(',')):return
    try: fn(); result={'name':name,'ok':True}
    except Exception as e: result={'name':name,'ok':False,'error':str(e)[:1600],'trace':traceback.format_exc()[-1600:]}
    checks.append(result); print(json.dumps(result),flush=True)
    (OUT/'revision-checks.json').write_text(json.dumps({'checks':checks,'errors':errors,'metrics':metrics},indent=2),encoding='utf-8')

with sync_playwright() as p:
    browser=p.chromium.launch()
    ctx=browser.new_context(viewport={'width':390,'height':844},locale='en-NG',timezone_id='Africa/Lagos',reduced_motion='reduce',permissions=['clipboard-read','clipboard-write'])
    ctx.route('https://fonts.googleapis.com/**',lambda r:r.abort());ctx.route('https://fonts.gstatic.com/**',lambda r:r.abort())
    ctx.route('**/api/activity/page-view',lambda r:r.fulfill(json={'ok':True}))
    page=ctx.new_page();page.set_default_timeout(6000);page.on('pageerror',lambda e:errors.append(str(e)))
    def go(route):
        response=page.goto(BASE+route,wait_until='domcontentloaded',timeout=30000);ok(response.status==200,str(response.status));page.wait_for_timeout(180);page.add_style_tag(content=STILL)
    def shot(name, selector=None):
        if selector: page.locator(selector).first.scroll_into_view_if_needed();page.wait_for_timeout(50)
        page.screenshot(path=str(OUT/('revision-'+name+'.png')))
    def visible_rows(): return page.locator('[data-audit-row]:visible')
    go('/qa-session/owner')

    def layouts():
        for route in ['staff','audit','workspace']:
            go('/'+route)
            for width in [320,360,375,390,412,430,480,600,768,820,900]:
                page.set_viewport_size({'width':width,'height':844});page.wait_for_timeout(30)
                ok(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),f'{route} overflow {width}')
                if route=='workspace':
                    cards=page.locator('.role-stats>.mini-stat').evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height,e.scrollWidth<=e.clientWidth+1]})')
                    ok(len(cards)==4 and min(c[2] for c in cards)>110,str(cards));ok(cards[0][1]==cards[1][1] and cards[2][1]==cards[3][1],str(cards));ok(all(c[4] for c in cards),str(cards))
                elif route=='staff':
                    row=page.locator('[data-staff-row]').filter(has_text='Tayo Aderonke').first
                    bounds=row.locator('td').evaluate_all('(els)=>els.slice(0,4).map(e=>({x:e.getBoundingClientRect().x,w:e.getBoundingClientRect().width,sw:e.scrollWidth,cw:e.clientWidth}))')
                    ok(bounds[1]['w']>=220 and bounds[2]['w']>=195,str(bounds));ok(bounds[1]['x']+bounds[1]['w']<=bounds[2]['x']+1,str(bounds))
                    ok(row.locator('.staff-table-person').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),'staff identity overflow')
                else:
                    ok(page.locator('.audit-ledger').evaluate('(e)=>getComputedStyle(e).display')=='table')
                    ok(visible_rows().count()==25,'25 audit rows expected')
                    ok(page.locator('.audit-filter-grid').evaluate('(e)=>e.clientHeight')<=85,'Filter shelf too tall')
                    ok(page.locator('select[data-audit-category]').evaluate('(e)=>e.getBoundingClientRect().height')<=38,'Category too tall')
            page.set_viewport_size({'width':390,'height':844})
            shot(route+'-detail',{'staff':'.staff-table-wrap','audit':'.audit-command-panel','workspace':'.role-stats'}[route])
            if route=='audit': shot('audit-ledger','.audit-timeline-panel')
        page.set_viewport_size({'width':390,'height':844})
    record('33 mobile layout states: Staff columns, compact Audit filters/table, Workspace 2x2',layouts)

    def staff_controls():
        go('/staff');total=page.locator('[data-staff-row]').count()
        page.locator('[data-staff-search]').fill('Tayo');expect(page.locator('[data-staff-match-count]')).to_have_text(f'15 of {total} accounts')
        page.locator('[data-staff-clear]').click();expect(page.locator('[data-staff-match-count]')).to_have_text(f'{total} of {total} accounts')
        page.locator('[data-staff-sort]').click();names=page.locator('.staff-table-person strong').all_text_contents();ok(names==sorted(names,key=str.lower),str(names[:6]))
        box=page.locator('[data-staff-select]').first;box.check();ok(box.locator('xpath=ancestor::tr').locator('td').first.evaluate('(e)=>getComputedStyle(e).backgroundColor')!='rgba(0, 0, 0, 0)');expect(page.locator('[data-staff-bulk-bar]')).to_have_attribute('data-selected','true');box.uncheck()
        wrap=page.locator('.staff-table-wrap');wrap.evaluate('(e)=>e.scrollLeft=0');wrap.locator('button[aria-label="Next columns"]').click();page.wait_for_timeout(80);ok(wrap.evaluate('(e)=>e.scrollLeft')>0)
        wrap.focus();page.keyboard.press('End');ok(wrap.evaluate('(e)=>e.scrollLeft')>500,'End column shortcut');page.keyboard.press('Home');page.wait_for_timeout(50);ok(wrap.evaluate('(e)=>e.scrollLeft')<=8,'Home column shortcut must reach first column, allowing wrapper inset')
    record('Staff sorting, result count, clear, selection and ledger column controls',staff_controls)

    def audit_controls():
        go('/audit');total=int(page.locator('[data-audit-visible-count]').inner_text());ok(total==600,str(total));first=visible_rows().first.get_attribute('data-audit-ts')
        page.locator('[data-audit-next]').click();ok('2 /' in page.locator('[data-audit-page-status]').inner_text());ok(first!=visible_rows().first.get_attribute('data-audit-ts'))
        page.locator('[data-audit-page-size]').select_option('50');ok(visible_rows().count()==50)
        page.locator('[data-audit-page-size]').select_option('100');ok(visible_rows().count()==100)
        page.locator('[data-audit-sort]').click();ok(page.locator('[data-audit-sort]').locator('xpath=..').get_attribute('aria-sort')=='ascending');expect(page.locator('.audit-timeline-panel>.panel-head>.status')).to_have_text('Oldest first');ok(first>visible_rows().first.get_attribute('data-audit-ts'))
        page.locator('[data-audit-search]').fill('QA-20 Sales');expect(page.locator('[data-audit-visible-count]')).to_have_text('1');ok(visible_rows().count()==1)
        expect(page.locator('[data-audit-chips] button')).to_have_count(1);page.locator('[data-audit-chips] button').click();expect(page.locator('[data-audit-visible-count]')).to_have_text('600')
        category=page.locator('select[data-audit-category] option').nth(1).get_attribute('value');page.locator('select[data-audit-category]').select_option(category);ok(int(page.locator('[data-audit-visible-count]').inner_text())<600)
        page.locator('[data-audit-clear]').click();expect(page.locator('[data-audit-visible-count]')).to_have_text('600');page.locator('[data-audit-period="today"]').click();ok(page.locator('[data-audit-from]').input_value()!='')
        page.locator('[data-audit-search]').fill('nothing-can-match-qa');expect(page.locator('[data-audit-empty]')).to_be_visible();page.locator('[data-audit-clear]').click()
        page.set_viewport_size({'width':1440,'height':900});page.wait_for_timeout(60);ok(visible_rows().count()==600,'Desktop must show all matching rows')
        page.locator('[data-audit-search]').fill('QA-20 Sales');expect(page.locator('[data-audit-visible-count]')).to_have_text('1');ok(visible_rows().count()==1,'Desktop filtered rows visible');page.set_viewport_size({'width':390,'height':844})
    record('Audit all-event search, paging 25/50/100, sorting, chips, presets, empty and desktop filtering',audit_controls)

    def navigation():
        page.evaluate("sessionStorage.removeItem('sage-recent:'+SAGE_USER.id)");go('/workspace');page.locator('#mobileMenu').click();ok(page.locator('#sidebar').bounding_box()['width']<=280)
        ok(page.locator('.mobile-nav-search').bounding_box()['height']<=46,'Navigation search must remain one compact row')
        ok(page.locator('.nav-section-icon:visible').count()==5)
        for button in page.locator('[data-nav-section].open [data-nav-section-toggle]').all():button.click()
        shot('sidebar-final')
        page.locator('#mobileNavSearch').fill('audit');expect(page.locator('#mobileNavCount')).to_have_text('1 matching page');page.keyboard.press('Enter');expect(page.locator('body')).to_have_attribute('data-page','audit');expect(page.locator('#mobileMenu')).to_have_attribute('aria-expanded','false')
        page.locator('#mobileMenu').click();expect(page.locator('#mobileNavRecents a')).to_have_count(1);page.locator('#mobileNavClear').click();ok(page.locator('.nav-section-icon:visible').count()==5);page.keyboard.press('Escape')
        page.locator('#mobileToolsToggle').click();page.locator('[data-mobile-previous]').click();expect(page.locator('body')).to_have_attribute('data-page','workspace');ok(page.locator('#mobileToolsPanel').is_hidden())
        page.set_viewport_size({'width':1440,'height':900});ok(page.locator('.nav-section-icon:visible').count()==5);page.set_viewport_size({'width':390,'height':844})
        go('/income');wrap=page.locator('.money-table-scroll');wrap.evaluate('(e)=>e.scrollLeft=360');page.evaluate("window.scrollTo({top:350,behavior:'instant'})");saved=page.evaluate('scrollY');x=wrap.evaluate('(e)=>e.scrollLeft')
        page.evaluate("SAGENavigate('expenses')");expect(page.locator('body')).to_have_attribute('data-page','expenses');page.go_back();expect(page.locator('body')).to_have_attribute('data-page','income');page.wait_for_timeout(150)
        ok(abs(page.evaluate('scrollY')-saved)<3,'Back scroll position');ok(abs(page.locator('.money-table-scroll').evaluate('(e)=>e.scrollLeft')-x)<3,'Back column position')
        staff_ctx=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');staff_ctx.route('https://fonts.googleapis.com/**',lambda r:r.abort());staff_ctx.route('https://fonts.gstatic.com/**',lambda r:r.abort());staff_page=staff_ctx.new_page();staff_page.goto(BASE+'/qa-session/staff',wait_until='domcontentloaded');expect(staff_page.locator('body')).to_have_attribute('data-user-role','staff');staff_page.locator('#mobileMenu').click();staff_page.locator('#mobileNavSearch').fill('audit');expect(staff_page.locator('#mobileNavCount')).to_have_text('0 matching pages');staff_ctx.close()
    record('Narrow icon drawer, quicksearch, recents, previous, back scroll/columns and permitted results',navigation)

    ai_mode={'value':'success'};requests=[]
    ANSWER='# Finance review\n- **Income** ₦250,000.00\n- Check `QA-500` and expenses.\n<img src=x onerror=alert(1)>\n'+('\n'.join('- Review accountable record '+str(i) for i in range(20)))
    pending=[]
    def ai_route(route):
        requests.append(route.request.post_data_json)
        if ai_mode['value']=='pending':pending.append(route);return
        if ai_mode['value']=='error':route.fulfill(status=503,json={'ok':False,'message':'QA connection unavailable'});return
        route.fulfill(json={'ok':True,'answer':ANSWER,'model':'QA local response'})
    page.route('**/api/ai/chat',ai_route)
    def ai_geometry():
        go('/dashboard');page.locator('#aiOpen').click()
        for width,height in [(320,568),(390,844),(430,932),(768,1024),(844,390),(1024,768),(1440,900),(1920,1080),(390,420)]:
            page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(40)
            r=page.locator('#aiDrawer').bounding_box();close=page.locator('#aiClose').bounding_box();composer=page.locator('#aiForm').bounding_box()
            ok(r['x']>=0 and r['y']>=0 and r['x']+r['width']<=width and r['y']+r['height']<=height+1,str(r));ok(r['width']<=460)
            ok(close['y']>=0 and close['y']+close['height']<=height,'Close outside view');ok(composer['y']+composer['height']<=height,'Composer outside view')
            ok(page.locator('#aiDrawer').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),'Chat horizontal overflow')
            ok(page.locator('#aiBackdrop').evaluate('(e)=>getComputedStyle(e).backdropFilter')=='none')
            ok(page.locator('#appContent').evaluate('(e)=>getComputedStyle(e).filter')=='none')
        page.set_viewport_size({'width':390,'height':844});shot('ai-mobile');page.evaluate("Object.defineProperty(visualViewport,'height',{get:()=>360,configurable:true});visualViewport.dispatchEvent(new Event('resize'))");page.wait_for_timeout(50);ok(page.locator('#aiDrawer').evaluate('(e)=>e.classList.contains("ai-compact-height")'));ok(page.locator('#aiForm').bounding_box()['y']+page.locator('#aiForm').bounding_box()['height']<=360,'Visual viewport keyboard composer');page.evaluate("delete visualViewport.height;visualViewport.dispatchEvent(new Event('resize'))");page.set_viewport_size({'width':1440,'height':900});shot('ai-desktop');page.keyboard.press('Escape');ok(page.locator('#aiOpen').evaluate('(e)=>e===document.activeElement'));page.set_viewport_size({'width':390,'height':844})
    record('AI bounded in 9 portrait/landscape/desktop/keyboard sizes, reachable close/composer, no blur',ai_geometry)

    def ai_interactions():
        page.locator('#aiOpen').click();page.locator('#aiInput').fill('Unsent draft');page.keyboard.press('Enter');ok(page.locator('#aiInput').input_value()=='Unsent draft\n','Mobile Enter must make newline');page.locator('#aiClose').click();page.reload(wait_until='domcontentloaded');page.wait_for_timeout(120);page.add_style_tag(content=STILL);page.locator('#aiOpen').click();ok(page.locator('#aiInput').input_value()=='Unsent draft\n','Draft did not survive reload')
        page.locator('#aiInput').fill('Review finance');page.locator('#aiForm button[type=submit]').click();expect(page.locator('#aiState span')).to_have_text('Reply ready')
        ok(page.locator('#aiForm').bounding_box()['y']+page.locator('#aiForm').bounding_box()['height']<844,'Composer must stay reachable with suggestions hidden and long answers');shot('ai-reply-mobile')
        ok(page.locator('.ai-answer h4').count()==1,'Heading format');ok(page.locator('.ai-answer li strong').count()==1,'Bold format');ok(page.locator('.ai-answer mark').count()>=1,'Currency highlight');ok(page.locator('.ai-answer img').count()==0,'Escaped HTML');ok(page.locator('.ai-answer code').count()==1,'Code format')
        msg=page.locator('#aiMessages');msg.evaluate('(e)=>e.scrollTop=0');expect(page.locator('#aiJumpLatest')).to_be_visible();page.locator('#aiJumpLatest').click();page.wait_for_timeout(60);ok(msg.evaluate('(e)=>e.scrollHeight-e.scrollTop-e.clientHeight')<10)
        page.locator('.ai-message.assistant [data-copy-message]').last.click();expect(page.locator('.ai-message.assistant [data-copy-message]').last).to_have_attribute('aria-label','Message copied');ok(page.evaluate('navigator.clipboard.readText()').replace('\r\n','\n')==ANSWER,'Copy full answer (Windows line endings normalized)')
        ai_mode['value']='pending';page.locator('#aiInput').fill('Let me read earlier messages');page.locator('#aiForm button[type=submit]').click();expect(page.locator('#aiStop')).to_be_visible();page.wait_for_timeout(50);msg.evaluate('(e)=>e.scrollTop=0');pending.pop().fulfill(json={'ok':True,'answer':ANSWER,'model':'QA local response'});expect(page.locator('#aiState span')).to_have_text('Reply ready');ok(msg.evaluate('(e)=>e.scrollTop')<20,'Incoming reply must preserve reading position');expect(page.locator('#aiJumpLatest')).to_be_visible();page.locator('#aiJumpLatest').click()
        ai_mode['value']='error';page.locator('#aiInput').fill('Retry me');page.locator('#aiForm button[type=submit]').click();expect(page.locator('[data-ai-retry]')).to_be_visible();expect(page.locator('#aiState')).to_have_attribute('data-state','error')
        ai_mode['value']='success';page.locator('[data-ai-retry]').click();expect(page.locator('#aiState span')).to_have_text('Reply ready');ok(requests[-1]['message']=='Retry me');ok(not any(x['content']=='Retry me' for x in requests[-1]['history']),'Retry duplicated context')
        ai_mode['value']='pending';page.locator('#aiInput').fill('Stop this');page.locator('#aiForm button[type=submit]').click();expect(page.locator('#aiStop')).to_be_visible();ok(page.locator('#aiForm button[type=submit]').is_disabled());page.locator('#aiStop').click();expect(page.locator('#aiState span')).to_have_text('Stopped');ok(page.locator('#aiForm button[type=submit]').is_enabled())
        for route in pending:
            try:route.abort()
            except Exception:pass
        ai_mode['value']='success';page.set_viewport_size({'width':1440,'height':900});page.locator('#aiInput').fill('Desktop Enter');page.keyboard.press('Enter');expect(page.locator('#aiState span')).to_have_text('Reply ready');ok(requests[-1]['message']=='Desktop Enter')
        page.locator('#aiClose').focus();page.keyboard.press('Shift+Tab');ok(page.locator('#aiDrawer').evaluate('(e)=>e.contains(document.activeElement)'));page.keyboard.press('Escape');ok(not page.locator('#appContent').evaluate('(e)=>e.inert'));page.set_viewport_size({'width':390,'height':844})
    record('AI draft, mobile newline/desktop send, formatted escaped answers, copy, latest, retry, Stop and focus',ai_interactions)

    def pulse():
        go('/dashboard');page.wait_for_timeout(1000);page.add_style_tag(content='#sageLiveNotificationHost{opacity:1!important;pointer-events:auto!important}')
        page.evaluate("document.querySelector('#sageLiveNotification').classList.add('show');document.querySelector('#sageLiveTitle').textContent='Good morning, Owner.';document.querySelector('#sageLiveMessage').textContent='Here is the live status for your organization. Review outstanding actions and accountable records.';document.querySelector('#sageLiveMetric').hidden=false;document.querySelector('#sageLiveMetric').textContent='3 actions need attention'")
        card=page.locator('#sageLiveNotification');r=card.bounding_box();fab=page.locator('#mobileFabToggle').bounding_box();ok(r['width']<=264,str(r));ok(r['x']+r['width']<=fab['x'],str((r,fab)));ok(844-(r['y']+r['height'])<=12,str(r))
        shot('pulse');before=r['height'];page.locator('#sageLiveMinimize').click();ok(card.bounding_box()['height']<before);ok(page.locator('#sageLiveMinimize').get_attribute('aria-expanded')=='false');page.locator('#sageLiveMinimize').click();ok(card.bounding_box()['height']>=before)
    record('Pulse bottom placement, 264px max width, clear FAB and minimize/expand',pulse)

    def performance():
        times={}
        for route in ['audit','staff','departments','branches','payroll']:
            go('/'+route);page.wait_for_timeout(600);start=time.perf_counter();page.locator('#mobileMenu').click();page.wait_for_function("document.querySelector('#mobileMenu').getAttribute('aria-expanded')==='true'");page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');times[route]=round((time.perf_counter()-start)*1000);ok(times[route]<1800,f'{route}: {times[route]}ms');page.keyboard.press('Escape')
        metrics['drawer_ms']=times
        cdp=ctx.new_cdp_session(page);cdp.send('Emulation.setCPUThrottlingRate',{'rate':4});go('/audit');page.wait_for_timeout(500);start=time.perf_counter();page.locator('#mobileMenu').click();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');metrics['audit_drawer_4x_cpu_ms']=round((time.perf_counter()-start)*1000);ok(metrics['audit_drawer_4x_cpu_ms']<1800,str(metrics));cdp.send('Emulation.setCPUThrottlingRate',{'rate':1});page.keyboard.press('Escape')
    record('Populated organization sidebar response including 4x CPU slowdown',performance)

    # Same database content and original assets/templates for desktop geometry.
    def desktop():
        before=ctx.new_page();before.set_default_timeout(6000);before.add_init_script('window.setInterval=()=>0')
        def old_asset(route):
            path=ROOT/'.qa/revision_before'/urlparse(route.request.url).path.lstrip('/')
            if path.is_file(): route.fulfill(path=str(path))
            else: route.continue_()
        before.route('**/static/**',old_asset);before.set_viewport_size({'width':1440,'height':900});page.set_viewport_size({'width':1440,'height':900})
        measure='''()=>[...document.querySelectorAll('main .page-heading,main .panel,main .stat-card,main .role-stats,main .mini-stat,main .data-table,main .audit-event')].map(e=>{const r=e.getBoundingClientRect();return [[...e.classList].sort().join(' '),...['x','y','width','height'].map(k=>Math.round(r[k]*10)/10)]})'''
        diffs={}
        for route in ['dashboard','income','expenses','finance','requests','workspace','staff','departments','audit','settings']:
            print('Desktop comparison: '+route,flush=True);response=before.goto(BASE+'/qa-before/'+route,wait_until='domcontentloaded',timeout=30000);ok(response.status==200,str(response.status));before.wait_for_timeout(220);before.add_style_tag(content=STILL);go('/'+route)
            a=before.evaluate(measure);b=page.evaluate(measure)
            if a!=b:diffs[route]={'before':a,'after':b}
        (OUT/'revision-desktop-differences.json').write_text(json.dumps(diffs,indent=2),encoding='utf-8');metrics['desktop_pages']=10;metrics['desktop_differences']=list(diffs);before.close();ok(not diffs,'Desktop geometry differences: '+str(list(diffs)))
    if (OUT/'revision_before/templates/app_shell.html').exists():record('10 same-content desktop page geometry comparisons',desktop)
    record('No uncaught browser JavaScript errors',lambda:ok(not errors,str(errors)))
    browser.close()
print(json.dumps({'passed':sum(c['ok'] for c in checks),'total':len(checks),'metrics':metrics}),flush=True)
sys.exit(1 if any(not c['ok'] for c in checks) else 0)
