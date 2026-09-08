-- Billing query indexes for production SaaS workloads.
create index if not exists payments_invoice_created_idx on public.payments(invoice_id, created_at desc);
create index if not exists invoice_items_invoice_idx on public.invoice_items(invoice_id, created_at);
create index if not exists invoices_created_idx on public.invoices(created_at desc);
