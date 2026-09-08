-- Nidan Pathology Lab: enforce safe test-order creation at the database boundary
create or replace function private.guard_test_order_insert()
returns trigger
language plpgsql
set search_path = ''
as $$
declare
  patient_tenant uuid;
  sample_tenant uuid;
  sample_patient uuid;
begin
  if new.tenant_id <> public.current_tenant_id() then
    raise exception 'Test order tenant does not match the authenticated tenant';
  end if;

  if new.status <> 'ordered' then
    raise exception 'New test orders must start in ordered status';
  end if;

  if new.ordered_by is distinct from auth.uid() then
    raise exception 'Test order creator must be the authenticated user';
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

  return new;
end;
$$;

drop trigger if exists trg_guard_test_order_insert on public.test_orders;
create trigger trg_guard_test_order_insert
before insert on public.test_orders
for each row execute function private.guard_test_order_insert();