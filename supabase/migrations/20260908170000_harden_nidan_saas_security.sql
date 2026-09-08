-- Nidan Pathology Lab: SaaS security hardening
-- Applied to the live Supabase project on 2026-09-08.

revoke execute on function public.current_role() from anon, public;
revoke execute on function public.current_tenant_id() from anon, public;
revoke execute on function public.nidan_admin_update_user_profile(uuid,text,boolean) from anon, public;

alter function public.nidan_log_audit(text,text,uuid,jsonb) security invoker;
alter function public.nidan_record_payment(uuid,numeric,text,text) security invoker;
alter function public.nidan_create_draft_report(uuid) security invoker;
alter function public.nidan_release_report(uuid) security invoker;
alter function public.nidan_verify_test_item(uuid) security invoker;

revoke execute on function public.nidan_log_audit(text,text,uuid,jsonb) from anon, public;
revoke execute on function public.nidan_record_payment(uuid,numeric,text,text) from anon, public;
revoke execute on function public.nidan_create_draft_report(uuid) from anon, public;
revoke execute on function public.nidan_release_report(uuid) from anon, public;
revoke execute on function public.nidan_verify_test_item(uuid) from anon, public;

alter default privileges for role postgres in schema public
  revoke execute on functions from anon, authenticated, public;

alter function public.current_role() set search_path = '';
alter function public.current_tenant_id() set search_path = '';
alter function public.nidan_admin_update_user_profile(uuid,text,boolean) set search_path = '';

create index if not exists profiles_user_active_idx on public.profiles(user_id, active);
create index if not exists profiles_tenant_idx on public.profiles(tenant_id);
create index if not exists patients_tenant_idx on public.patients(tenant_id);
create index if not exists samples_tenant_idx on public.samples(tenant_id);
create index if not exists test_orders_tenant_idx on public.test_orders(tenant_id);
create index if not exists test_order_items_tenant_idx on public.test_order_items(tenant_id);
create index if not exists reports_tenant_idx on public.reports(tenant_id);
create index if not exists invoices_tenant_idx on public.invoices(tenant_id);
create index if not exists invoice_items_tenant_idx on public.invoice_items(tenant_id);
create index if not exists payments_tenant_idx on public.payments(tenant_id);
create index if not exists doctors_tenant_idx on public.doctors(tenant_id);
create index if not exists lab_settings_tenant_idx on public.lab_settings(tenant_id);
create index if not exists audit_logs_tenant_idx on public.audit_logs(tenant_id);
