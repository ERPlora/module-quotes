# Quotes

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `quotes` |
| **Version** | `1.0.0` |
| **Icon** | `document-text-outline` |
| **Dependencies** | `customers` |

## Dependencies

This module requires the following modules to be installed:

- `customers`

## Models

### `QuoteSeries`

Quote numbering series.

Each series has a prefix and an auto-incrementing counter.
Examples: QT (quotes), PR (proposals), BU (budgets).

| Field | Type | Details |
|-------|------|---------|
| `name` | CharField | max_length=100 |
| `prefix` | CharField | max_length=10 |
| `next_number` | PositiveIntegerField |  |
| `is_default` | BooleanField |  |
| `is_active` | BooleanField |  |
| `number_digits` | PositiveSmallIntegerField |  |

**Methods:**

- `generate_number()` — Get and increment the next quote number.

Returns formatted quote number like "QT-00001".

### `QuoteSettings`

Per-hub quote configuration.

| Field | Type | Details |
|-------|------|---------|
| `default_validity_days` | PositiveIntegerField |  |
| `default_series` | ForeignKey | → `quotes.QuoteSeries`, on_delete=SET_NULL, optional |
| `default_notes` | TextField | optional |
| `default_terms` | TextField | optional |
| `tax_rate` | DecimalField |  |
| `show_tax` | BooleanField |  |
| `show_discount` | BooleanField |  |

**Methods:**

- `get_settings()` — Get or create settings for a hub.

### `Quote`

Quote / Proposal / Budget document.

| Field | Type | Details |
|-------|------|---------|
| `quote_number` | CharField | max_length=50, optional |
| `series` | ForeignKey | → `quotes.QuoteSeries`, on_delete=PROTECT |
| `title` | CharField | max_length=255, optional |
| `customer` | ForeignKey | → `customers.Customer`, on_delete=SET_NULL, optional |
| `customer_name` | CharField | max_length=255 |
| `customer_email` | EmailField | max_length=254, optional |
| `customer_phone` | CharField | max_length=50, optional |
| `customer_address` | TextField | optional |
| `related_lead` | UUIDField | max_length=32, optional |
| `status` | CharField | max_length=20, choices: draft, sent, accepted, rejected, expired, converted |
| `notes` | TextField | optional |
| `terms` | TextField | optional |
| `subtotal` | DecimalField |  |
| `discount_amount` | DecimalField |  |
| `discount_percent` | DecimalField |  |
| `tax_amount` | DecimalField |  |
| `tax_rate` | DecimalField |  |
| `total` | DecimalField |  |
| `valid_until` | DateField | optional |
| `sent_at` | DateTimeField | optional |
| `accepted_at` | DateTimeField | optional |
| `rejected_at` | DateTimeField | optional |
| `converted_at` | DateTimeField | optional |
| `rejection_reason` | TextField | optional |

**Methods:**

- `calculate_totals()` — Recalculate totals from line items.
- `mark_sent()` — Mark quote as sent. Assigns quote number if not yet assigned.
- `mark_accepted()` — Mark quote as accepted.
- `mark_rejected()` — Mark quote as rejected with optional reason.
- `mark_expired()` — Mark quote as expired.
- `mark_converted()` — Mark an accepted quote as converted (e.g. to sale/invoice).

**Properties:**

- `is_expired` — Check if quote has expired based on valid_until date.
- `days_until_expiry` — Return days until expiry, or None if no valid_until date.

### `QuoteLine`

Individual line item in a quote.

| Field | Type | Details |
|-------|------|---------|
| `quote` | ForeignKey | → `quotes.Quote`, on_delete=CASCADE |
| `line_type` | CharField | max_length=20, choices: product, service, custom |
| `product_id` | UUIDField | max_length=32, optional |
| `service_id` | UUIDField | max_length=32, optional |
| `description` | CharField | max_length=500 |
| `quantity` | DecimalField |  |
| `unit_price` | DecimalField |  |
| `discount_percent` | DecimalField |  |
| `tax_rate` | DecimalField |  |
| `total` | DecimalField |  |
| `sort_order` | PositiveSmallIntegerField |  |

**Methods:**

- `calculate_total()` — Calculate line total with discount.

## Cross-Module Relationships

