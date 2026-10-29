/* ========================================================================== */
/* SAGE UI STABILITY — breakpoint settling + compact semantic helper text.    */
/* ========================================================================== */
(() => {
  'use strict';
  const html=document.documentElement,mobile=matchMedia('(max-width:900px)'),q=(s,r=document)=>r.querySelector(s),qa=(s,r=document)=>[...r.querySelectorAll(s)];
  let releaseTimer=0,currentMode=mobile.matches?'mobile':'desktop';

  function sentenceCaseDelta(){
    qa('.sage-ref-delta-context').forEach(el=>{const text=(el.textContent||'').trim();if(!text)return;const normalized=text.charAt(0).toUpperCase()+text.slice(1).toLowerCase();if(el.textContent!==normalized)el.textContent=normalized;});
  }
  function resetNewLedgers(){
    qa('.main-content :is(.history-ledger-scroll,.request-ledger-scroll,.finance-workbook-scroll,.money-table-scroll)').forEach(wrap=>{if(wrap.dataset.sageStableScroll)return;wrap.dataset.sageStableScroll='1';wrap.scrollLeft=0;});
  }
  function finishSwitch(){
    clearTimeout(releaseTimer);releaseTimer=setTimeout(()=>{requestAnimationFrame(()=>requestAnimationFrame(()=>{html.classList.remove('sage-layout-switching');html.dataset.sageViewport=currentMode;window.SAGE_MARKET?.refresh?.();sentenceCaseDelta();resetNewLedgers();}));},90);
  }
  function beginSwitch(force=false){
    const next=mobile.matches?'mobile':'desktop';if(!force&&next===currentMode)return;currentMode=next;html.classList.add('sage-layout-switching');finishSwitch();
  }
  mobile.addEventListener?.('change',()=>beginSwitch(true));
  window.addEventListener('orientationchange',()=>beginSwitch(true),{passive:true});
  document.addEventListener('sage:page-ready',()=>{sentenceCaseDelta();resetNewLedgers();});
  document.addEventListener('sage:styles-ready',()=>{sentenceCaseDelta();});
  const observer=new MutationObserver(mutations=>{if(mutations.some(m=>[...m.addedNodes].some(n=>n.nodeType===1))){sentenceCaseDelta();resetNewLedgers();}});
  const start=()=>{html.dataset.sageViewport=currentMode;sentenceCaseDelta();resetNewLedgers();const root=q('.main-content');if(root)observer.observe(root,{childList:true,subtree:true});};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
