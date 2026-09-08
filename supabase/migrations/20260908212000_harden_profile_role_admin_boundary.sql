create or replace function private.nidan_admin_update_user_profile(p_user_id uuid, p_role text, p_active boolean)
returns jsonb
language plpgsql
security definer
set search_path=''
as $fn$
declare
  v_tenant uuid;
  v_actor_role text;
  v_old_role text;
  v_old_active boolean;
begin
  select tenant_id, role into v_tenant, v_actor_role
  from public.profiles
  where user_id=auth.uid() and active=true;

  if v_tenant is null or v_actor_role not in ('owner','admin') then
    raise exception 'not authorized';
  end if;
  if p_role not in ('owner','admin','technician','pathologist','receptionist') then
    raise exception 'invalid role';
  end if;

  select role, active into v_old_role, v_old_active
  from public.profiles
  where user_id=p_user_id and tenant_id=v_tenant
  for update;
  if not found then raise exception 'user not found'; end if;

  if v_actor_role='admin' then
    if v_old_role='owner' then raise exception 'admin cannot modify an owner'; end if;
    if p_role='owner' then raise exception 'only owner can grant owner role'; end if;
  end if;

  if p_user_id=auth.uid() then
    if v_actor_role='owner' and p_role<>'owner' then raise exception 'owner cannot demote self'; end if;
    if not p_active then raise exception 'cannot deactivate current user'; end if;
  end if;

  update public.profiles set role=p_role, active=p_active, updated_at=now()
  where user_id=p_user_id and tenant_id=v_tenant;

  perform public.nidan_log_audit(p_action=>'update',p_entity_type=>'profile',p_entity_id=>p_user_id,
    p_details=jsonb_build_object('old_role',v_old_role,'new_role',p_role,'old_active',v_old_active,'new_active',p_active));

  return jsonb_build_object('user_id',p_user_id,'role',p_role,'active',p_active);
end;
$fn$;

revoke all on function private.nidan_admin_update_user_profile(uuid,text,boolean) from public;
revoke all on function public.nidan_admin_update_user_profile(uuid,text,boolean) from public, anon;
grant execute on function public.nidan_admin_update_user_profile(uuid,text,boolean) to authenticated;