| From | Field | To | on_delete | Nullable |
|------|-------|----|-----------|----------|
| `QuoteSettings` | `default_series` | `quotes.QuoteSeries` | SET_NULL | Yes |
| `Quote` | `series` | `quotes.QuoteSeries` | PROTECT | No |
| `Quote` | `customer` | `customers.Customer` | SET_NULL | Yes |
| `QuoteLine` | `quote` | `quotes.Quote` | CASCADE | No |

## URL Endpoints

Base path: `/m/quotes/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `list/` | `list` | GET |
| `series/` | `series` | GET |
| `quote_serieses/` | `quote_serieses_list` | GET |
| `quote_serieses/add/` | `quote_series_add` | GET/POST |
| `quote_serieses/<uuid:pk>/edit/` | `quote_series_edit` | GET |
| `quote_serieses/<uuid:pk>/delete/` | `quote_series_delete` | GET/POST |
| `quote_serieses/<uuid:pk>/toggle/` | `quote_series_toggle_status` | GET |
| `quote_serieses/bulk/` | `quote_serieses_bulk_action` | GET/POST |
| `quotes/` | `quotes_list` | GET |
| `quotes/add/` | `quote_add` | GET/POST |
| `quotes/<uuid:pk>/edit/` | `quote_edit` | GET |
| `quotes/<uuid:pk>/delete/` | `quote_delete` | GET/POST |
| `quotes/bulk/` | `quotes_bulk_action` | GET/POST |
| `settings/` | `settings` | GET |

## Permissions

| Permission | Description |
|------------|-------------|
| `quotes.view_quote` | View Quote |
| `quotes.add_quote` | Add Quote |
| `quotes.change_quote` | Change Quote |
| `quotes.delete_quote` | Delete Quote |
| `quotes.send_quote` | Send Quote |
| `quotes.accept_quote` | Accept Quote |
| `quotes.convert_quote` | Convert Quote |
| `quotes.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `accept_quote`, `add_quote`, `change_quote`, `convert_quote`, `send_quote`, `view_quote`
- **employee**: `add_quote`, `view_quote`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Dashboard | `speedometer-outline` | `dashboard` | No |
| Quotes | `document-text-outline` | `list` | No |
| Series | `layers-outline` | `series` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_quotes`

List quotes with optional filters. Returns quote number, customer, status, total.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter: draft, sent, accepted, rejected, expired, converted |
| `search` | string | No | Search by customer name or quote number |
| `limit` | integer | No | Max results (default 20) |

### `create_quote`

Create a new quote for a customer with line items.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Quote title |
| `customer_id` | string | No | Customer ID |
| `customer_name` | string | No | Customer name (if no customer_id) |
| `customer_email` | string | No | Customer email |
| `notes` | string | No | Additional notes |
| `valid_days` | integer | No | Days until expiry (default 30) |
| `lines` | array | No | Quote lines |

### `get_quote`

Get detailed quote info including line items and status timestamps.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `quote_id` | string | Yes | Quote ID |

### `update_quote_status`

Update quote status: send (draft→sent), accept (sent→accepted), reject (sent→rejected), convert (accepted→converted).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `quote_id` | string | Yes | Quote ID |
| `action` | string | Yes | Action: send, accept, reject, convert |
| `reason` | string | No | Rejection reason (for reject action) |

## File Structure

```
README.md
__init__.py
admin.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
migrations/
  0001_initial.py
  __init__.py
models.py
module.py
static/
  quotes/
    css/
      quotes.css
    js/
templates/
  quotes/
    pages/
      dashboard.html
      detail.html
      index.html
      list.html
      quote_add.html
      quote_edit.html
      quote_series_add.html
      quote_series_edit.html
      quote_serieses.html
      quotes.html
      series.html
      settings.html
    partials/
      dashboard_content.html
      detail_content.html
      panel_quote_add.html
      panel_quote_edit.html
      panel_quote_series_add.html
      panel_quote_series_edit.html
      panel_series_add.html
      quote_add_content.html
      quote_edit_content.html
      quote_lines.html
      quote_series_add_content.html
      quote_series_edit_content.html
      quote_serieses_content.html
      quote_serieses_list.html
      quotes_content.html
      quotes_list.html
      series_content.html
      settings_content.html
tests/
  __init__.py
  conftest.py
  test_models.py
  test_views.py
urls.py
views.py
```
