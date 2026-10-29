"""Sample the desktop design tokens in every offered theme, with browser-resolved colors."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.qa-deps'))
from playwright.sync_api import sync_playwright,expect
OUT=ROOT/'.qa/desktop';rows=[]
JS="""()=>{const canvas=document.createElement('canvas'),c=canvas.getContext('2d',{willReadFrequently:true}),s=document.createElement('span');document.body.append(s);function rgb(value){s.style.color=value;c.clearRect(0,0,1,1);c.fillStyle=getComputedStyle(s).color;c.fillRect(0,0,1,1);return [...c.getImageData(0,0,1,1).data].slice(0,3)}function lum(a){return a.map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((a,x,i)=>a+x*[.2126,.7152,.0722][i],0)}const pairs=[['body','--desktop-ink','--desktop-canvas'],['muted','--desktop-muted','--desktop-surface'],['muted-subtle','--desktop-muted','--desktop-subtle'],['accent','--desktop-accent-ink','--desktop-accent-soft'],['positive','--desktop-positive-ink','--desktop-surface'],['negative','--desktop-negative-ink','--desktop-surface'],['warning','--desktop-warning-ink','--desktop-surface'],['action',null,'--desktop-action']];const result=pairs.map(([name,fg,bg])=>{const a=rgb(fg?'var('+fg+')':'#fff'),b=rgb('var('+bg+')'),aa=lum(a),bb=lum(b);return {name,fg:a,bg:b,ratio:Math.round((Math.max(aa,bb)+.05)/(Math.min(aa,bb)+.05)*100)/100}});s.remove();return result}"""
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(viewport={'width':1440,'height':900});c.route('https://fonts.googleapis.com/**',lambda r:r.abort());c.route('https://fonts.gstatic.com/**',lambda r:r.abort());q=c.new_page();q.goto('http://127.0.0.1:5016/qa-session/owner',wait_until='domcontentloaded');expect(q.locator('html')).to_have_attribute('data-sage-style-mode','desktop');themes=q.locator('[data-theme-choice]').evaluate_all('(es)=>es.map(e=>e.dataset.themeChoice)')
    for page in ['income','expenses','customers','bills']:
        q.goto('http://127.0.0.1:5016/'+page,wait_until='domcontentloaded')
        for theme in themes:
            q.evaluate('t=>document.documentElement.dataset.theme=t',theme);rows.append({'page':page,'theme':theme,'pairs':q.evaluate(JS)})
    b.close()
failures=[{'page':r['page'],'theme':r['theme'],**x} for r in rows for x in r['pairs'] if x['ratio']<4.5];(OUT/'contrast.json').write_text(json.dumps({'states':rows,'failures':failures},indent=2),encoding='utf-8');print(json.dumps({'states':len(rows),'pairs':len(rows)*8,'failures':failures}));sys.exit(1 if failures else 0)
