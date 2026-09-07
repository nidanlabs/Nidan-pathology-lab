-- NIDAN Pathology Lab - Supabase foundation schema
-- Applied to Supabase project: kisezyvotaznkdfgghul
-- Keep this file in source control as the canonical migration reference.

create extension if not exists pgcrypto;

create table if not exists public.tenants (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  tenant_id uuid not null references public.tenants(id) on delete restrict,
  email text,
  role text not null default 'receptionist' check (role in ('owner','admin','technician','pathologist','receptionist')),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.patients (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete restrict,
  patient_id text not null,
  first_name text not null,
  last_name text,
  date_of_birth date,
  sex text check (sex in ('M','F','O')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, patient_id)
);

create table if not exists public.samples (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete restrict,
  accession_number text not null,
  patient_id uuid not null references public.patients(id) on delete restrict,
  status text not null default 'received',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, accession_number)
);

create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references public.tenants(id) on delete restrict,
  sample_id uuid not null references public.samples(id) on delete restrict,
  status text not null default 'draft',
  result_data jsonb not null default '{}'::jsonb,
  verified_by uuid references auth.users(id),
  released_by uuid references auth.users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists patients_tenant_id_idx on public.patients(tenant_id);
create index if not exists samples_tenant_id_idx on public.samples(tenant_id);
create index if not exists reports_tenant_id_idx on public.reports(tenant_id);

create or replace function public.current_tenant_id()
returns uuid
language sql
stable
security definer
set search_path = public
as $$
  select tenant_id from public.profiles
  where user_id = auth.uid() and active = true
  limit 1;
$$;

create or replace function public.current_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select role from public.profiles
  where user_id = auth.uid() and active = true
  limit 1;
$$;

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  return new;
end;
$$;

alter table public.tenants enable row level security;
alter table public.profiles enable row level security;
alter table public.patients enable row level security;
alter table public.samples enable row level security;
alter table public.reports enable row level security;

-- Tenant-isolation policies. Role-specific write rules are added by the application layer/RLS hardening migration.
drop policy if exists tenants_select_own on public.tenants;
create policy tenants_select_own on public.tenants
for select to authenticated
using (id = public.current_tenant_id());

drop policy if exists profiles_select_own_tenant on public.profiles;
create policy profiles_select_own_tenant on public.profiles
for select to authenticated
using (tenant_id = public.current_tenant_id());

-- No self-service role/tenant mutation. Profile administration should be performed server-side.
drop policy if exists profiles_update_self on public.profiles;

-- Tenant-scoped CRUD foundation.
drop policy if exists patients_tenant_access on public.patients;
create policy patients_tenant_access on public.patients
for all to authenticated
using (tenant_id = public.current_tenant_id())
with check (tenant_id = public.current_tenant_id());

drop policy if exists samples_tenant_access on public.samples;
create policy samples_tenant_access on public.samples
for all to authenticated
using (tenant_id = public.current_tenant_id())
with check (tenant_id = public.current_tenant_id());

drop policy if exists reports_tenant_access on public.reports;
create policy reports_tenant_access on public.reports
for all to authenticated
using (tenant_id = public.current_tenant_id())
with check (tenant_id = public.current_tenant_id());

revoke execute on function public.current_tenant_id() from anon;
revoke execute on function public.current_role() from anon;
revoke execute on function public.handle_new_user() from anon, authenticated;
grant execute on function public.current_tenant_id() to authenticated;
grant execute on function public.current_role() to authenticated;
