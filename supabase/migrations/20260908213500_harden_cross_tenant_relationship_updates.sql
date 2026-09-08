create or replace function private.guard_invoice_update()
returns trigger
language plpgsql
set search_path=''
as $fn$
declare r text; payment_update boolean; pt uuid; st uuid; sp uuid;
begin
  r:=public.current_role();
  payment_update:=coalesce(current_setting('nidan.payment_update',true),'')='1';
  if new.tenant_id<>old.tenant_id or new.tenant_id<>public.current_tenant_id() then raise exception 'Invoice tenant cannot change'; end if;
  select tenant_id into pt from public.patients where id=new.patient_id;
  if pt is null or pt<>new.tenant_id then raise exception 'Invoice patient does not belong to invoice tenant'; end if;
  if new.sample_id is not null then
    select tenant_id,patient_id into st,sp from public.samples where id=new.sample_id;
    if st is null or st<>new.tenant_id then raise exception 'Invoice sample does not belong to invoice tenant'; end if;
    if sp<>new.patient_id then raise exception 'Invoice sample patient does not match invoice patient'; end if;
  end if;
  if payment_update then
    if r not in ('owner','admin','receptionist') then raise exception 'Not permitted'; end if;
    if new.paid<old.paid then raise exception 'Paid amount cannot decrease'; end if;
    if new.paid>new.total then raise exception 'Paid amount cannot exceed invoice total'; end if;
    return new;
  end if;
  if r='receptionist' then
    if new.subtotal is distinct from old.subtotal or new.discount is distinct from old.discount or new.total is distinct from old.total or new.paid is distinct from old.paid or new.balance is distinct from old.balance or new.status is distinct from old.status or new.patient_id is distinct from old.patient_id or new.sample_id is distinct from old.sample_id then raise exception 'Receptionists cannot modify invoice financial or ownership fields'; end if;
  elsif r not in ('owner','admin') then raise exception 'Not permitted'; end if;
  if new.total<new.paid then raise exception 'Invoice total cannot be less than paid amount'; end if;
  return new;
end;
$fn$;

create or replace function private.guard_invoice_item_mutation()
returns trigger
language plpgsql
set search_path=''
as $fn$
declare tt uuid;
begin
  if tg_op='DELETE' then return old; end if;
  if new.tenant_id<>public.current_tenant_id() then raise exception 'Invoice item tenant mismatch'; end if;
  select tenant_id into tt from public.invoices where id=new.invoice_id;
  if tt is null or tt<>new.tenant_id then raise exception 'Invoice item invoice tenant mismatch'; end if;
  return new;
end;
$fn$;

drop trigger if exists trg_guard_invoice_item_mutation on public.invoice_items;
create trigger trg_guard_invoice_item_mutation before update or delete on public.invoice_items for each row execute function private.guard_invoice_item_mutation();
revoke all on function private.guard_invoice_item_mutation() from public,anon,authenticated;

create or replace function private.guard_payment_mutation()
returns trigger
language plpgsql
set search_path=''
as $fn$
declare it uuid;
begin
  if tg_op='DELETE' then return old; end if;
  if new.tenant_id<>old.tenant_id or new.tenant_id<>public.current_tenant_id() then raise exception 'Payment tenant cannot change'; end if;
  select tenant_id into it from public.invoices where id=new.invoice_id;
  if it is null or it<>new.tenant_id then raise exception 'Payment invoice tenant mismatch'; end if;
  return new;
end;
$fn$;

drop trigger if exists trg_guard_payment_mutation on public.payments;
create trigger trg_guard_payment_mutation before update or delete on public.payments for each row execute function private.guard_payment_mutation();
revoke all on function private.guard_payment_mutation() from public,anon,authenticated;
