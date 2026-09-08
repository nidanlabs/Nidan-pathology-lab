(() => {
  const page = document.getElementById('page');
  const cfg = window.NIDAN_CONFIG || {};
  let db = null;
  let profile = null;

  const esc = v => String(v ?? '').replace(/[&<>\"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
  const configured = () => cfg.supabaseUrl && cfg.supabasePublishableKey && !cfg.supabasePublishableKey.startsWith('YOUR_');
  const canEdit = () => ['owner','admin','receptionist'].includes(profile?.role);

  async function initDb() {
    if (!configured() || !window.supabase) throw new Error('Supabase configuration is incomplete.');
    if (!db) db = window.supabase.createClient(cfg.supabaseUrl, cfg.supabasePublishableKey);
    const { data: sessionData } = await db.auth.getSession();
    if (!sessionData.session) throw new Error('Please sign in again.');
    const { data, error } = await db.from('profiles').select('tenant_id,role,active').eq('user_id', sessionData.session.user.id).single();
    if (error || !data?.active) throw new Error('Active laboratory profile not found.');
    profile = data;
  }

  function shell(title, eyebrow, subtitle, body, back='samples') {
    page.innerHTML = `<div class="page-head"><div><p class="eyebrow">${eyebrow}</p><h2>${title}</h2><p class="muted">${subtitle}</p></div><button class="ghost" data-section="${back}">← Back</button></div>${body}`;
  }

  async function loadPatients() {
    const { data, error } = await db.from('patients').select('id,patient_id,first_name,last_name,age,sex').order('first_name');
    if (error) throw error;
    return data || [];
  }

  async function listSamples() {
    await initDb();
    shell('Samples','ACCESSIONING','Track specimens, patient identity and accession status.','<div class="panel" id="samplePanel">Loading…</div>');
    try {
      const [{ data: samples, error }, { data: patients, error: patientError }] = await Promise.all([
        db.from('samples').select('id,accession_number,patient_id,specimen_type,status,created_at').order('created_at',{ascending:false}).limit(100),
        db.from('patients').select('id,patient_id,first_name,last_name,age,sex').order('first_name')
      ]);
      if (error) throw error;
      if (patientError) throw patientError;
      const byId = Object.fromEntries((patients || []).map(p => [p.id, p]));
      const rows = samples || [];
      if (!rows.length) {
        document.getElementById('samplePanel').innerHTML = '<div class="empty">No samples found.</div>';
        return;
      }
      document.getElementById('samplePanel').innerHTML = `<div class="table-wrap"><table><thead><tr><th>Accession Number</th><th>Patient</th><th>Patient ID</th><th>Specimen</th><th>Status</th><th>Created At</th>${canEdit()?'<th>Action</th>':''}</tr></thead><tbody>${rows.map(s=>{const p=byId[s.patient_id];const name=p?`${p.first_name} ${p.last_name||''}`.trim():'Unknown patient';return `<tr><td><strong>${esc(s.accession_number)}</strong></td><td>${esc(name)}</td><td>${esc(p?.patient_id||s.patient_id)}</td><td>${esc(s.specimen_type||'—')}</td><td><span class="status-pill">${esc(s.status)}</span></td><td>${esc(s.created_at)}</td>${canEdit()?`<td><button class="ghost" data-action="edit-sample" data-sample-id="${esc(s.id)}">Edit</button></td>`:''}</tr>`;}).join('')}</tbody></table></div>`;
    } catch (e) {
      document.getElementById('samplePanel').innerHTML = `<div class="error">${esc(e.message)}</div>`;
    }
  }

  async function newSample() {
    await initDb();
    shell('New Sample','SAMPLE ACCESSION','Create an accession and link it to the correct patient.','<div class="panel">Loading patients…</div>');
    try {
      const ps = await loadPatients();
      if (!ps.length) { page.innerHTML = '<div class="panel notice">Please register a patient first.</div>'; return; }
      shell('New Sample','SAMPLE ACCESSION','Create an accession and link it to the correct patient.',`<div class="panel"><form id="sampleWorkflowForm" class="form-grid"><label>Accession number<input name="accession_number" value="NID-${new Date().toISOString().slice(0,10).replaceAll('-','')}-${String(Date.now()).slice(-5)}" required></label><label>Patient<select name="patient_id" required><option value="">Select patient</option>${ps.map(p=>`<option value="${esc(p.id)}">${esc(p.patient_id)} — ${esc(`${p.first_name} ${p.last_name||''}`.trim())} (${esc(p.age)}y, ${esc(p.sex)})</option>`).join('')}</select></label><label>Specimen type<select name="specimen_type" required><option value="Blood">Blood</option><option value="Serum">Serum</option><option value="Plasma">Plasma</option><option value="Urine">Urine</option><option value="Stool">Stool</option><option value="Other">Other</option></select></label><label>Status<select name="status"><option value="received">Received</option><option value="processing">Processing</option><option value="completed">Completed</option></select></label><div class="form-actions"><button class="primary" type="submit">Save Sample</button><span id="sampleMessage" class="message"></span></div></form></div>`);
      document.getElementById('sampleWorkflowForm').onsubmit = async e => {
        e.preventDefault();
        const p = Object.fromEntries(new FormData(e.target).entries());
        p.tenant_id = profile.tenant_id;
        const { error } = await db.from('samples').insert(p);
        document.getElementById('sampleMessage').textContent = error ? error.message : 'Sample saved successfully.';
        if (!error) setTimeout(listSamples, 600);
      };
    } catch (e) {
      page.innerHTML = `<div class="error-card"><h2>Unable to load patients</h2><p>${esc(e.message)}</p></div>`;
    }
  }

  async function editSample(id) {
    await initDb();
    if (!canEdit()) { page.innerHTML = '<div class="panel notice">You do not have permission to edit samples.</div>'; return; }
    shell('Edit Sample','SAMPLE ACCESSION','Update accession details without changing the patient link.','<div class="panel">Loading sample…</div>');
    try {
      const [{ data: sample, error }, { data: patients, error: patientError }] = await Promise.all([
        db.from('samples').select('id,accession_number,patient_id,specimen_type,status').eq('id',id).single(),
        db.from('patients').select('id,patient_id,first_name,last_name,age,sex').order('first_name')
      ]);
      if (error) throw error;
      if (patientError) throw patientError;
      const patient = (patients || []).find(p => p.id === sample.patient_id);
      shell('Edit Sample','SAMPLE ACCESSION','Update accession details. The patient link is kept unchanged.',`<div class="panel"><form id="sampleEditForm" class="form-grid"><label>Accession number<input name="accession_number" value="${esc(sample.accession_number)}" required></label><label>Patient<input value="${esc(patient ? `${patient.patient_id} — ${patient.first_name} ${patient.last_name||''}`.trim() : sample.patient_id)}" readonly></label><label>Specimen type<select name="specimen_type" required>${['Blood','Serum','Plasma','Urine','Stool','Other'].map(x=>`<option value="${x}" ${sample.specimen_type===x?'selected':''}>${x}</option>`).join('')}</select></label><label>Status<select name="status">${['received','processing','completed'].map(x=>`<option value="${x}" ${sample.status===x?'selected':''}>${x[0].toUpperCase()+x.slice(1)}</option>`).join('')}</select></label><div class="form-actions"><button class="primary" type="submit">Save Changes</button><button class="ghost" type="button" data-section="samples">Cancel</button><span id="sampleEditMessage" class="message"></span></div></form></div>`);
      document.getElementById('sampleEditForm').onsubmit = async e => {
        e.preventDefault();
        const p = Object.fromEntries(new FormData(e.target).entries());
        const { error: updateError } = await db.from('samples').update({accession_number:p.accession_number,specimen_type:p.specimen_type,status:p.status}).eq('id',id);
        document.getElementById('sampleEditMessage').textContent = updateError ? updateError.message : 'Sample updated successfully.';
        if (!updateError) setTimeout(listSamples, 600);
      };
    } catch (e) {
      page.innerHTML = `<div class="error-card"><h2>Unable to load sample</h2><p>${esc(e.message)}</p><button class="ghost" data-section="samples">← Back to Samples</button></div>`;
    }
  }

  document.addEventListener('click', e => {
    const nav = e.target.closest('[data-section="samples"]');
    if (nav) { e.preventDefault(); e.stopImmediatePropagation(); listSamples(); return; }
    const edit = e.target.closest('[data-action="edit-sample"]');
    if (edit) { e.preventDefault(); e.stopImmediatePropagation(); editSample(edit.dataset.sampleId); return; }
    const add = e.target.closest('[data-action="new-sample"]');
    if (add) { e.preventDefault(); e.stopImmediatePropagation(); newSample(); return; }
  }, true);

  window.NIDAN_SAMPLE_WORKFLOW = { listSamples, newSample, editSample };
})();