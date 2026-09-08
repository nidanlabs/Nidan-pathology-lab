-- Commercial hardening: private helper/trigger functions must never be directly executable by API roles.
-- Public RPCs remain exposed only through their explicit grants.
revoke all on all functions in schema private from public, anon, authenticated;

revoke all on function private.current_role() from public, anon, authenticated;
revoke all on function private.current_tenant_id() from public, anon, authenticated;
revoke all on function private.nidan_admin_update_user_profile(uuid, text, boolean) from public, anon, authenticated;
