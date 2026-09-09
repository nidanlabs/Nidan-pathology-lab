(() => {
  const cfg = window.NIDAN_CONFIG || {};
  if (!cfg.supabaseUrl || !cfg.supabasePublishableKey || cfg.supabasePublishableKey.startsWith('YOUR_')) return;
  const client = supabase.createClient(cfg.supabaseUrl, cfg.supabasePublishableKey);
  const page = document.getElementById('page');

  const toast = (message, kind='info') => {
    let el = document.getElementById('nidanUxToast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'nidanUxToast';
      el.setAttribute('role','status');
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.dataset.kind = kind;
    clearTimeout(window.__nidanToastTimer);
    window.__nidanToastTimer = setTimeout(() => { el.remove(); }, 4200);
  };

  const style = document.createElement('style');
  style.textContent = `
    #nidanUxToast{position:fixed;right:18px;bottom:18px;z-index:9999;max-width:min(440px,calc(100vw - 36px));padding:14px 16px;border-radius:12px;background:#102a2b;color:#fff;box-shadow:0 14px 40px #0f172a33;font-size:13px;font-weight:650;line-height:1.45}
    #nidanUxToast[data-kind="success"]{background:#166534}
    #nidanUxToast[data-kind="warning"]{background:#92400e}
    .nidan-disabled{opacity:.55!important;cursor:not-allowed!important}
    .nidan-workflow-note{margin:0 0 18px;padding:14px 16px;border:1px solid #d9e7e5;border-left:4px solid #0f766e;border-radius:12px;background:#f5fbfa;color:#30474a;font-size:13px}
    .nidan-workflow-note strong{display:block;margin-bottom:4px;color:#0f5f5a}
    .result-field input:invalid{border-color:#d14343}
    @media(max-width:800px){#nidanUxToast{left:14px;right:14px;bottom:14px;max-width:none}.nidan-workflow-note{font-size:12px}}
  `;
  document.head.appendChild(style);

  async function reportState(reportId){
    const {data:report,error:reportError}=await client.from('reports').select('id,status,report_number,sample_id').eq('id',reportId).maybeSingle();
    if(reportError) throw reportError;
    if(!report) throw new Error('Report not found.');
    const {data:items,error:itemError}=await client.from('test_order_items').select('id,status,result_data,test_name,test_code,test_orders!inner(sample_id)').eq('test_orders.sample_id',report.sample_id).neq('status','cancelled');
    if(itemError) throw itemError;
    const active=items||[];
    const entered=active.filter(i=>i.status==='result_entered');
    const verified=active.filter(i=>['verified','released'].includes(i.status));
    const missing=active.filter(i=>!i.result_data || Object.keys(i.result_data).length===0);
    return {report,items:active,entered,verified,missing};
  }

  async function releaseSafely(reportId){
    try {
      const s=await reportState(reportId);
      if (s.report.status==='released') { toast('Report is already released.','info'); return; }
      if (!s.items.length) { toast('No test result is attached to this report yet. Enter results first.','warning'); return; }
      if (s.missing.length) { toast(`${s.missing.length} test result${s.missing.length>1?'s are':' is'} still empty. Enter and save every result before verification.`,'warning'); return; }
      if (s.entered.length) { toast(`${s.entered.length} result${s.entered.length>1?'s are':' is'} waiting for verification. Open Reports and verify them first.`,'warning'); return; }
      if (s.verified.length !== s.items.length) { toast('Every active test must be verified before the report can be released.','warning'); return; }
      if (!window.confirm('Release this report? Released results will be locked.')) return;
      const {data,error}=await client.rpc('nidan_release_report',{p_report_id:reportId});
      if(error) throw error;
      toast(`Report ${data?.report_number||''} released successfully.`.trim(),'success');
      if(window.NIDAN_WORKFLOW?.verificationHome) window.NIDAN_WORKFLOW.verificationHome();
    } catch(e) {
      toast(e?.message||'Unable to release this report.','warning');
    }
  }

  async function guardPrintShare(button){
    try {
      const id=button.dataset.printReport || button.dataset.shareReport;
      const s=await reportState(id);
      if(s.report.status!=='released') {
        toast('This report is still a draft. Verify all results and release it before printing or sharing.','warning');
        return true;
      }
      return false;
    } catch(e) {
      toast(e?.message||'Unable to check report status.','warning');
      return true;
    }
  }

  function decorate(){
    if(!page) return;
    const reportButtons=page.querySelectorAll('[data-print-report],[data-share-report]');
    reportButtons.forEach(btn=>{
      const isDraftPage=!page.querySelector('[data-share-report]');
      if(btn.dataset.printReport && isDraftPage){
        btn.disabled=true;
        btn.classList.add('nidan-disabled');
        btn.title='Print becomes available after the report is released.';
      }
    });
    page.querySelectorAll('form[data-result-item]').forEach(form=>{
      form.querySelectorAll('input[name]').forEach(input=>{
        if(!input.disabled) input.required=true;
      });
      const button=form.querySelector('button[type="submit"]');
      if(button) button.textContent='Save & Submit Result';
    });
    const reportHead=page.querySelector('.report-paper');
    if(reportHead && !page.querySelector('.nidan-workflow-note')){
      const release=page.querySelector('[data-release-report]');
      const share=page.querySelector('[data-share-report]');
      const note=document.createElement('div');
      note.className='nidan-workflow-note';
      if(release){
        note.innerHTML='<strong>Release checklist</strong>Enter every test result → Save → Verify every test → Release report. After release, results are locked and the report can be printed/shared.';
      } else if(share){
        note.innerHTML='<strong>Released report</strong>This report is finalized. Results are locked; Print/PDF and Share are available.';
      }
      if(note.textContent) reportHead.parentNode.insertBefore(note,reportHead);
    }
  }

  document.addEventListener('click', async (e) => {
    const release=e.target.closest('[data-release-report]');
    if(release){
      e.preventDefault();
      e.stopImmediatePropagation();
      await releaseSafely(release.dataset.releaseReport);
      return;
    }
    const ps=e.target.closest('[data-print-report],[data-share-report]');
    if(ps){
      const blocked=await guardPrintShare(ps);
      if(blocked){e.preventDefault();e.stopImmediatePropagation();return;}
    }
  }, true);

  document.addEventListener('submit', (e) => {
    const form=e.target.closest('form[data-result-item]');
    if(!form) return;
    const empty=[...form.querySelectorAll('input[name]:not(:disabled)')].filter(i=>!i.value.trim());
    if(empty.length){
      e.preventDefault();
      toast(`Please enter all ${empty.length} required result value${empty.length>1?'s':''} before saving.`,'warning');
      empty[0].focus();
    }
  }, true);

  const observer=new MutationObserver(decorate);
  observer.observe(page||document.body,{childList:true,subtree:true});
  decorate();
})();
