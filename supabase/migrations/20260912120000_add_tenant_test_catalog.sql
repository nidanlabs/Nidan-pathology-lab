ALTER TABLE public.lab_settings
  ADD COLUMN IF NOT EXISTS test_catalog jsonb NOT NULL DEFAULT '{}'::jsonb;

COMMENT ON COLUMN public.lab_settings.test_catalog IS 'Tenant-specific test catalog overrides keyed by test code: {CODE:{name,price,params:[{code,label,unit,low,high}]}}';