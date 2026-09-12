CREATE OR REPLACE FUNCTION private.expected_result_codes(p_test_code text)
RETURNS text[]
LANGUAGE sql
IMMUTABLE
SECURITY DEFINER
SET search_path TO ''
AS $function$
  select case upper(coalesce(p_test_code,''))
    when 'CBC' then array['HB','RBC','HCT','MCV','MCH','MCHC','RDW_CV','WBC','NEUT','LYMPH','MONO','EOS','BASO','PLT','MPV']
    when 'LFT' then array['TBIL','DBIL','ALT','AST','ALP','TP','ALB']
    when 'RFT' then array['UREA','CREAT','URIC','SOD','POT']
    when 'LIPID' then array['TC','TG','HDL','LDL']
    when 'TSH' then array['TSH']
    when 'WIDAL' then array['TO','TH','AH','BH']
    when 'ESR' then array['ESR']
    when 'CRP' then array['CRP']
    when 'ASO' then array['ASO']
    when 'RA' then array['RA']
    when 'FBS' then array['FBS']
    when 'PPBS' then array['PPBS']
    when 'RBS' then array['RBS']
    when 'HBA1C' then array['HBA1C']
    when 'DENGUE_NS1' then array['NS1']
    when 'DENGUE_IGM' then array['DENGUE_IGM']
    when 'DENGUE_IGG_IGM' then array['IGG','IGM']
    when 'DENGUE_PANEL' then array['NS1','IGM','IGG']
    when 'MALARIA' then array['MALARIA']
    when 'URINE_RM' then array['COLOUR','APPEAR','PH','PROTEIN','SUGAR','RBC','PUS']
    when 'URINE_RME' then array['COLOUR','APPEAR','PH','PROTEIN','SUGAR','RBC','PUS']
    when 'URINE_CULTURE' then array['RESULT']
    when 'STOOL_RM' then array['APPEAR','OCCULT','WBC','RBC']
    when 'STOOL' then array['APPEAR','OCCULT','WBC','RBC']
    when 'BT_CT' then array['BT','CT']
    when 'PT_INR' then array['PT','INR']
    when 'APTT' then array['APTT']
    when 'IRON' then array['IRON']
    when 'FERRITIN' then array['FERRITIN']
    when 'B12' then array['B12']
    when 'VIT_D' then array['VITD']
    when 'CALCIUM' then array['CALCIUM']
    when 'PHOSPHORUS' then array['PHOSPHORUS']
    when 'MAGNESIUM' then array['MAGNESIUM']
    when 'AMYLASE' then array['AMYLASE']
    when 'LIPASE' then array['LIPASE']
    when 'GGT' then array['GGT']
    when 'LDH' then array['LDH']
    when 'BILIRUBIN' then array['TBIL','DBIL']
    when 'ALBUMIN' then array['ALB']
    when 'TOTAL_PROTEIN' then array['TP']
    when 'SODIUM' then array['SODIUM']
    when 'POTASSIUM' then array['POTASSIUM']
    when 'CHLORIDE' then array['CHLORIDE']
    when 'HIV' then array['HIV']
    when 'HBSAG' then array['HBSAG']
    when 'HCV' then array['HCV']
    when 'VDRL' then array['VDRL']
    when 'THYROID_PROFILE' then array['TSH','FT3','FT4']
    when 'FT3' then array['FT3']
    when 'FT4' then array['FT4']
    when 'TROPONIN_I' then array['TROPONIN']
    when 'CK_MB' then array['CKMB']
    when 'CORTISOL' then array['CORTISOL']
    else array[]::text[]
  end;
$function$;

CREATE OR REPLACE FUNCTION private.guard_test_order_item_update()
RETURNS trigger
LANGUAGE plpgsql
SET search_path TO ''
AS $function$
declare r text; required text[]; k text; data jsonb;
begin
  r := public.current_role();
  if OLD.status = 'released' then raise exception 'Released results are immutable'; end if;
  if OLD.status = 'verified' then
    if NEW.status = 'released' and r in ('owner','admin','pathologist') and NEW.result_data is not distinct from OLD.result_data then return NEW; end if;
    raise exception 'Verified results are immutable until controlled report release';
  end if;
  if NEW.status = 'verified' and r not in ('owner','admin','pathologist') then raise exception 'Only owner, admin or pathologist can verify results'; end if;
  if NEW.status = 'released' and OLD.status <> 'verified' then raise exception 'Only verified results can be released'; end if;
  if NEW.status = 'result_entered' then
    data := coalesce(NEW.result_data,'{}'::jsonb);
    if jsonb_typeof(data) <> 'object' or not exists (
      select 1 from jsonb_each(case when jsonb_typeof(data)='object' then data else '{}'::jsonb end)
    ) then raise exception 'Cannot save an empty result'; end if;
    if exists (select 1 from jsonb_each_text(case when jsonb_typeof(data)='object' then data else '{}'::jsonb end) e where btrim(e.value)='') then raise exception 'Cannot save a result with empty values'; end if;
    required := private.expected_result_codes(NEW.test_code);
    if coalesce(array_length(required,1),0) > 0 then
      foreach k in array required loop
        if not (data ? k) or btrim(coalesce(data->>k,''))='' then raise exception 'All result parameters must be entered before saving'; end if;
      end loop;
    end if;
  end if;
  return NEW;
