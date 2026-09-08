alter table public.lab_settings
  add column if not exists reference_ranges jsonb not null default '{}'::jsonb;

comment on column public.lab_settings.reference_ranges is
  'Tenant-specific validated reference ranges keyed by test parameter code. Example: {"HB":{"unit":"g/dL","low":13,"high":17}}';

create index if not exists lab_settings_reference_ranges_gin_idx
  on public.lab_settings using gin (reference_ranges);
