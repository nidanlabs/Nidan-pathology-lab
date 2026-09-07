(() => {
  const originalOpen = window.addEventListener;
  function esc(v){return String(v??'').replace(/[&<>'\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c]));}
  document.addEventListener('click', async (e) => {
    const btn=e.target.closest('[data-action="new-sample"]');
    if(!btn) return;
    e.stopImmediatePropagation();
    const page=document.getElementById('page');
    page.innerHTML='<div class="page-head"><div><p class="eyebrow">SAMPLE ACCESSION</p><h2>New Sample</h2><p class="muted">Select the registered patient. No UUID entry is required.</p></div><button class="ghost" data-section="samples">← Back</button></div><div class="panel"><div id="sampleLoad">Loading patients…</div></div>';
    const client=window.supabaseClient || window._nidanClient;
    const supabaseUrl=(window.NIDAN_CONFIG||{}).supabaseUrl;
    const key=(window.NIDAN_CONFIG||{}).supabasePublishableKey;
    const sb=client || (supabaseUrl&&key?window.supabase.createClient(supabaseUrl,key):null);
    if(!sb){document.getElementById('sampleLoad').innerHTML='<div class="error">Supabase is not configured.</div>';return;}
    const {data:auth}=await sb.auth.getSession();
    if(!auth.session){document.getElementById('sampleLoad').innerHTML='<div class="error">Please sign in again.</div>';return;}
    const {data:profile,error:pe}=await sb.from('profiles').select('tenant_id,role,active').eq('user_id',auth.session.user.id).single();
    if(pe||!profile?.active){document.getElementById('sampleLoad').innerHTML='<div class="error">Active laboratory profile not found.</div>';return;}
    const {data:patients,error}=await sb.from('patients').select('id,patient_id,first_name,last_name,age,sex').eq('tenant_id',profile.tenant_id).order('created_at',{ascending:false}).limit(200);
    if(error){document.getElementById('sampleLoad').innerHTML='<div class="error">'+esc(error.message)+'</div>';return;}
    const options=(patients||[]).map(p=>`<option value="${esc(p.id)}">${esc(p.patient_id)} — ${esc(p.first_name)} ${esc(p.last_name)}${p.age!==null?' · '+esc(p.age)+' yrs':''}</option>`).join('');
    document.getElementById('sampleLoad').innerHTML=`<form id="sampleFormFixed" class="form-grid"><label>Patient<select name="patient_id" required><option value="">Select patient</option>${options}</select></label><label>Accession number<input name="accession_number" placeholder="NID-2026-0001" required></label><label>Specimen type<select name="specimen_type"><option>Blood</option><option>Serum</option><option>Plasma</option><option>Urine</option><option>Stool</option><option>Other</option></select></label><label>Status<select name="status"><option value="received">Received</option><option value="processing">Processing</option><option value="completed">Completed</option></select></label><div class="form-actions"><button class="primary" type="submit">Save Sample</button><span id="sampleMessage" class="message"></span></div></form>`;
    document.getElementById('sampleFormFixed').onsubmit=async ev=>{ev.preventDefault();const f=new FormData(ev.target);const payload={tenant_id:profile.tenant_id,patient_id:f.get('patient_id'),accession_number:f.get('accession_number'),status:f.get('status')};const {error:ie}=await sb.from('samples').insert(payload);const m=document.getElementById('sampleMessage');m.textContent=ie?ie.message:'Sample saved successfully.';if(!ie)setTimeout(()=>document.querySelector('[data-section="samples"]').click(),600);};
  }, true);
})();
