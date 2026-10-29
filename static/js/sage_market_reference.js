/* ========================================================================== */
/* SAGE MARKET REFERENCE LAYER — identity → micro trend → main value → delta */
/* Uses real deltas when present. Decorative pulse lines never invent figures. */
/* ========================================================================== */
(() => {
  'use strict';
  const q=(s,r=document)=>r.querySelector(s), qa=(s,r=document)=>[...r.querySelectorAll(s)], main=()=>q('.main-content')||document;
  const moneyLike=/[₦$£€¥₹]|GH₵|KSh|USh|TSh|FRw|CFA|FCFA|MAD|CHF/i;
  const valueNumber=text=>{const clean=String(text||'').replace(/[^0-9.,−-]/g,'').replace(/,/g,'').replace('−','-');const n=Number.parseFloat(clean);return Number.isFinite(n)?n:0;};
  const page=()=>document.body.dataset.page||'';
  const flowFor=(card,label,valueText)=>{
    const text=`${label} ${card.className||''} ${card.textContent||''}`.toLowerCase(),value=valueNumber(valueText);
    if(/negative|loss|deficit|shortfall|overdue/.test(text)||value<0)return'out';
    if(card.classList.contains('danger')||card.classList.contains('negative'))return'out';
    if(card.classList.contains('success')||card.classList.contains('positive'))return'in';
    if(/expense|expenditure|money out|payable|cost|spend|released|payment|tax|payroll/.test(text))return'out';
    if(/income|revenue|money in|receivable|profit|sales|collection|growth|received/.test(text))return'in';
    if(/net position|net visible|profit \/ loss/.test(text))return value<0?'out':'in';
    return'neutral';
  };
  const paths={in:'M2 28 L12 25 L20 26 L29 17 L37 21 L46 10 L55 14 L65 8 L75 12 L84 5 L96 8',out:'M2 7 L12 10 L21 8 L30 18 L39 15 L48 26 L58 22 L67 29 L76 25 L86 31 L96 28',neutral:'M2 19 L13 17 L23 20 L33 16 L43 18 L54 14 L64 17 L75 13 L86 15 L96 12'};
  const signalMarkup=flow=>`<span class="sage-ref-signal sage-ref-signal-${flow}" aria-hidden="true"><svg viewBox="0 0 100 36" preserveAspectRatio="none"><defs><linearGradient id="sageRefFade-${flow}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="currentColor" stop-opacity=".24"/><stop offset="1" stop-color="currentColor" stop-opacity="0"/></linearGradient></defs><path class="sage-ref-area" d="${paths[flow]} L96 36 L2 36 Z"/><path class="sage-ref-line" d="${paths[flow]}"/><path class="sage-ref-tail" d="M96 ${flow==='out'?28:flow==='in'?8:12} H100"/></svg></span>`;

  function primaryValue(card){return q('.dashboard-summary-amount strong,.finance-kpi strong,.money-filter-summary strong,.finance-workbook-summary strong,.control-metrics strong,.income-kpi-grid strong,.income-insight-grid strong,.intelligence-kpi-grid strong,.reports-v2-kpis strong,.mini-stat strong',card)||q('strong',card);}
  function cardLabel(card){return (q('.dashboard-summary-top>span,.finance-kpi small,.income-kpi-grid>article>span,.income-insight-grid>article>span,.money-filter-summary small,.finance-workbook-summary small,.control-metrics span,.mini-stat span',card)?.textContent||'').trim();}
  function decorateCard(card){
    const existing=q(':scope > .sage-ref-signal',card);
    if(card.dataset.sageRefReady&&existing)return;
    const value=primaryValue(card);if(!value)return;
    const raw=value.textContent.trim(); if(!moneyLike.test(raw)&&!/%/.test(raw))return;
    const label=cardLabel(card),flow=flowFor(card,label,raw);card.dataset.sageRefReady='1';card.dataset.sageRefFlow=flow;card.classList.add('sage-ref-card');
    /* IMPORTANT: signal belongs INSIDE the card. Inserting after value.parentElement
       can make it a sibling of <article>, turning the sparkline into a CSS-grid item. */
    if(!existing)card.insertAdjacentHTML('beforeend',signalMarkup(flow));
    const helper=qa('small',card).find(el=>/[+−-]?\d[\d,.]*%/.test(el.textContent||''));
    if(helper&&!helper.dataset.sageRefDelta){
      const text=helper.textContent.trim(),match=text.match(/^([+−-]?\d[\d,.]*%)\s*(.*)$/);if(match){const semantic=helper.classList.contains('negative-text')?'out':helper.classList.contains('positive-text')?'in':(match[1].startsWith('-')||match[1].startsWith('−')?'out':'in');helper.dataset.sageRefDelta='1';helper.classList.add('sage-ref-delta-wrap');helper.innerHTML=`<span class="sage-ref-delta sage-ref-delta-${semantic}">${match[1]}</span>${match[2]?`<span class="sage-ref-delta-context">${match[2]}</span>`:''}`;}
    }
  }
  function decorateCards(root=main()){
    qa('.dashboard-summary-card:not(.dashboard-approvals-card),.dashboard-position-strip>div,.dashboard-funding-stats>a,.income-kpi-grid>article,.income-insight-grid>article,.finance-kpi,.control-metrics>article,.finance-workbook-summary>span,.money-filter-summary>span,.intelligence-kpi-grid>article,.reports-v2-kpis>article,.mini-stat',root).forEach(decorateCard);
  }
  function decorateLedger(root=main()){
    qa('.finance-workbook-table tbody tr,[data-money-table] tbody tr',root).forEach(row=>{if(row.dataset.sageRefRow)return;const amount=q('.finance-money',row),direction=q('[data-label="Direction / Type"]',row);if(!amount&&!direction)return;const text=`${direction?.textContent||''} ${amount?.textContent||''}`.toLowerCase(),flow=/money out|expense|−|-/.test(text)?'out':/money in|income|\+/.test(text)?'in':'neutral';row.dataset.sageRefRow='1';row.dataset.sageRefFlow=flow;});
  }
  function semanticDashboardSeries(root=main()){
    qa('.dashboard-summary-card:not(.dashboard-approvals-card)',root).forEach(card=>{const canvas=q('canvas.sparkline',card);if(!canvas)return;const flow=flowFor(card,cardLabel(card),primaryValue(card)?.textContent||'');const wanted=flow==='out'?'red':'green';if(canvas.dataset.color!==wanted){canvas.dataset.color=wanted;setTimeout(()=>window.dispatchEvent(new Event('resize')),0);}});
  }
  function cleanupStraySignals(root=main()){qa('.income-kpi-grid > .sage-ref-signal,.expense-kpi-grid > .sage-ref-signal,.income-insight-grid > .sage-ref-signal,.expense-insight-grid > .sage-ref-signal,.finance-kpi-grid > .sage-ref-signal,.control-metrics > .sage-ref-signal',root).forEach(el=>el.remove());}
  function refresh(){const root=main();cleanupStraySignals(root);decorateCards(root);decorateLedger(root);semanticDashboardSeries(root);document.body.classList.toggle('sage-ref-financial-page',['dashboard','income','expenses','finance','debtors','imprest','daily_close','analytics','reports','inventory','assets','procurement'].includes(page()));}
  let queued=false;const schedule=()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;refresh();});};
  const start=()=>{refresh();const root=q('.main-content');if(root)new MutationObserver(schedule).observe(root,{childList:true,subtree:true});new MutationObserver(schedule).observe(document.body,{attributes:true,attributeFilter:['data-page','data-theme']});document.addEventListener('sage:styles-ready',schedule);};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
