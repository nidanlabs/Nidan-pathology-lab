insert into storage.buckets (id,name,public) values ('lab-letterheads','lab-letterheads',true) on conflict (id) do update set public=true;

drop policy if exists "lab letterhead upload" on storage.objects;
drop policy if exists "lab letterhead update" on storage.objects;
drop policy if exists "lab letterhead delete" on storage.objects;
create policy "lab letterhead upload" on storage.objects for insert to authenticated with check (bucket_id='lab-letterheads' and (storage.foldername(name))[1]=(select tenant_id::text from public.profiles where user_id=auth.uid() limit 1) and public.current_role() in ('owner','admin'));
create policy "lab letterhead update" on storage.objects for update to authenticated using (bucket_id='lab-letterheads' and (storage.foldername(name))[1]=(select tenant_id::text from public.profiles where user_id=auth.uid() limit 1) and public.current_role() in ('owner','admin')) with check (bucket_id='lab-letterheads' and (storage.foldername(name))[1]=(select tenant_id::text from public.profiles where user_id=auth.uid() limit 1) and public.current_role() in ('owner','admin'));
create policy "lab letterhead delete" on storage.objects for delete to authenticated using (bucket_id='lab-letterheads' and (storage.foldername(name))[1]=(select tenant_id::text from public.profiles where user_id=auth.uid() limit 1) and public.current_role() in ('owner','admin'));