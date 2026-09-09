-- Fix authenticated profile lookup for login/session guards.
-- Users must always be able to read their own profile; tenant-scoped
-- visibility remains available for authorized authenticated users.

DROP POLICY IF EXISTS profiles_select_own_tenant ON public.profiles;

CREATE POLICY profiles_select_own_tenant
ON public.profiles
FOR SELECT
TO authenticated
USING (
  user_id = auth.uid()
  OR tenant_id = private.current_tenant_id()
);