end;
$function$;

CREATE OR REPLACE FUNCTION public.nidan_verify_test_item(p_item_id uuid)
RETURNS test_order_items
LANGUAGE plpgsql
SET search_path TO 'public'
AS $function$
declare r public.test_order_items; required text[]; k text; data jsonb;
begin
  if public.current_role() <> all(array['owner','admin','pathologist']) then raise exception 'Only owner, admin or pathologist can verify results'; end if;
  select i.* into r from public.test_order_items i where i.id=p_item_id and i.tenant_id=public.current_tenant_id() for update;
  if not found then raise exception 'Result item not found'; end if;
  if r.status <> 'result_entered' then raise exception 'Only result-entered items can be verified'; end if;
  data := coalesce(r.result_data,'{}'::jsonb);
  if jsonb_typeof(data) <> 'object' or not exists (
    select 1 from jsonb_each(case when jsonb_typeof(data)='object' then data else '{}'::jsonb end)
  ) then raise exception 'Cannot verify an empty result'; end if;
  if exists (select 1 from jsonb_each_text(case when jsonb_typeof(data)='object' then data else '{}'::jsonb end) e where btrim(e.value)='') then raise exception 'Cannot verify a result with empty values'; end if;
  required := private.expected_result_codes(r.test_code);
  if coalesce(array_length(required,1),0)>0 then
    foreach k in array required loop
      if not (data ? k) or btrim(coalesce(data->>k,''))='' then raise exception 'All result parameters must be entered before verification'; end if;
    end loop;
  end if;
  update public.test_order_items set status='verified' where id=p_item_id returning * into r;
  return r;
end;
$function$;

CREATE OR REPLACE FUNCTION public.nidan_release_report(p_report_id uuid)
RETURNS reports
LANGUAGE plpgsql
SET search_path TO 'public'
AS $function$
declare
  r public.reports;
  t uuid;
  bad integer;
  active integer;
  agg jsonb;
begin
  if public.current_role() <> all(array['owner','admin','pathologist']) then raise exception 'Only owner, admin or pathologist can release reports'; end if;
  t := public.current_tenant_id();
  select * into r from public.reports where id=p_report_id and tenant_id=t for update;
  if not found then raise exception 'Report not found'; end if;
  if r.status='released' then raise exception 'Report already released'; end if;
  if r.status <> 'draft' then raise exception 'Only draft reports can be released'; end if;
  select count(*) into active from public.test_order_items i join public.test_orders o on o.id=i.order_id where o.sample_id=r.sample_id and o.tenant_id=t and i.status<>'cancelled';
  if active=0 then raise exception 'Cannot release a report without test results'; end if;
  select count(*) into bad
  from public.test_order_items i
  join public.test_orders o on o.id=i.order_id
  where o.sample_id=r.sample_id and o.tenant_id=t and (
    i.status not in ('verified','released','cancelled')
    or jsonb_typeof(coalesce(i.result_data,'{}'::jsonb)) <> 'object'
    or not exists (
      select 1 from jsonb_each(case when jsonb_typeof(coalesce(i.result_data,'{}'::jsonb))='object' then coalesce(i.result_data,'{}'::jsonb) else '{}'::jsonb end)
    )
    or exists (
      select 1 from jsonb_each_text(case when jsonb_typeof(coalesce(i.result_data,'{}'::jsonb))='object' then coalesce(i.result_data,'{}'::jsonb) else '{}'::jsonb end) e where btrim(e.value)=''
    )
  );
  if bad>0 then raise exception 'Every test result must be entered and verified before release'; end if;
  select coalesce(jsonb_agg(jsonb_build_object('test_code',i.test_code,'test_name',i.test_name,'status',i.status,'result',i.result_data) order by i.created_at),'[]'::jsonb) into agg
  from public.test_order_items i join public.test_orders o on o.id=i.order_id
  where o.sample_id=r.sample_id and o.tenant_id=t and i.status<>'cancelled';
  update public.reports set status='released',result_data=agg,verified_by=coalesce(verified_by,auth.uid()),released_by=auth.uid(),verified_at=coalesce(verified_at,now()),released_at=now(),updated_at=now() where id=r.id returning * into r;
  update public.test_order_items i set status='released' from public.test_orders o where i.order_id=o.id and o.sample_id=r.sample_id and o.tenant_id=t and i.status='verified';
  return r;
end;
$function$;
