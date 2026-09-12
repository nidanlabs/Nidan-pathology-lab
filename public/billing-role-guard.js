(() => {
  const cfg=window.NIDAN_CONFIG||{};
  if(!cfg.supabaseUrl||!cfg.supabasePublishableKey||cfg.supabasePublishableKey.startsWith('YOUR_')) return;
  const db=window.supabase.createClient(cfg.supabaseUrl,cfg.supabasePublishableKey);
  let role=null;
  async function loadRole(){
    try{
      const {data:{user}}=await db.auth.getUser();
      if(!user){role=null;return;}
      const {data,error}=await db.from('profiles').select('role').eq('user_id',user.id).single();
      if(!error) role=data?.role||null;
    }catch(_){ role=null; }
  }
  function apply(){
    if(role!=='receptionist') return;
    document.querySelectorAll('[data-bw-edit]').forEach(b=>b.remove());
    document.querySelectorAll('[data-bw="new"],[data-bw="pay"]').forEach(b=>{b.style.display='';});
    document.querySelectorAll('[data-bw-edit] + .ghost').forEach(()=>{});
    document.querySelectorAll('#bwPanel td:last-child').forEach(td=>{
      if(!td.querySelector('[data-bw-pay],[data-bw-receipt]')) td.remove();
    });
  }
  loadRole().then(apply);
  const observer=new MutationObserver(apply);
  observer.observe(document.getElementById('page')||document.body,{childList:true,subtree:true});
  window.NIDAN_BILLING_ROLE_GUARD={reload:async()=>{await loadRole();apply();}};
})();
