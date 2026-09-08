create or replace function private.guard_invoice_insert()
returns trigger
language plpgsql
set search_path=''
as $fn$
declare pt uuid; st uuid; sp uuid;
begin
  if new.tenant_id<>public.current_tenant_id() then raise exception 'Invoice tenant does not match authenticated tenant'; end if;
  select tenant_id into pt from public.patients where id=new.patient_id;
  if pt is null or pt<>new.tenant_id then raise exception 'Invoice patient does not belong to invoice tenant'; end if;
  if new.sample_id is not null then
    select tenant_id,patient_id into st,sp from public.samples where id=new.sample_id;
    if st is null or st<>new.tenant_id then raise exception 'Invoice sample does not belong to invoice tenant'; end if;
    if sp<>new.patient_id then raise exception 'Invoice sample patient does not match invoice patient'; end if;
  end if;
  return new;
end;
$fn$;

drop trigger if exists trg_guard_invoice_insert on public.invoices;
create trigger trg_guard_invoice_insert before insert on public.invoices for each row execute function private.guard_invoice_insert();
revoke all on function private.guard_invoice_insert() from public,anon,authenticated;

create or replace function private.guard_invoice_item_insert()
returns trigger
language plpgsql
set search_path=''
as $fn$
declare tt uuid;
begin
  if new.tenant_id<>public.current_tenant_id() then raise exception 'Invoice item tenant does not match authenticated tenant'; end if;
  select tenant_id into tt from public.invoices where id=new.invoice_id;
  if tt is null or tt<>new.tenant_id then raise exception 'Invoice item tenant does not match invoice tenant'; end if;
  return new;
end;
$fn$;

drop trigger if exists trg_guard_invoice_item_insert on public.invoice_items;
create trigger trg_guard_invoice_item_insert before insert on public.invoice_items for each row execute function private.guard_invoice_item_insert();
revoke all on function private.guard_invoice_item_insert() from public,anon,authenticated;

create or replace function private.guard_test_order_item_insert()
returns trigger
language plpgsql
set search_path=''
as $fn$
declare ot uuid;
begin
  if new.tenant_id<>public.current_tenant_id() then raise exception 'Test result tenant does not match authenticated tenant'; end if;
  select tenant_id into ot from public.test_orders where id=new.order_id;
  if ot is null or ot<>new.tenant_id then raise exception 'Test result order does not belong to result tenant'; end if;
  if new.status not in ('ordered','result_entered','verified','released','cancelled') then raise exception 'Invalid test result status'; end if;
  return new;
end;
$fn$;

drop trigger if exists trg_guard_test_order_item_insert on public.test_order_items;
create trigger trg_guard_test_order_item_insert before insert on public.test_order_items for each row execute function private.guard_test_order_item_insert();
revoke all on function private.guard_test_order_item_insert() from public,anon,authenticated;

create or replace function private.guard_payment_insert()
returns trigger
language plpgsql
set search_path=''
as $fn$
declare it uuid;
begin
  if new.tenant_id<>public.current_tenant_id() then raise exception 'Payment tenant does not match authenticated tenant'; end if;
  select tenant_id into it from public.invoices where id=new.invoice_id;
  if it is null or it<>new.tenant_id then raise exception 'Payment invoice does not belong to payment tenant'; end if;
  if public.current_role()=any(array['owner','admin']::text[]) then return new; end if;
  if public.current_role()='receptionist' and coalesce(current_setting('nidan.payment_insert',true),'0')='1' then return new; end if;
  raise exception 'Direct payment insertion is not permitted; use the payment workflow';
end;
$fn$;
