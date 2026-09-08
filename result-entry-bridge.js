(() => {
  const cfg=window.NIDAN_CONFIG||{};
  if(!cfg.supabaseUrl||!cfg.supabasePublishableKey||!window.supabase)return;
  const db=window.supabase.createClient(cfg.supabaseUrl,cfg.supabasePublishableKey),page=document.getElementById('page');
  const esc=v=>String(v??'').replace(/[&<>'\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c]));
  async function openFromButton(){
    const text=(page.textContent||'');
    const m=text.match(/NID-ORD-\d{8}-\d+/);
    if(!m)throw new Error('Order number could not be identified. Please open Test Orders and select the order.');
    const {data:o,error}=await db.from('test_orders').select('id').eq('order_number',m[0]).maybeSingle();
    if(error)throw error;if(!o)throw new Error('Test order not found.');
    if(window.NIDAN_RESULT_WORKFLOW?.open)return window.NIDAN_RESULT_WORKFLOW.open(o.id);
    throw new Error('Result Entry module is still loading. Please try again.');
  }
  document.addEventListener('click',e=>{
    const b=e.target.closest('button');if(!b)return;
    if(!/Enter Result Values/i.test((b.textContent||'').trim()))return;
    e.preventDefault();e.stopImmediatePropagation();
    openFromButton().catch(x=>page.innerHTML=`<div class="error-card"><h2>Unable to load results</h2><p>${esc(x.message)}</p></div>`);
  },true);
})();