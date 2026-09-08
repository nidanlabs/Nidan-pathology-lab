-- Nidan Pathology Lab: commercial test-order lifecycle and tenant integrity
create or replace function private.guard_test_order_update()
returns trigger
language plpgsql
set search_path = ''
as $$
declare
  actor_role text := public.current_role();
  patient_tenant uuid;
  sample_tenant uuid;
  sample_patient uuid;
begin
  if new.tenant_id <> old.tenant_id then
    raise exception 'Tenant cannot be changed on an existing test order';
  end if;

  if new.ordered_by is distinct from old.ordered_by then
    raise exception 'Order creator cannot be changed';
  end if;

  select p.tenant_id into patient_tenant
  from public.patients p where p.id = new.patient_id;
  if patient_tenant is null or patient_tenant <> new.tenant_id then
    raise exception 'Patient does not belong to the order tenant';
  end if;

  select s.tenant_id, s.patient_id into sample_tenant, sample_patient
  from public.samples s where s.id = new.sample_id;
  if sample_tenant is null or sample_tenant <> new.tenant_id then
    raise exception 'Sample does not belong to the order tenant';
  end if;
  if sample_patient <> new.patient_id then
    raise exception 'Sample patient does not match the test order patient';
  end if;

  if old.status in ('completed','cancelled') then
    if new.status is distinct from old.status
       or new.patient_id is distinct from old.patient_id
       or new.sample_id is distinct from old.sample_id
       or new.order_number is distinct from old.order_number then
      raise exception 'Completed or cancelled test orders are immutable';
    end if;
    return new;
  end if;

  if new.status is distinct from old.status then
    if actor_role not in ('owner','admin') then
      raise exception 'Only owner or admin can change test-order status';
    end if;

    if not (
      (old.status = 'ordered' and new.status in ('processing','completed','cancelled'))
      or (old.status = 'processing' and new.status in ('completed','cancelled'))
    ) then
      raise exception 'Invalid test-order status transition';
    end if;
  end if;

  if old.status <> 'ordered'
     and (new.patient_id is distinct from old.patient_id
          or new.sample_id is distinct from old.sample_id
          or new.order_number is distinct from old.order_number) then
    raise exception 'Patient, sample and order number cannot be changed after processing starts';
  end if;

  if actor_role = 'receptionist'
     and (new.status is distinct from old.status
          or new.tenant_id is distinct from old.tenant_id
          or new.ordered_by is distinct from old.ordered_by) then
    raise exception 'Receptionist cannot change protected test-order fields';
  end if;

  if actor_role not in ('owner','admin','receptionist') then
    raise exception 'You do not have permission to edit test orders';
  end if;

  return new;
end;
$$;

drop trigger if exists trg_guard_test_order_update on public.test_orders;
create trigger trg_guard_test_order_update
before update on public.test_orders
for each row execute function private.guard_test_order_update();

drop policy if exists test_orders_update_staff on public.test_orders;
create policy test_orders_update_staff on public.test_orders
for update to authenticated
using (
  tenant_id = public.current_tenant_id()
  and public.current_role() = any (array['owner','admin','receptionist']::text[])
)
with check (
  tenant_id = public.current_tenant_id()
);