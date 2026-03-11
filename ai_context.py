"""
AI context for the Quotes module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Quotes

### Models

**QuoteSeries** — Numbering series for quotes (e.g., QT-00001, PR-00001).
- `name`, `prefix` (unique per hub), `next_number`, `number_digits` (default 5)
- `is_default` (only one per hub), `is_active`
- `generate_number()`: Returns formatted number like "QT-00001" and increments counter

**QuoteSettings** — Per-hub configuration (singleton).
- `default_validity_days` (default 30), `default_series` FK → QuoteSeries
- `default_notes`, `default_terms`
- `tax_rate` (default 21%), `show_tax`, `show_discount`
- Use `QuoteSettings.get_settings(hub_id)`

**Quote** — A quote/proposal/budget document.
- `quote_number` (assigned on send, not on creation), `series` FK → QuoteSeries, `title`
- `customer` FK → customers.Customer (nullable)
- `customer_name`, `customer_email`, `customer_phone`, `customer_address`: Snapshot fields (stable for PDFs)
- `related_lead` (UUIDField, optional): UUID of related lead
- `status`: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired' | 'converted'
- `notes`, `terms`
- `subtotal`, `discount_amount`, `discount_percent`, `tax_amount`, `tax_rate`, `total`
- `valid_until` (DateField)
- `sent_at`, `accepted_at`, `rejected_at`, `converted_at`, `rejection_reason`
- Methods: `calculate_totals()`, `mark_sent()`, `mark_accepted()`, `mark_rejected(reason)`, `mark_expired()`, `mark_converted()`
- `is_expired` property: True if status='sent' and valid_until < today

**QuoteLine** — Line items within a quote.
- `quote` FK → Quote (related_name='lines')
- `line_type`: 'product' | 'service' | 'custom'
- `product_id` (UUIDField, optional), `service_id` (UUIDField, optional)
- `description` (max 500 chars), `quantity` (decimal, 3 dp), `unit_price`
- `discount_percent` (line-level), `tax_rate`, `total` (auto-calculated on save)
- `sort_order`

### Key Flows

1. **Create quote**: Create Quote (status='draft') with customer snapshot → add QuoteLines → `quote.calculate_totals()` → save
2. **Send quote**: `quote.mark_sent()` → assigns quote_number from series, sets valid_until if not set, status='sent'
3. **Accept/Reject/Convert**: Call corresponding mark_* methods; only valid from 'sent' state; mark_converted() requires 'accepted' state
4. **Totals**: `calculate_totals()` sums lines, applies global discount_percent → computes tax on after-discount amount → total = (subtotal - discount) + tax
5. **Line total**: `quantity × unit_price × (1 - discount_percent/100)` — calculated automatically on QuoteLine.save()

### Relationships
- `Quote.customer` → customers.Customer
- `Quote.series` → QuoteSeries
- `QuoteLine.quote` → Quote
"""
