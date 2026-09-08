create or replace function private.guard_test_order_item_update() returns trigger language plpgsql set search_path='' as $$
declare r text;
begin
  r := public.current_role();
  if OLD.status = 'released' then raise exception 'Released results are immutable'; end if;
  if OLD.status = 'verified' then
    if NEW.status = 'released' and r in ('owner','admin','pathologist') and NEW.result_data is not distinct from OLD.result_data then return NEW; end if;
    raise exception 'Verified results are immutable until controlled report release';
  end if;
  if NEW.status = 'verified' and r not in ('owner','admin','pathologist') then raise exception 'Only owner, admin or pathologist can verify results'; end if;
  if NEW.status = 'released' and OLD.status <> 'verified' then raise exception 'Only verified results can be released'; end if;
  return NEW;
end;
$$;
drop trigger if exists trg_guard_test_order_item_update on public.test_order_items;
create trigger trg_guard_test_order_item_update before update on public.test_order_items for each row execute function private.guard_test_order_item_update();

create or replace function private.guard_invoice_update() returns trigger language plpgsql set search_path='' as $$
declare r text; payment_update boolean;
begin
  r := public.current_role();
  payment_update := coalesce(current_setting('nidan.payment_update', true),'') = '1';
  if payment_update then
    if r not in ('owner','admin','receptionist') then raise exception 'Not permitted'; end if;
    if NEW.paid < OLD.paid then raise exception 'Paid amount cannot decrease'; end if;
    if NEW.paid > NEW.total then raise exception 'Paid amount cannot exceed invoice total'; end if;
    return NEW;
  end if;
  if r = 'receptionist' then
    if NEW.subtotal is distinct from OLD.subtotal or NEW.discount is distinct from OLD.discount or NEW.total is distinct from OLD.total or NEW.paid is distinct from OLD.paid or NEW.balance is distinct from OLD.balance or NEW.status is distinct from OLD.status or NEW.patient_id is distinct from OLD.patient_id or NEW.sample_id is distinct from OLD.sample_id or NEW.tenant_id is distinct from OLD.tenant_id then raise exception 'Receptionists cannot modify invoice financial or ownership fields'; end if;
  elsif r not in ('owner','admin') then raise exception 'Not permitted'; end if;
  if NEW.total < NEW.paid then raise exception 'Invoice total cannot be less than paid amount'; end if;
  return NEW;
end;
$$;
drop trigger if exists trg_guard_invoice_update on public.invoices;
create trigger trg_guard_invoice_update before update on public.invoices for each row execute function private.guard_invoice_update();

create or replace function public.nidan_record_payment(p_invoice_id uuid, p_amount numeric, p_method text, p_reference text default null) returns public.invoices language plpgsql set search_path='public' as $$
declare v_invoice public.invoices; v_paid numeric; v_balance numeric; v_status text; v_tenant uuid;
begin
  v_tenant := public.current_tenant_id();
  if v_tenant is null then raise exception 'Tenant context missing'; end if;
  if public.current_role() not in ('owner','admin','receptionist') then raise exception 'Not permitted'; end if;
  if p_amount is null or p_amount <= 0 then raise exception 'Payment amount must be greater than zero'; end if;
  if p_method not in ('cash','upi','card','bank_transfer','other') then raise exception 'Invalid payment method'; end if;
  select * into v_invoice from public.invoices where id=p_invoice_id and tenant_id=v_tenant for update;
  if not found then raise exception 'Invoice not found'; end if;
  if p_amount > v_invoice.balance then raise exception 'Payment exceeds invoice balance'; end if;
  insert into public.payments(tenant_id, invoice_id, amount, method, reference, received_by) values(v_tenant,p_invoice_id,p_amount,p_method,p_reference,auth.uid());
  v_paid := coalesce(v_invoice.paid,0) + p_amount;
  v_balance := greatest(coalesce(v_invoice.total,0) - v_paid,0);
  v_status := case when v_balance=0 then 'paid' when v_paid>0 then 'partial' else 'unpaid' end;
  perform set_config('nidan.payment_update','1',true);
  update public.invoices set paid=v_paid,balance=v_balance,status=v_status,updated_at=now() where id=p_invoice_id and tenant_id=v_tenant returning * into v_invoice;
  return v_invoice;
end;
$$;

DROP POLICY IF EXISTS test_order_items_update_staff ON public.test_order_items;
CREATE POLICY test_order_items_update_staff ON public.test_order_items FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id() AND public.current_role() = ANY(ARRAY['owner','admin','technician','pathologist'])) WITH CHECK (tenant_id = public.current_tenant_id() AND public.current_role() = ANY(ARRAY['owner','admin','technician','pathologist']));
DROP POLICY IF EXISTS invoice_items_staff_update ON public.invoice_items;
CREATE POLICY invoice_items_staff_update ON public.invoice_items FOR UPDATE TO authenticated USING (tenant_id = public.current_tenant_id() AND public.current_role() = ANY(ARRAY['owner','admin'])) WITH CHECK (tenant_id = public.current_tenant_id() AND public.current_role() = ANY(ARRAY['owner','admin']));
DROP POLICY IF EXISTS invoice_items_staff_delete ON public.invoice_items;
CREATE POLICY invoice_items_staff_delete ON public.invoice_items FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id() AND public.current_role() = ANY(ARRAY['owner','admin']));
DROP POLICY IF EXISTS invoices_staff_delete ON public.invoices;
CREATE POLICY invoices_staff_delete ON public.invoices FOR DELETE TO authenticated USING (tenant_id = public.current_tenant_id() AND public.current_role() = ANY(ARRAY['owner','admin']));
