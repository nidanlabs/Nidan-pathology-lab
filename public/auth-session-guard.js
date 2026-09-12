// Authentication session guard is intentionally disabled here.
// Access authorization is enforced by Supabase Auth + profiles RLS + database policies.
// The previous client-side guard could incorrectly sign out valid users when a profile
// read temporarily failed, producing a false "laboratory access is inactive" lockout.
(() => {})();
