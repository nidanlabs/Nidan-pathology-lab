-- Nidan Pathology Lab: commercial billing mutation integrity
-- Applied to the live Supabase project on 2026-09-08.
-- Payment rows are ledger records: direct staff mutation is restricted and receptionist inserts
-- are accepted only through the atomic nidan_record_payment workflow.

begin;

drop policy if exists payments_staff_update on public.payments;
drop policy if exists payments_staff_delete on public.payments;
create policy payments_owner_admin_update on public.payments
for update using (
  tenant_id = public.current_tenant_id()
  and public.current_role() = any(array['owner','admin']::text[])
) with check (
  tenant_id = public.current_tenant_id()
  and public.current_role() = any(array['owner','admin']::text[])
);
create policy payments_owner_admin_delete on public.payments
for delete using (
  tenant_id = public.current_tenant_id()
  and public.current_role() = any(array['owner','admin']::text[])
);

drop policy if exists payments_owner_admin_insert on public.payments;
drop policy if exists payments_staff_insert on public.payments;
create policy payments_staff_insert on public.payments
for insert with check (
  tenant_id = public.current_tenant_id()
  and public.current_role() = any(array['owner','admin','receptionist']::text[])
);

create or replace function private.guard_payment_insert()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  if public.current_role() = any(array['owner','admin']::text[]) then
    return new;
  end if;
  if public.current_role() = 'receptionist'
     and coalesce(current_setting('nidan.payment_insert', true),'0') = '1' then
    return new;
  end if;
  raise exception 'Direct payment insertion is not permitted; use the payment workflow';
end;
$$;

drop trigger if exists trg_guard_payment_insert on public.payments;
create trigger trg_guard_payment_insert
before insert on public.payments
for each row execute function private.guard_payment_insert();

create or replace function public.nidan_record_payment(
  p_invoice_id uuid,
  p_amount numeric,
  p_method text,
  p_reference text default null
) returns public.invoices
language plpgsql
security invoker
set search_path = 'public'
as $$
declare
  v_invoice public.invoices;
  v_paid numeric;
  v_balance numeric;
  v_status text;
  v_tenant uuid;
begin
  v_tenant := public.current_tenant_id();
  if v_tenant is null then raise exception 'Tenant context missing'; end if;
  if public.current_role() not in ('owner','admin','receptionist') then raise exception 'Not permitted'; end if;
  if p_amount is null or p_amount <= 0 then raise exception 'Payment amount must be greater than zero'; end if;
  if p_method not in ('cash','upi','card','bank_transfer','other') then raise exception 'Invalid payment method'; end if;
  select * into v_invoice from public.invoices where id=p_invoice_id and tenant_id=v_tenant for update;
  if not found then raise exception 'Invoice not found'; end if;
  if p_amount > v_invoice.balance then raise exception 'Payment exceeds invoice balance'; end if;
  perform set_config('nidan.payment_insert','1',true);
  insert into public.payments(tenant_id, invoice_id, amount, method, reference, received_by)
  values(v_tenant,p_invoice_id,p_amount,p_method,p_reference,auth.uid());
  v_paid := coalesce(v_invoice.paid,0) + p_amount;
  v_balance := greatest(coalesce(v_invoice.total,0) - v_paid,0);
  v_status := case when v_balance=0 then 'paid' when v_paid>0 then 'partial' else 'unpaid' end;
  perform set_config('nidan.payment_update','1',true);
  update public.invoices set paid=v_paid,balance=v_balance,status=v_status,updated_at=now()
  where id=p_invoice_id and tenant_id=v_tenant returning * into v_invoice;
  return v_invoice;
end;
$$;

-- Receptionists may create invoices, but financial edits after creation are owner/admin only.
drop policy if exists invoices_staff_update on public.invoices;
create policy invoices_owner_admin_update on public.invoices
for update using (
  tenant_id = public.current_tenant_id()
  and public.current_role() = any(array['owner','admin']::text[])
) with check (
  tenant_id = public.current_tenant_id()
  and public.current_role() = any(array['owner','admin']::text[])
);

commit;
