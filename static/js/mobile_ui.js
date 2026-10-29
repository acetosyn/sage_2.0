(()=>{'use strict';
  // ==========================================================
  // MOBILE INTERACTIONS ONLY — CSS owns every responsive size.
  // No font measurement, body sizing modes or table conversion.
  // ==========================================================
  const mq=matchMedia('(max-width:900px)'),q=(s,r=document)=>r.querySelector(s),qa=(s,r=document)=>[...r.querySelectorAll(s)];
  const side=q('#sidebar'),opener=q('#mobileMenu'),tools=q('#mobileToolsPanel'),toolsToggle=q('#mobileToolsToggle');
  const focusables=root=>qa('a[href],button:not([disabled]),input:not([disabled]):not([type=hidden]),select:not([disabled]),textarea:not([disabled]),[tabindex="0"]',root).filter(el=>el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden'&&!el.closest('[inert]'));
  let drawerWasOpen=false;
  function closeTools(restore=false){if(tools)tools.hidden=true;toolsToggle?.setAttribute('aria-expanded','false');if(restore)toolsToggle?.focus({preventScroll:true});}
  toolsToggle?.addEventListener('click',event=>{event.stopPropagation();const open=tools.hidden;tools.hidden=!open;toolsToggle.setAttribute('aria-expanded',String(open));if(open)q('button',tools)?.focus({preventScroll:true});});
  tools?.addEventListener('click',event=>{const button=event.target.closest('[data-mobile-control]');if(!button)return;event.stopPropagation();closeTools();document.getElementById(button.dataset.mobileControl)?.click();});
  document.addEventListener('click',event=>{if(!event.target.closest('#mobileToolsPanel,#mobileToolsToggle'))closeTools();});
  q('.top-avatar')?.addEventListener('click',()=>{if(mq.matches)q('.nav-link[data-route="settings"]')?.click();});

  const fab=q('#mobileFabToggle'),floats=q('.floating-actions');
  function closeFab(){floats?.classList.remove('mobile-fab-open');fab?.setAttribute('aria-expanded','false');}
  fab?.addEventListener('click',event=>{event.stopPropagation();const open=!floats.classList.contains('mobile-fab-open');floats.classList.toggle('mobile-fab-open',open);fab.setAttribute('aria-expanded',String(open));});
  document.addEventListener('click',event=>{if(!event.target.closest('#mobileFabToggle'))closeFab();});

  // Drawer focus, inert background, scroll lock and reliable desktop restoration.
  function syncDrawer(){
    if(!side)return;const open=mq.matches&&document.body.classList.contains('mobile-nav-open');
    side.inert=document.body.classList.contains('sage-ai-open')||(mq.matches&&!open);opener?.setAttribute('aria-expanded',String(open));
    if(mq.matches){side.setAttribute('aria-hidden',String(!open));if(open){side.setAttribute('role','dialog');side.setAttribute('aria-modal','true');side.setAttribute('aria-label','SAGE navigation');}else{side.removeAttribute('role');side.removeAttribute('aria-modal');}}
    else{side.removeAttribute('aria-hidden');side.removeAttribute('role');side.removeAttribute('aria-modal');side.removeAttribute('aria-label');}
    qa('#appContent,.topbar,.floating-actions').forEach(el=>el.inert=open||document.body.classList.contains('sage-ai-open'));
    if(open&&!drawerWasOpen){closeTools();q('#mobileClose')?.focus({preventScroll:true});}
    if(!open&&drawerWasOpen&&mq.matches)opener?.focus({preventScroll:true});drawerWasOpen=open;
  }
  new MutationObserver(syncDrawer).observe(document.body,{attributes:true,attributeFilter:['class']});
  mq.addEventListener('change',()=>{if(!mq.matches)document.body.classList.remove('mobile-nav-open');closeTools();closeFab();syncDrawer();syncDialogs();});syncDrawer();

  // Closed overlays must not be keyboard stops. Inline disclosure forms stay
  // accessible on phones; their desktop-only portal metadata must not hide them.
  function syncDialogs(){
    qa('.form-message').forEach(message=>{message.setAttribute('role','status');message.setAttribute('aria-live','polite');});
    qa('.modal-head [data-close-modal]').forEach(button=>{if(!button.hasAttribute('aria-label'))button.setAttribute('aria-label','Close dialog');});
    qa('.modal-backdrop').forEach(modal=>{modal.inert=!modal.classList.contains('open');if(modal.classList.contains('open')&&mq.matches){modal.setAttribute('role','dialog');modal.setAttribute('aria-modal','true');const heading=q('h2,h3',modal);if(heading){heading.id||=`mobile-dialog-${modal.id}`;modal.setAttribute('aria-labelledby',heading.id);}}});
    if(mq.matches)qa('.v4-modal-disclosure>.v4-modal-panel').forEach(panel=>{panel.removeAttribute('aria-hidden');panel.removeAttribute('aria-modal');panel.setAttribute('role','group');});
  }
  const bound=new Map(),resize=window.ResizeObserver?new ResizeObserver(entries=>entries.forEach(e=>bound.get(e.target)?.())):null;let frame=0;
  function bindScrollRegions(){
    for(const wrap of bound.keys())if(!wrap.isConnected){resize?.unobserve(wrap);bound.delete(wrap);}
    qa('.table-scroll,.table-scroller,.table-wrap,.finance-workbook-scroll,.money-table-scroll,.history-ledger-scroll,.request-ledger-scroll,.staff-history-scroll,.report-table-scroll,.platform-table-shell').forEach(wrap=>{
      if(bound.has(wrap))return;wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Data register. Swipe horizontally or use the arrow keys to view all columns.');
      const sync=()=>{wrap.classList.toggle('m-scroll-left',mq.matches&&wrap.scrollLeft>2);wrap.classList.toggle('m-scroll-right',mq.matches&&wrap.scrollLeft+wrap.clientWidth<wrap.scrollWidth-2);};
      qa('th',wrap).forEach(th=>{if(!th.hasAttribute('scope'))th.setAttribute('scope','col');});
      bound.set(wrap,sync);wrap.addEventListener('scroll',sync,{passive:true});resize?.observe(wrap);sync();
    });
  }
  function refresh(){cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{syncDialogs();bindScrollRegions();});}
  new MutationObserver(mutations=>{if(mutations.some(m=>(m.type==='childList'&&!m.target.closest?.('[data-ui-static]')&&[...m.addedNodes].some(n=>n.nodeType===1))||m.target.matches?.('.modal-backdrop')))refresh();}).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
  document.addEventListener('keydown',event=>{
    if(!mq.matches)return;
    if(event.key==='Escape'){closeFab();const appearance=qa('.font-menu.open,.theme-menu.open');if(!tools?.hidden||appearance.length){closeTools(true);appearance.forEach(menu=>{menu.classList.remove('open');menu.setAttribute('aria-hidden','true');});q('#fontToggle')?.setAttribute('aria-expanded','false');q('#themeToggle')?.setAttribute('aria-expanded','false');}return;}
    if(event.key!=='Tab')return;
    const root=qa('.modal-backdrop.open').at(-1)||(drawerWasOpen?side:tools&&!tools.hidden?tools:null);if(!root)return;
    const nodes=focusables(root),first=nodes[0],last=nodes.at(-1);if(!first){event.preventDefault();return;}
    if(event.shiftKey&&(document.activeElement===first||!root.contains(document.activeElement))){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&(document.activeElement===last||!root.contains(document.activeElement))){event.preventDefault();first.focus();}
  });
  refresh();
})();
