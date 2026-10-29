(()=>{'use strict';
  // ==========================================================
  // MOBILE REFINEMENTS — page-scoped interaction, no sizing loop.
  // ==========================================================
  const q=(s,r=document)=>r.querySelector(s),qa=(s,r=document)=>[...r.querySelectorAll(s)],mobile=matchMedia('(max-width:900px)'),reduced=matchMedia('(prefers-reduced-motion:reduce)');
  const side=q('#sidebar'),navLinks=qa('.nav-link[data-route]'),sections=qa('[data-nav-section]'),search=q('#mobileNavSearch'),count=q('#mobileNavCount'),recents=q('#mobileNavRecents'),recentKey=`sage-recent:${window.SAGE_USER?.id||'session'}`;
  let lastPage=document.body.dataset.page,previousPage='',recent=[];try{recent=JSON.parse(sessionStorage.getItem(recentKey)||'[]');}catch(_){}
  function navigate(page){if(navLinks.some(link=>link.dataset.route===page))window.SAGENavigate?.(page);}
  function renderRecents(){
    const page=document.body.dataset.page;recent=[page,...recent.filter(p=>p!==page&&navLinks.some(link=>link.dataset.route===p))].slice(0,6);try{sessionStorage.setItem(recentKey,JSON.stringify(recent));}catch(_){}
    if(recents){recents.replaceChildren();for(const route of recent.filter(p=>p!==page).slice(0,3)){const source=navLinks.find(link=>link.dataset.route===route),link=document.createElement('a');link.href='/'+route;link.dataset.route=route;link.textContent=source.dataset.label||source.textContent.trim();link.title='Recent: '+link.textContent;recents.append(link);}}
    const previous=q('[data-mobile-previous]');if(previous)previous.disabled=!previousPage&&!recent.some(p=>p!==page);
  }
  function filterNav(){
    const value=(search?.value||'').trim().toLowerCase();side?.classList.toggle('nav-searching',Boolean(value));let visible=0;
    for(const link of navLinks){const match=!value||(link.dataset.label||link.textContent).toLowerCase().includes(value);link.hidden=!match;if(match)visible++;}
    for(const section of sections){const has=qa('.nav-link',section).some(link=>!link.hidden);section.hidden=!has;const open=value&&has?true:section.classList.contains('open');q('[data-nav-section-toggle]',section)?.setAttribute('aria-expanded',String(open));q('[data-nav-section-group]',section)?.setAttribute('aria-hidden',String(!open));}
    if(count)count.textContent=value?`${visible} matching page${visible===1?'':'s'}`:'Search your permitted pages';
  }
  search?.addEventListener('input',filterNav);q('#mobileNavClear')?.addEventListener('click',()=>{search.value='';filterNav();search.focus({preventScroll:true});});search?.addEventListener('keydown',event=>{if(event.key==='Enter'){const first=navLinks.find(link=>!link.hidden);if(first){event.preventDefault();navigate(first.dataset.route);}}});
  q('[data-mobile-previous]')?.addEventListener('click',()=>{const page=previousPage||recent.find(p=>p!==document.body.dataset.page);if(!page)return;const menu=q('#mobileToolsPanel');if(menu)menu.hidden=true;q('#mobileToolsToggle')?.setAttribute('aria-expanded','false');if(history.state?.page===document.body.dataset.page)history.back();else navigate(page);});

  // One observer and explicit teardown for SPA scroll regions.
  const ledgers=new Map(),resize=window.ResizeObserver?new ResizeObserver(entries=>entries.forEach(e=>ledgers.get(e.target)?.sync())):null;
  const ledgerSelector='.table-scroll,.table-scroller,.table-wrap,.finance-workbook-scroll,.money-table-scroll,.history-ledger-scroll,.request-ledger-scroll,.staff-history-scroll,.report-table-scroll,.audit-feed';
  function bindLedgers(){
    for(const wrap of ledgers.keys())if(!wrap.isConnected){resize?.unobserve(wrap);ledgers.delete(wrap);}
    qa(ledgerSelector,q('#appContent')||document).forEach((wrap,index)=>{
      if(ledgers.has(wrap)||!q('table',wrap))return;const controls=document.createElement('div');controls.className='mobile-ledger-jumps mobile-only';controls.setAttribute('aria-label','Scroll register columns');
      wrap.id||=`mobile-ledger-${document.body.dataset.page}-${index}`;wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Data register. Swipe columns or use Left, Right, Home and End.');
      const buttons=[-1,1].map(direction=>{const button=document.createElement('button');button.type='button';button.textContent=direction<0?'‹':'›';button.setAttribute('aria-label',direction<0?'Previous columns':'Next columns');button.setAttribute('aria-controls',wrap.id);button.addEventListener('click',()=>wrap.scrollBy({left:direction*Math.max(140,wrap.clientWidth*.65),behavior:reduced.matches?'auto':'smooth'}));controls.append(button);return button;});
      wrap.insertBefore(controls,q('table',wrap));const sync=()=>{const max=Math.max(0,wrap.scrollWidth-wrap.clientWidth);controls.hidden=!mobile.matches||max<3;buttons[0].disabled=wrap.scrollLeft<3;buttons[1].disabled=wrap.scrollLeft>=max-3;wrap.classList.toggle('m-can-scroll',max>3);};
      wrap.addEventListener('scroll',sync,{passive:true});wrap.addEventListener('keydown',event=>{if(event.target!==wrap||!mobile.matches)return;if(['Home','End','ArrowLeft','ArrowRight'].includes(event.key)){event.preventDefault();if(event.key==='Home')wrap.scrollLeft=0;else if(event.key==='End')wrap.scrollLeft=wrap.scrollWidth;else wrap.scrollBy({left:event.key==='ArrowLeft'?-144:144,behavior:reduced.matches?'auto':'smooth'});}});ledgers.set(wrap,{sync});resize?.observe(wrap);sync();
    });
  }

  // Audit filters search all retained rows; phones paginate the matching set.
  let activeAudit=null;
  function initAudit(){
    const root=q('.sage-audit-page');if(!root){activeAudit=null;return;}if(root.dataset.refinementReady)return;root.dataset.refinementReady='1';
    const rows=qa('[data-audit-row]',root).map((row,index)=>({row,index,time:new Date(row.dataset.auditTs).getTime(),text:row.dataset.auditText||''})),fields={search:q('[data-audit-search]',root),category:q('[data-audit-category]',root),department:q('[data-audit-department]',root),from:q('[data-audit-from]',root),to:q('[data-audit-to]',root)},chips=q('[data-audit-chips]',root),size=q('[data-audit-page-size]',root),status=q('[data-audit-page-status]',root),prev=q('[data-audit-prev]',root),next=q('[data-audit-next]',root),body=q('.audit-ledger tbody',root);
    let page=0,ascending=false,timer=0,rendered=[];
    const dateValue=date=>`${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
    function apply(reset=true){
      if(!root.isConnected)return;if(reset)page=0;const term=fields.search.value.trim().toLowerCase(),from=fields.from.value?new Date(fields.from.value+'T00:00:00').getTime():null,to=fields.to.value?new Date(fields.to.value+'T23:59:59.999').getTime():null;
      const matches=rows.filter(item=>(!term||item.text.includes(term))&&(!fields.category.value||item.row.dataset.auditCategory===fields.category.value)&&(!fields.department.value||item.row.dataset.auditDepartment===fields.department.value)&&(from===null||item.time>=from)&&(to===null||item.time<=to)),perPage=Number(size?.value||25),pages=Math.max(1,Math.ceil(matches.length/perPage));page=Math.min(page,pages-1);const matchSet=new Set(matches),shown=mobile.matches?matches.slice(page*perPage,(page+1)*perPage):rows;
      for(const item of rows){const hidden=!matchSet.has(item);if(item.row.hidden!==hidden)item.row.hidden=hidden;}
      // Keep every event searchable in the cache, while only the current phone
      // page participates in layout, paint and inert/focus recalculation.
      if(rows.length&&(shown.length!==rendered.length||shown.some((item,index)=>item!==rendered[index]))){const fragment=document.createDocumentFragment();for(const item of shown){item.row.dataset.auditPageVisible='true';fragment.append(item.row);}body.replaceChildren(fragment);rendered=shown;}
      const visible=q('[data-audit-visible-count]',root),empty=q('[data-audit-empty]',root);if(visible)visible.textContent=String(matches.length);if(empty)empty.hidden=matches.length!==0;if(status)status.textContent=matches.length?`${page+1} / ${pages} · ${matches.length} events`:'No matches';if(prev)prev.disabled=page===0;if(next)next.disabled=page>=pages-1;
      if(chips){chips.replaceChildren();for(const [key,field] of Object.entries(fields)){if(!field.value)continue;const button=document.createElement('button');button.type='button';const value=field.tagName==='SELECT'?field.selectedOptions[0]?.textContent:field.value;button.textContent=`${key==='search'?'Search':key}: ${value} ×`;button.setAttribute('aria-label',`Remove ${key} filter`);button.addEventListener('click',()=>{field.value='';apply();});chips.append(button);}}
    }
    Object.values(fields).forEach(field=>field?.addEventListener(field===fields.search?'input':'change',()=>{clearTimeout(timer);if(field===fields.search)timer=setTimeout(()=>apply(),120);else apply();}));
    qa('[data-audit-period]',root).forEach(button=>button.addEventListener('click',()=>{const period=button.dataset.auditPeriod,now=new Date(),start=new Date(now);if(period!=='all')start.setDate(start.getDate()-(period==='today'?0:Number(period)-1));fields.from.value=period==='all'?'':dateValue(start);fields.to.value=period==='all'?'':dateValue(now);qa('[data-audit-period]',root).forEach(item=>item.classList.toggle('active',item===button));apply();}));
    q('[data-audit-clear]',root)?.addEventListener('click',()=>{Object.values(fields).forEach(field=>field.value='');qa('[data-audit-period]',root).forEach(button=>button.classList.toggle('active',button.dataset.auditPeriod==='all'));apply();});
    const turn=direction=>{page+=direction;apply(false);q('.audit-feed',root).scrollTop=0;};prev?.addEventListener('click',()=>turn(-1));next?.addEventListener('click',()=>turn(1));size?.addEventListener('change',()=>apply());
    q('[data-audit-sort]',root)?.addEventListener('click',event=>{ascending=!ascending;rows.sort((a,b)=>(ascending?a.time-b.time:b.time-a.time)||a.index-b.index);event.currentTarget.closest('th').setAttribute('aria-sort',ascending?'ascending':'descending');const order=q('.audit-timeline-panel>.panel-head>.status',root);if(order)order.textContent=ascending?'Oldest first':'Newest first';apply();});activeAudit={root,apply};apply();
  }
  function initStaff(){
    const root=q('.staff-admin-page');if(!root||root.dataset.refinementReady)return;root.dataset.refinementReady='1';const rows=qa('[data-staff-row]',root),count=q('[data-staff-match-count]',root),bar=q('[data-staff-bulk-bar]',root),controls=qa('[data-staff-search],[data-staff-filter-department],[data-staff-filter-role],[data-staff-filter-status]',root);let ascending=true;
    const sync=()=>{if(count)count.textContent=`${rows.filter(row=>!row.hidden).length} of ${rows.length} accounts`;if(bar)bar.dataset.selected=String(qa('[data-staff-select]:checked',root).some(box=>!box.closest('[data-staff-row]').hidden));};
    controls.forEach(control=>control.addEventListener(control.tagName==='INPUT'?'input':'change',sync));root.addEventListener('change',sync);
    q('[data-staff-clear]',root)?.addEventListener('click',()=>{for(const control of controls){control.value='';control.dispatchEvent(new Event(control.tagName==='INPUT'?'input':'change',{bubbles:true}));}sync();});
    q('[data-staff-sort]',root)?.addEventListener('click',event=>{const ordered=[...rows].sort((a,b)=>(ascending?1:-1)*(q('.staff-table-person strong',a)?.textContent||'').localeCompare(q('.staff-table-person strong',b)?.textContent||'')),fragment=document.createDocumentFragment();ordered.forEach(row=>fragment.append(row));q('#staffList',root).append(fragment);event.currentTarget.textContent=ascending?'Name Z–A':'Name A–Z';q('th:nth-child(2)',root)?.setAttribute('aria-sort',ascending?'ascending':'descending');ascending=!ascending;});sync();
  }
  q('#sageLiveMinimize')?.addEventListener('click',event=>{const card=q('#sageLiveNotification'),small=card.classList.toggle('is-minimized');event.currentTarget.textContent=small?'+':'−';event.currentTarget.setAttribute('aria-expanded',String(!small));event.currentTarget.setAttribute('aria-label',small?'Expand live update':'Minimize live update');});
  function ready(){const page=document.body.dataset.page;if(page!==lastPage){previousPage=lastPage;lastPage=page;}if(search?.value){search.value='';filterNav();}renderRecents();bindLedgers();initAudit();initStaff();}
  document.addEventListener('sage:page-ready',ready);mobile.addEventListener('change',()=>{if(!mobile.matches&&search){search.value='';filterNav();}for(const item of ledgers.values())item.sync();activeAudit?.apply(false);});filterNav();ready();
})();
