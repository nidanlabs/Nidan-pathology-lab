create or replace function public.nidan_guard_report_mutation()
returns trigger
language plpgsql
set search_path = public
as $fn$
begin
  if tg_op = 'DELETE' then
    if old.status = 'released' then
      raise exception 'Released reports are immutable and cannot be deleted';
    end if;
    return old;
  end if;

  if old.status = 'released' then
    if new.status <> old.status
       or new.result_data is distinct from old.result_data
       or new.report_number is distinct from old.report_number
       or new.tenant_id is distinct from old.tenant_id
       or new.sample_id is distinct from old.sample_id
       or new.verified_by is distinct from old.verified_by
       or new.released_by is distinct from old.released_by
       or new.verified_at is distinct from old.verified_at
       or new.released_at is distinct from old.released_at
       or new.verification_token is distinct from old.verification_token then
      raise exception 'Released reports are immutable';
    end if;
  end if;
  return new;
end;
$fn$;

drop trigger if exists trg_guard_report_mutation on public.reports;
create trigger trg_guard_report_mutation
before update or delete on public.reports
for each row execute function public.nidan_guard_report_mutation();

revoke all on function public.nidan_guard_report_mutation() from public, anon, authenticated;

create or replace function public.nidan_release_report(p_report_id uuid)
returns public.reports
language plpgsql
set search_path = public
as $fn$
declare
  r public.reports;
  t uuid;
  bad integer;
  active integer;
  agg jsonb;
begin
  if public.current_role() <> all(array['owner','admin','pathologist']) then
    raise exception 'Only owner, admin or pathologist can release reports';
  end if;
  t := public.current_tenant_id();
  select * into r from public.reports where id=p_report_id and tenant_id=t for update;
  if not found then raise exception 'Report not found'; end if;
  if r.status='released' then raise exception 'Report already released'; end if;
  if r.status <> 'draft' then raise exception 'Only draft reports can be released'; end if;

  select count(*) into active
  from public.test_order_items i
  join public.test_orders o on o.id=i.order_id
  where o.sample_id=r.sample_id and o.tenant_id=t and i.status<>'cancelled';
  if active=0 then raise exception 'Cannot release a report without test results'; end if;

  select count(*) into bad
  from public.test_order_items i
  join public.test_orders o on o.id=i.order_id
  where o.sample_id=r.sample_id and o.tenant_id=t
    and i.status not in ('verified','released','cancelled');
  if bad>0 then raise exception 'All test results must be verified before release'; end if;

  select coalesce(jsonb_agg(jsonb_build_object(
    'test_code',i.test_code,
    'test_name',i.test_name,
    'status',i.status,
    'result',i.result_data
  ) order by i.created_at),'[]'::jsonb') into agg
  from public.test_order_items i
  join public.test_orders o on o.id=i.order_id
  where o.sample_id=r.sample_id and o.tenant_id=t and i.status<>'cancelled';

  update public.reports
  set status='released',
      result_data=agg,
      verified_by=coalesce(verified_by,auth.uid()),
      released_by=auth.uid(),
      verified_at=coalesce(verified_at,now()),
      released_at=now(),
      updated_at=now()
  where id=r.id
  returning * into r;

  update public.test_order_items i
  set status='released'
  from public.test_orders o
  where i.order_id=o.id
    and o.sample_id=r.sample_id
    and o.tenant_id=t
    and i.status='verified';

  return r;
end;
$fn$;

revoke all on function public.nidan_release_report(uuid) from public, anon;
grant execute on function public.nidan_release_report(uuid) to authenticated;
