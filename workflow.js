(() => {
  const cfg = window.NIDAN_CONFIG || {};
  if (!cfg.supabaseUrl || !cfg.supabasePublishableKey || cfg.supabasePublishableKey.startsWith('YOUR_')) return;
  const client = window.supabase.createClient(cfg.supabaseUrl, cfg.supabasePublishableKey);
  const page = document.getElementById('page');
  const esc = v => String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  async function profile() {
    const {data:{session}} = await client.auth.getSession();
    if (!session) throw new Error('Session expired. Please login again.');
    const {data,error} = await client.from('profiles').select('tenant_id,role,email').eq('user_id',session.user.id).single();
    if (error) throw error;
    return data;
  }
  async function verificationHome() {
    if (!page) return;
    page.innerHTML='<div class="page-head"><div><p class="eyebrow">VERIFICATION & RELEASE</p><h2>Reports</h2><p class="muted">Review, verify and release laboratory reports.</p></div></div><div class="panel" id="reportWorkflow">Loading reports…</div>';
    const panel=document.getElementById('reportWorkflow');
    try {
      const p=await profile();
      if (!['owner','admin','pathologist','technician','receptionist'].includes(p.role)) throw new Error('You do not have permission to view Reports.');
      const {data,error}=await client.from('reports').select('id,report_number,sample_id,status,created_at,verified_at,released_at').order('created_at',{ascending:false}).limit(100);
      if(error) throw error;
      if(!data?.length){panel.innerHTML='<div class="empty">No reports found yet.</div>';return;}
      panel.innerHTML='<div class="table-wrap"><table><thead><tr><th>Report No.</th><th>Sample</th><th>Status</th><th>Created</th><th>Action</th></tr></thead><tbody>'+
        data.map(r=>{
          const released=r.status==='released';
          const action=released
            ? '<button class="primary small-btn" data-workflow-print="'+esc(r.id)+'">Print / PDF</button>'
            : '<span class="muted">Draft — verify results first</span>';
          return '<tr><td><b>'+esc(r.report_number||'Draft')+'</b></td><td>'+esc(r.sample_id)+'</td><td>'+esc(r.status)+'</td><td>'+esc(new Date(r.created_at).toLocaleString('en-IN'))+'</td><td>'+action+'</td></tr>';
        }).join('')+'</tbody></table></div>';
      panel.querySelectorAll('[data-workflow-print]').forEach(b=>b.onclick=()=>window.NIDAN_PRINT?.report?window.NIDAN_PRINT.report(b.dataset.workflowPrint):alert('Print module is loading. Refresh once and try again.'));
    } catch(e) {
      panel.innerHTML='<div class="error-card"><h3>Unable to load Reports</h3><p>'+esc(e.message||e)+'</p><button class="primary" onclick="location.reload()">Refresh</button></div>';
    }
  }
  async function resultsHome() {
    if (!page) return;
    const p=await profile();
    if (!['owner','admin','technician','pathologist'].includes(p.role)) {
      page.innerHTML='<div class="error-card"><h2>Access denied</h2><p>You do not have permission to access Results.</p></div>';
      return;
    }
    const nav=document.querySelector('[data-section="results"]');
    if (nav) { nav.removeAttribute('data-section'); nav.click(); }
  }
  async function openResultOrder(orderId) {
    if (typeof window.NIDAN_E2E_WORKFLOW?.start === 'function') {
      alert('Open the Results menu to select this order for result entry.');
    } else {
      alert('Open Results from the left menu.');
    }
  }
  window.NIDAN_WORKFLOW={verificationHome,resultsHome,openResultOrder};
})();