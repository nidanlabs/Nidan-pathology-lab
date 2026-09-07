# NIDAN Pathology Lab

Professional pathology laboratory information system (LIMS) based on SENAITE with a Supabase-backed multi-tenant application workspace.

## Architecture
- SENAITE Core 2.7.x
- SENAITE LIMS 2.7.x
- Custom NIDAN LIMS extension
- Supabase Auth + PostgreSQL + Row Level Security
- NIDAN browser dashboard (Step 1)

## Step 1 — Login & Dashboard
- Secure email/password login through Supabase Auth
- Tenant/profile and role display
- Dashboard metrics for patients, samples and reports
- Patient registration
- Sample accessioning
- Starter pathology test catalog
- Results, reports, billing, doctors and settings navigation
- Responsive desktop/mobile layout

## Planned modules
- Patient registration
- Sample accessioning and tracking
- Test catalog and result entry
- Pathology report generation
- Billing and payments
- Doctor/referral management
- Laboratory administration

## Configuration
The frontend uses `config.js` for the Supabase project URL and publishable key. Never place a service-role key in browser code or Git. For a local/private configuration, create `config.local.js` and keep it untracked.

## Repository status
Step 1 implemented on `main`: login + dashboard application shell and core patient/sample views. Subsequent steps will add the full test-order, result-verification, report-PDF, billing and administration workflows.
