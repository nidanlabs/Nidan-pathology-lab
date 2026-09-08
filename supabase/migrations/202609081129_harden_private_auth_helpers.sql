create schema if not exists private;

create or replace function private.current_role()
returns text language sql stable security definer set search_path = ''
as $$
  select role from public.profiles where user_id = auth.uid() and active = true limit 1;
$$;

create or replace function private.current_tenant_id()
returns uuid language sql stable security definer set search_path = ''
as $$
  select tenant_id from public.profiles where user_id = auth.uid() and active = true limit 1;
$$;

create or replace function public.current_role()
returns text language sql stable security invoker set search_path = ''
as $$ select private.current_role(); $$;

create or replace function public.current_tenant_id()
returns uuid language sql stable security invoker set search_path = ''
as $$ select private.current_tenant_id(); $$;

create or replace function private.nidan_admin_update_user_profile(p_user_id uuid, p_role text, p_active boolean)
returns jsonb language plpgsql security definer set search_path = ''
as $$
declare v_tenant uuid; v_actor_role text; v_old_role text; v_old_active boolean;
begin
  select tenant_id, role into v_tenant, v_actor_role from public.profiles where user_id=auth.uid() and active=true;
  if v_tenant is null or v_actor_role not in ('owner','admin') then raise exception 'not authorized'; end if;
  if p_role not in ('owner','admin','technician','pathologist','receptionist') then raise exception 'invalid role'; end if;
  select role, active into v_old_role, v_old_active from public.profiles where user_id=p_user_id and tenant_id=v_tenant for update;
  if not found then raise exception 'user not found'; end if;
  if p_user_id=auth.uid() and (p_role<>v_old_role or p_active<>v_old_active) then
    if v_actor_role='owner' and p_role<>'owner' then raise exception 'owner cannot demote self'; end if;
    if not p_active then raise exception 'cannot deactivate current user'; end if;
  end if;
  update public.profiles set role=p_role, active=p_active, updated_at=now() where user_id=p_user_id and tenant_id=v_tenant;
  perform public.nidan_log_audit(p_action=>'update',p_entity_type=>'profile',p_entity_id=>p_user_id,p_details=jsonb_build_object('old_role',v_old_role,'new_role',p_role,'old_active',v_old_active,'new_active',p_active));
  return jsonb_build_object('user_id',p_user_id,'role',p_role,'active',p_active);
end;
$$;

create or replace function public.nidan_admin_update_user_profile(p_user_id uuid, p_role text, p_active boolean)
returns jsonb language sql security invoker set search_path = ''
as $$ select private.nidan_admin_update_user_profile(p_user_id,p_role,p_active); $$;

revoke all on function private.current_role() from public, anon, authenticated;
revoke all on function private.current_tenant_id() from public, anon, authenticated;
revoke all on function private.nidan_admin_update_user_profile(uuid,text,boolean) from public, anon, authenticated;
grant usage on schema private to authenticated;

drop policy if exists doctors_staff_write on public.doctors;
drop policy if exists invoice_items_staff_write on public.invoice_items;
drop policy if exists invoices_staff_write on public.invoices;
drop policy if exists payments_staff_write on public.payments;

create policy doctors_staff_insert on public.doctors for insert to authenticated with check (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));
create policy doctors_staff_update on public.doctors for update to authenticated using (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[])) with check (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));
create policy doctors_staff_delete on public.doctors for delete to authenticated using (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));

create policy invoice_items_staff_insert on public.invoice_items for insert to authenticated with check (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));
create policy invoice_items_staff_update on public.invoice_items for update to authenticated using (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[])) with check (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));
create policy invoice_items_staff_delete on public.invoice_items for delete to authenticated using (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));

create policy invoices_staff_insert on public.invoices for insert to authenticated with check (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));
create policy invoices_staff_update on public.invoices for update to authenticated using (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[])) with check (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));
create policy invoices_staff_delete on public.invoices for delete to authenticated using (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));

create policy payments_staff_insert on public.payments for insert to authenticated with check (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));
create policy payments_staff_update on public.payments for update to authenticated using (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[])) with check (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));
create policy payments_staff_delete on public.payments for delete to authenticated using (tenant_id = public.current_tenant_id() and public.current_role() = any (array['owner','admin','receptionist']::text[]));

create index if not exists audit_logs_user_id_idx on public.audit_logs(user_id);
create index if not exists invoices_created_by_idx on public.invoices(created_by);
create index if not exists invoices_patient_id_idx on public.invoices(patient_id);
create index if not exists invoices_sample_id_idx on public.invoices(sample_id);
create index if not exists payments_received_by_idx on public.payments(received_by);
create index if not exists reports_released_by_idx on public.reports(released_by);
create index if not exists reports_sample_id_idx on public.reports(sample_id);
create index if not exists reports_verified_by_idx on public.reports(verified_by);
create index if not exists samples_patient_id_idx on public.samples(patient_id);
create index if not exists test_orders_ordered_by_idx on public.test_orders(ordered_by);

drop index if exists public.patients_tenant_idx;
drop index if exists public.profiles_tenant_idx;
drop index if exists public.reports_tenant_idx;
drop index if exists public.samples_tenant_idx;
