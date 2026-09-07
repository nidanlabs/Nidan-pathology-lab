-- NIDAN: patient registration uses age instead of date of birth.
ALTER TABLE public.patients
  ADD COLUMN IF NOT EXISTS age integer;

ALTER TABLE public.patients
  ALTER COLUMN date_of_birth DROP NOT NULL;

ALTER TABLE public.patients
  ADD CONSTRAINT patients_age_valid
  CHECK (age IS NULL OR (age >= 0 AND age <= 150));
