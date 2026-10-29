(()=>{'use strict';
  // ========================================================================
  // Legacy mobile decoration. Desktop uses the separate SAGE 8 component system.
  // ========================================================================
  const q=(s,r=document)=>r.querySelector(s),qa=(s,r=document)=>[...r.querySelectorAll(s)],reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const pageIcons={dashboard:'dashboard',requests:'requests',income:'arrow-up',expenses:'arrow-down',finance:'wallet',workspace:'briefcase',catalog:'box',operations:'briefcase',fulfillment:'check',procurement:'cart',inventory:'inventory',assets:'assets',departments:'building',staff:'users',reports:'reports',audit:'clock',analytics:'analytics',settings:'settings'};
  const cardSelector='.panel,.stat-card,.mini-stat,.department-card,.report-card,.owner-request-card,.acquisition-card,.procurement-card,.supplier-card,.finance-kpi,.finance-budget-card,.finance-forecast-card,.management-alert-card,.job-tool-card,.dashboard-summary-card,.role-hero,.catalogue-item-card,.branch-comparison-card,.intelligence-chart-card,.settings-subpanel,.settings-panel,.money-register-panel,.finance-workbook-panel,.audit-command-panel,.audit-timeline-panel,.dashboard-section,.dashboard-department-balances';
  const revealSelector='.page-heading,.stat-grid,.compact-stats,.dashboard-grid,.panel,.finance-kpi-grid,.income-kpi-grid,.expense-kpi-grid,.owner-request-command-panel,.owner-balance-control,.money-budget-strip,.finance-workbook-panel,.department-grid,.catalogue-group,.catalogue-owner-overview,.acquisition-grid,.procurement-control-strip,.staff-stat-grid,.staff-directory-panel,.reports-v2-summary,.reports-v2-kpis,.reports-v2-charts,.audit-command-panel,.audit-summary-grid,.settings-v2-layout,.management-alert-panel';
  let revealObserver=null,mutationTimer=0;
  const requestsPage=()=>document.body.dataset.page==='requests';
  const clearRequestPremium=()=>{if(!requestsPage())return;const main=q('.main-content');q('.sage-ambient',main||document)?.remove();q('.premium-grain')?.remove();q('.premium-page-emblem',main||document)?.remove();qa('[data-premium-card]',main||document).forEach(card=>{card.removeAttribute('data-premium-card');card.style.removeProperty('--mx');card.style.removeProperty('--my');qa(':scope > .premium-card-edge,:scope > .premium-sheen',card).forEach(node=>node.remove());});qa('.premium-reveal,.premium-metric-pop',main||document).forEach(node=>{node.classList.remove('premium-reveal','premium-metric-pop','is-visible');node.style.removeProperty('--premium-delay');node.style.removeProperty('animation-delay');node.removeAttribute('data-premium-metric-ready');});};

  // ========================================================================
  // PREMIUM SHELL: ambient canvas, grain and scroll-position accent.
  // ========================================================================
  const ensureShell=()=>{const main=q('.main-content');if(requestsPage()){q('.sage-ambient',main||document)?.remove();q('.premium-grain')?.remove();if(!q('.sage-scroll-progress'))document.body.insertAdjacentHTML('afterbegin','<div class="sage-scroll-progress" aria-hidden="true"></div>');return;}if(main&&!q('.sage-ambient'))main.insertAdjacentHTML('afterbegin','<div class="sage-ambient" aria-hidden="true"><i></i><i></i><i></i></div>');if(!q('.premium-grain'))document.body.insertAdjacentHTML('afterbegin','<div class="premium-grain" aria-hidden="true"></div>');if(!q('.sage-scroll-progress'))document.body.insertAdjacentHTML('afterbegin','<div class="sage-scroll-progress" aria-hidden="true"></div>');};
  const updateProgress=()=>{const bar=q('.sage-scroll-progress'),max=document.documentElement.scrollHeight-innerHeight,p=max>0?Math.min(1,scrollY/max):0;if(bar)bar.style.transform=`scaleX(${p})`;};

  // ========================================================================
  // PAGE EMBLEM: one quiet graphic identity for every major SAGE workspace.
  // ========================================================================
  const ensureEmblem=()=>{if(requestsPage()){q('.main-content .premium-page-emblem')?.remove();return;}const heading=q('.main-content .page-heading'),page=document.body.dataset.page||'dashboard';if(!heading||q('.premium-page-emblem',heading))return;const icon=pageIcons[page]||'sparkles',node=document.createElement('span');node.className='premium-page-emblem';node.setAttribute('aria-hidden','true');node.innerHTML=`<svg><use href="#i-${icon}"/></svg>`;heading.appendChild(node);};

  // ========================================================================
  // CARDS: spotlight coordinates, top edge and occasional premium sheen.
  // ========================================================================
  const decorateCards=()=>{if(requestsPage()){clearRequestPremium();return;}qa(cardSelector,q('.main-content')||document).forEach((card,index)=>{if(card.dataset.premiumCard)return;card.dataset.premiumCard='1';if(card.matches('.panel,.stat-card'))card.insertAdjacentHTML('afterbegin','<i class="premium-card-edge" aria-hidden="true"></i>');if(index<16&&card.matches('.panel,.stat-card,.mini-stat,.finance-kpi,.job-tool-card,.dashboard-summary-card'))card.insertAdjacentHTML('afterbegin','<i class="premium-sheen" aria-hidden="true"></i>');});};

  // ========================================================================
  // REVEALS + METRIC POPS: restrained stagger, reruns after SPA navigation.
  // ========================================================================
  const initRevealObserver=()=>{if(revealObserver)revealObserver.disconnect();if(requestsPage()){clearRequestPremium();return;}if(reduced){qa(revealSelector).forEach(el=>el.classList.add('is-visible'));return;}revealObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');revealObserver.unobserve(entry.target);}}),{threshold:.06,rootMargin:'0px 0px -5%'});qa(revealSelector,q('.main-content')||document).forEach((el,index)=>{if(el.classList.contains('premium-page-emblem'))return;el.classList.add('premium-reveal');el.style.setProperty('--premium-delay',`${Math.min(index%8,7)*34}ms`);revealObserver.observe(el);});};
  // ======================================================
  // METRIC MOTION — PLAY ONCE PER RENDERED FIGURE; NEVER RESTART ON LIVE CLOCK / DOM TICKS
  // ======================================================
  const metricPops=()=>{if(requestsPage())return;qa('.stat-card-head strong,.mini-stat strong,.finance-kpi strong,.dashboard-summary-amount strong,.finance-money,.owner-request-kpis strong,.income-kpi-grid strong,.expense-kpi-grid strong',q('.main-content')||document).forEach((el,index)=>{if(el.dataset.premiumMetricReady)return;el.dataset.premiumMetricReady='1';el.style.animationDelay=`${Math.min(index,10)*25}ms`;el.classList.add('premium-metric-pop');});};

  // ========================================================================
  // MAGNETIC ACTIONS + RIPPLE: desktop-only tactile feedback on key controls.
  // ========================================================================
  const decorateActions=()=>qa('.btn,.new-request-btn,.ai-topbar-btn,.theme-control,.font-control,.guide-combo,.icon-button,.text-button',document).forEach(el=>{if(el.closest('.modal-backdrop')||el.dataset.premiumMagnetic)return;el.dataset.premiumMagnetic='1';});

  // ========================================================================
  // REFRESH: safe to call repeatedly after route swaps / modal injections.
  // ========================================================================
  const refresh=()=>{if(innerWidth>900){revealObserver?.disconnect();document.body.classList.add('sage-premium-ready');return;}ensureShell();if(requestsPage()){clearRequestPremium();updateProgress();document.body.classList.add('sage-premium-ready');return;}ensureEmblem();decorateCards();decorateActions();metricPops();initRevealObserver();updateProgress();document.body.classList.add('sage-premium-ready');};
  const scheduleRefresh=()=>{clearTimeout(mutationTimer);mutationTimer=setTimeout(refresh,80);};
  const start=()=>{refresh();addEventListener('scroll',updateProgress,{passive:true});addEventListener('resize',updateProgress,{passive:true});const root=q('.main-content');if(root)new MutationObserver(records=>{if(records.some(m=>!m.target.closest?.('[data-ui-static]')&&[...m.addedNodes].some(n=>n.nodeType===1)))scheduleRefresh();}).observe(root,{childList:true,subtree:true});new MutationObserver(scheduleRefresh).observe(document.body,{attributes:true,attributeFilter:['data-page']});matchMedia('(min-width:901px)').addEventListener('change',refresh);window.SAGE_PREMIUM={refresh};};
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',start,{once:true}):start();
})();
