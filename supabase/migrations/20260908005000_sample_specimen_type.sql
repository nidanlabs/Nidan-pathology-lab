alter table public.samples
  add column if not exists specimen_type text not null default 'Blood';

create index if not exists samples_tenant_patient_created_idx
  on public.samples(tenant_id, patient_id, created_at desc);
