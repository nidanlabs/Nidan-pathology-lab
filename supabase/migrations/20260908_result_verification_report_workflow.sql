alter table public.reports add column if not exists report_number text;
alter table public.reports add column if not exists verified_at timestamptz;
alter table public.reports add column if not exists released_at timestamptz;
create unique index if not exists reports_tenant_report_number_uq on public.reports(tenant_id, report_number) where report_number is not null;

create or replace function public.nidan_verify_test_item(p_item_id uuid)
returns public.test_order_items
language plpgsql security definer set search_path = public
as $$
declare r public.test_order_items;
begin
  if public.current_role() <> all(array['owner','admin','pathologist']) then raise exception 'Only owner, admin or pathologist can verify results'; end if;
  select i.* into r from public.test_order_items i where i.id=p_item_id and i.tenant_id=public.current_tenant_id() for update;
  if not found then raise exception 'Result item not found'; end if;
  if r.status <> 'result_entered' then raise exception 'Only result-entered items can be verified'; end if;
  update public.test_order_items set status='verified' where id=p_item_id returning * into r;
  return r;
end;
$$;

create or replace function public.nidan_create_draft_report(p_sample_id uuid)
returns public.reports
language plpgsql security definer set search_path = public
as $$
declare r public.reports; t uuid; n text;
begin
  if public.current_role() <> all(array['owner','admin','pathologist']) then raise exception 'Only owner, admin or pathologist can create reports'; end if;
  t:=public.current_tenant_id();
  if not exists (select 1 from public.samples where id=p_sample_id and tenant_id=t) then raise exception 'Sample not found'; end if;
  if exists (select 1 from public.reports where sample_id=p_sample_id and tenant_id=t and status='released') then raise exception 'Report already released'; end if;
  n:='NID-RPT-'||to_char(now(),'YYYYMMDDHH24MISSMS');
  select * into r from public.reports where sample_id=p_sample_id and tenant_id=t order by created_at desc limit 1;
  if found then return r; end if;
  insert into public.reports(tenant_id,sample_id,status,result_data,report_number) values(t,p_sample_id,'draft','{}'::jsonb,n) returning * into r;
  return r;
end;
$$;

create or replace function public.nidan_release_report(p_report_id uuid)
returns public.reports
language plpgsql security definer set search_path = public
as $$
declare r public.reports; t uuid; bad integer; agg jsonb;
begin
  if public.current_role() <> all(array['owner','admin','pathologist']) then raise exception 'Only owner, admin or pathologist can release reports'; end if;
  t:=public.current_tenant_id();
  select * into r from public.reports where id=p_report_id and tenant_id=t for update;
  if not found then raise exception 'Report not found'; end if;
  select count(*) into bad from public.test_order_items i join public.test_orders o on o.id=i.order_id where o.sample_id=r.sample_id and o.tenant_id=t and i.status not in ('verified','released','cancelled');
  if bad>0 then raise exception 'All test results must be verified before release'; end if;
  select coalesce(jsonb_agg(jsonb_build_object('test_code',i.test_code,'test_name',i.test_name,'status',i.status,'result',i.result_data) order by i.created_at),'[]'::jsonb) into agg from public.test_order_items i join public.test_orders o on o.id=i.order_id where o.sample_id=r.sample_id and o.tenant_id=t and i.status<>'cancelled';
  update public.reports set status='released',result_data=agg,verified_by=coalesce(verified_by,auth.uid()),released_by=auth.uid(),verified_at=coalesce(verified_at,now()),released_at=now(),updated_at=now() where id=r.id returning * into r;
  update public.test_order_items i set status='released' from public.test_orders o where i.order_id=o.id and o.sample_id=r.sample_id and o.tenant_id=t and i.status='verified';
  return r;
end;
$$;

revoke all on function public.nidan_verify_test_item(uuid) from public, anon;
revoke all on function public.nidan_create_draft_report(uuid) from public, anon;
revoke all on function public.nidan_release_report(uuid) from public, anon;
grant execute on function public.nidan_verify_test_item(uuid) to authenticated;
grant execute on function public.nidan_create_draft_report(uuid) to authenticated;
grant execute on function public.nidan_release_report(uuid) to authenticated;
