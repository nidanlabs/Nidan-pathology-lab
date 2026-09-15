-- Fix result-entry updates after private helper execution was hardened.
-- The trigger function calls private.expected_result_codes(), so it must execute
-- with its definer privileges rather than the authenticated caller's privileges.

create or replace function private.guard_test_order_item_update()
returns trigger
language plpgsql
security definer
set search_path to ''
as $function$
declare r text; required text[]; k text; data jsonb;
begin
  r := public.current_role();

  if OLD.status = 'released' then
    raise exception 'Released results are immutable';
  end if;

  if OLD.status = 'verified' then
    if NEW.status = 'released'
       and r in ('owner','admin','pathologist')
       and NEW.result_data is not distinct from OLD.result_data then
      return NEW;
    end if;
    raise exception 'Verified results are immutable until controlled report release';
  end if;

  if NEW.status = 'verified'
     and r not in ('owner','admin','pathologist') then
    raise exception 'Only owner, admin or pathologist can verify results';
  end if;

  if NEW.status = 'released' and OLD.status <> 'verified' then
    raise exception 'Only verified results can be released';
  end if;

  if NEW.status = 'result_entered' then
    data := coalesce(NEW.result_data,'{}'::jsonb);

    if jsonb_typeof(data) <> 'object'
       or not exists (
         select 1
         from jsonb_each(
           case when jsonb_typeof(data)='object' then data else '{}'::jsonb end
         )
       ) then
      raise exception 'Cannot save an empty result';
    end if;

    if exists (
      select 1
      from jsonb_each_text(
        case when jsonb_typeof(data)='object' then data else '{}'::jsonb end
      ) e
      where btrim(e.value)=''
    ) then
      raise exception 'Cannot save a result with empty values';
    end if;

    required := private.expected_result_codes(NEW.test_code);

    if coalesce(array_length(required,1),0) > 0 then
      foreach k in array required loop
        if not (data ? k) or btrim(coalesce(data->>k,''))='' then
          raise exception 'All result parameters must be entered before saving';
        end if;
      end loop;
    end if;
  end if;

  return NEW;
end;
$function$;

revoke all on function private.guard_test_order_item_update() from public, anon, authenticated;
