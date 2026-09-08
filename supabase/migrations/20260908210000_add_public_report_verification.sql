alter table public.reports
  add column if not exists verification_token uuid not null default gen_random_uuid();

create unique index if not exists reports_verification_token_uidx
  on public.reports(verification_token);

create or replace function public.nidan_verify_report(p_token uuid)
returns table(report_number text, status text, released_at timestamptz, lab_name text)
language sql
security definer
set search_path=''
as $$
  select r.report_number, r.status, r.released_at,
         coalesce(ls.lab_name,'NIDAN PATHOLOGY LAB')
  from public.reports r
  left join public.lab_settings ls on ls.tenant_id=r.tenant_id
  where r.verification_token=p_token and r.status='released'
  limit 1;
$$;

revoke all on function public.nidan_verify_report(uuid) from public;
grant execute on function public.nidan_verify_report(uuid) to anon, authenticated;
