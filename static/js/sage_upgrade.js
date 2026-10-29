/* ==========================================================================
   SAGE GREETING — one desktop sequence per authenticated login, SPA aware.
   The server's login token survives refreshes and rotates at the next login.
   ========================================================================== */
(()=>{
 'use strict';
 const desktop=matchMedia('(min-width:901px)'),reduced=matchMedia('(prefers-reduced-motion:reduce)');
 const seen=new Set();let active=null;
 function stop(){if(!active)return;clearTimeout(active.timer);active.el.textContent=active.final;active.el.classList.remove('sage-greeting-active');active=null;}
 function start(){
  if(active&&!active.el.isConnected)stop();
  const el=document.querySelector('[data-sage-greeting]');if(!el||el.dataset.greetingReady)return;
  el.dataset.greetingReady='1';
  const token=el.dataset.greetingToken,key='sage-greeting:'+el.dataset.greetingUser;
  if(!token)return;
  let consumed=seen.has(token);try{consumed=consumed||localStorage.getItem(key)===token;}catch(_){}
  if(consumed)return;
  /* Consume on mobile/reduced motion too: refreshing later must not replay it. */
  seen.add(token);try{localStorage.setItem(key,token);}catch(_){}
  if(!desktop.matches||reduced.matches)return;
  stop();const name=el.dataset.greetingName||'SAGE User',final=el.textContent;
  /* Walk the entire permitted sidebar in DOM order, including collapsed groups.
     Use route identities to deduplicate; future pages get a label-based fallback. */
  const descriptions={"dashboard":"Live organization-wide financial and operational position.","workspace":"Job-focused tools, actions and KPIs for the signed-in department.","catalog":"Role-aware equipment, materials, consumables and custom items for the signed-in department.","analytics":"Explore financial, operational and departmental performance.","income":"Sales, fees, service income and other money coming into the organization, with staff accountability.","expenses":"Detailed money-out tracking by department, date, vendor, payment method and accountable staff.","finance":"Income, revenue, expenditure, cash flow, budgets and financial position.","requests":"From staff need to approval, money-sent confirmation, purchase evidence and final accountability.","operations":"Job-specific operational actions, accountable records and live staff activity.","fulfillment":"Turn granted requests into confirmed stock or assets with receipts, custody and immutable evidence.","procurement":"Track requested items, sourcing, commitments, buying activity and fulfillment.","inventory":"Monitor received items, stock value, usage, transfers and replenishment.","assets":"Track equipment, custodians, locations and movements.","departments":"Create and manage every department, unit, branch or special team.","staff":"Manage people, roles, departments and accountability.","reports":"Management-ready finance, procurement, inventory, department and audit reports.","audit":"Time-aware organization history across finance, requests, purchases, inventory, assets, staff access and retained changes.","settings":"Configure organization profile, approvals, roles and notification preferences.","events":"Planning, funding, accountability and measurable business outcomes.","customers":"Contacts, customer history, invoices and connected credit sales.","debtors":"Outstanding invoices, due dates and payment history.","suppliers":"Supplier details, quotations, acquisition history and payable balances.","imprest":"Accountable cash, receipt-backed retirement and approved replenishment.","daily_close":"Compare recorded collections with counted payment channels.","branches":"Branch performance, staff access and finance-account allocation.","stock":"Batches, expiry, prices, transfers and physical counts.","bills":"Subscriptions, recurring costs, due dates and payments.","compliance":"Business documents, renewal history and expiry accountability.","payroll":"Salary policy, commissions, payslips, claims and staff advances.","business_reports":"Connected operating results, receivables, cash accountability and upcoming obligations."};
  const routes=new Set(),summaries=[];
  document.querySelectorAll('.sidebar-nav .nav-link[data-route]').forEach(link=>{
   const route=link.dataset.route;if(!route||routes.has(route))return;routes.add(route);
   const label=link.dataset.label||link.querySelector('.nav-label')?.textContent.trim()||route.replaceAll('_',' ');
   summaries.push(label+': '+(descriptions[route]||'Explore the tools and records available to you here.'));
  });
  const lines=['Welcome, '+name+' (SAGE User).','Glance through your dashboards, '+name+'.',...summaries,final];
  /* Measure the full sequence once, keeping the business-name row stationary
     even when a page description wraps onto more than two lines. */
  const probe=el.cloneNode(false);probe.removeAttribute('data-sage-greeting');probe.removeAttribute('id');
  const style=getComputedStyle(el);
  probe.style.cssText='position:fixed!important;visibility:hidden!important;pointer-events:none!important;display:block!important;height:auto!important;min-height:0!important;max-height:none!important;padding:0!important;border:0!important;white-space:normal!important;';
  probe.style.width=el.getBoundingClientRect().width+'px';probe.style.font=style.font;probe.style.lineHeight=style.lineHeight;probe.style.letterSpacing=style.letterSpacing;
  document.body.appendChild(probe);let height=el.getBoundingClientRect().height;
  lines.forEach(copy=>{probe.textContent=copy+' |';height=Math.max(height,probe.getBoundingClientRect().height);});
  probe.remove();el.style.setProperty('min-height',Math.ceil(height)+'px','important');
  active={el,final,timer:null};el.classList.add('sage-greeting-active');let line=0,index=0;
  function tick(){
   if(!active||active.el!==el)return;
   if(!desktop.matches||reduced.matches||!el.isConnected){stop();return;}
   el.textContent=lines[line].slice(0,++index);
   if(index<lines[line].length)active.timer=setTimeout(tick,42);
   else if(line<lines.length-1)active.timer=setTimeout(()=>{line++;index=0;tick();},1800);
   else stop();
  }tick();
 }
 desktop.addEventListener('change',()=>{if(!desktop.matches){stop();document.querySelectorAll('[data-sage-greeting]').forEach(el=>el.style.removeProperty('min-height'));}});
 reduced.addEventListener('change',()=>{if(reduced.matches)stop();});
 const boot=()=>{start();const root=document.querySelector('#appContent');if(root)new MutationObserver(start).observe(root,{childList:true,subtree:true});};
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
