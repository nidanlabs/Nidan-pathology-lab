# NIDAN Supabase Integration

## Project

- Supabase project: `Nidan pathology lab`
- Project ref: `kisezyvotaznkdfgghul`
- Region: `ap-south-1`

## Configuration

Set these environment variables in the runtime/deployment environment:

- `SUPABASE_URL=https://kisezyvotaznkdfgghul.supabase.co`
- `SUPABASE_PUBLISHABLE_KEY=<your publishable key>`

Do not commit real keys or service-role credentials.

## Database foundation

The Supabase database contains tenant-aware tables for:

- `tenants`
- `profiles`
- `patients`
- `samples`
- `reports`

Row Level Security (RLS) is enabled and tenant isolation is based on the authenticated user's active profile.

## Authentication model

Supabase Auth owns credentials and sessions. The NIDAN application stores only the user-to-tenant mapping and application role in `profiles`.

Supported roles:

- owner
- admin
- technician
- pathologist
- receptionist

Profile role/tenant changes must not be self-service. Administrative changes should be performed by trusted server-side code.

## Source of truth

The SQL migration reference is stored under `supabase/migrations/`. The migration was already applied to the production Supabase project; do not re-run the same DDL manually against production.
