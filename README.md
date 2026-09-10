# NIDAN Pathology Lab

Professional pathology laboratory information system (LIMS) with a Supabase-backed multi-tenant application workspace and a custom NIDAN LIMS package.

## Current architecture
- Browser application: static HTML/CSS/JavaScript
- Supabase Auth + PostgreSQL + Row Level Security
- Multi-tenant patient, sample, order, report and billing data model
- Custom NIDAN LIMS extension under `custom/nidan.lims`
- Vercel deployment for the browser application
- SENAITE/Plone buildout retained as a legacy integration path

## End-to-end laboratory workflow
The production browser workflow is designed around:

**Patient → Sample → Tests → Billing → Results → Verification → Report → Release → Print/PDF/Share**

### Patient
- Patient registration with contact details
- Tenant-scoped patient records
- Duplicate-safe patient identifiers

### Sample
- Sample accessioning linked to the patient
- Tenant-scoped accession and sample identifiers
- Patient/sample consistency checks

### Test order
- Multiple tests per sample
- Server-controlled order lifecycle
- Ordered → processing → completed status synchronization
- Completed/cancelled records protected by database rules

### Result entry
- Test-specific parameter definitions
- Required result validation
- Abnormal-result flagging
- Verification controls for authorized laboratory roles
- Verified/released results become locked

### Billing
- Invoice and invoice-item records linked to patient/sample
- Discount and payment handling
- Financial consistency enforced server-side

### Reports
- Draft report creation from the test order
- Verification and release safeguards
- Released reports are immutable
- Printing/sharing is restricted to released reports
- Report verification flow and QR/verification support

## Security
- Row Level Security is enabled on application tables.
- Tenant and role checks are enforced server-side.
- Verification/release operations use protected database functions.
- Browser code must contain only the Supabase publishable key; service-role keys must never be committed.
- Authentication authorization is not trusted to a client-only session guard.

## Testing and CI
The main `NIDAN CI` workflow runs the supported production checks:
- Domain tests
- NIDAN package build

The legacy SENAITE/Plone buildout is isolated into a manual `Legacy SENAITE Integration` workflow because the historical Plone/SENAITE dependency tree contains Python-2-only packages that are not a supported production runtime for the browser application.

## Configuration
The frontend uses `config.js` for the Supabase project URL and publishable key. Never place a service-role key in browser code or Git. For local/private configuration, create `config.local.js` and keep it untracked.

## Commercial-readiness note
The core application workflow and database safeguards are implemented, but commercial launch still requires operational checks such as production-domain configuration, backup/retention policy, monitoring, customer onboarding, payment-provider integration where required, and final security/compliance review.
