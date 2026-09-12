(() => {
  const page=document.getElementById('page');
  if(!page)return;
  document.addEventListener('click',e=>{
    const b=e.target.closest('[data-enter-result]');
    if(!b)return;
    e.preventDefault();
    e.stopImmediatePropagation();
    const orderId=b.dataset.enterResult;
    if(!orderId){page.innerHTML='<div class="error-card"><h2>Unable to open results</h2><p>Test order ID is missing.</p></div>';return;}
    if(window.NIDAN_WORKFLOW?.openResultOrder)return window.NIDAN_WORKFLOW.openResultOrder(orderId);
    if(!window.NIDAN_WORKFLOW?.resultsHome){page.innerHTML='<div class="error-card"><h2>Result module is loading</h2><p>Please try again.</p></div>';return;}
    window.NIDAN_WORKFLOW.resultsHome().then(()=>{
      const row=page.querySelector(`[data-result-order="${CSS.escape(orderId)}"]`);
      if(row)row.click();else throw new Error('Test order could not be opened.');
    }).catch(x=>page.innerHTML=`<div class="error-card"><h2>Unable to open results</h2><p>${String(x.message||x)}</p></div>`);
  },true);
})();