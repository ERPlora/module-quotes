# Quotes Module

Create and manage quotes, proposals and budgets.

## Features

- Create quotes, proposals, and budgets with full lifecycle management (draft, sent, accepted, rejected, expired, converted)
- Configurable numbering series with custom prefixes and auto-incrementing counters (e.g., QT-00001, PR-00001)
- Line items supporting product, service, and custom types with per-line discounts and tax rates
- Global discount (percentage or fixed amount) and tax calculation on quotes
- Automatic validity period tracking with expiration detection
- Customer snapshot denormalization for PDF stability (name, email, phone, address stored on quote)
- Optional link to leads via UUID reference
- Status transition methods: send, accept, reject (with reason), expire, and convert
- Configurable default notes, terms and conditions, tax rate, and validity period via settings
- Toggle visibility of tax breakdown and discount columns

## Installation

This module is installed automatically via the ERPlora Marketplace.

**Dependencies**: Requires `customers` module.

## Configuration

Access settings via: **Menu > Quotes > Settings**

Configurable options include:

- Default validity period (days)
- Default numbering series
- Default notes and terms & conditions
- Default tax rate
- Show/hide tax breakdown and discount columns

## Usage

Access via: **Menu > Quotes**

### Views

| View | URL | Description |
|------|-----|-------------|
| Dashboard | `/m/quotes/dashboard/` | Overview of quote activity and statistics |
| Quotes | `/m/quotes/list/` | List and manage all quotes |
| Series | `/m/quotes/series/` | Manage quote numbering series |
| Settings | `/m/quotes/settings/` | Module configuration |

## Models

| Model | Description |
|-------|-------------|
| `QuoteSeries` | Numbering series with prefix, auto-incrementing counter, and digit formatting |
| `QuoteSettings` | Per-hub configuration for defaults (validity, tax rate, notes, terms, display options) |
| `Quote` | Quote document with customer details, status lifecycle, amounts, validity date, and timestamps |
| `QuoteLine` | Individual line item with type (product/service/custom), quantity, unit price, discount, tax rate, and sort order |

## Permissions

| Permission | Description |
|------------|-------------|
| `quotes.view_quote` | View quotes |
| `quotes.add_quote` | Create new quotes |
| `quotes.change_quote` | Edit existing quotes |
| `quotes.delete_quote` | Delete quotes |
| `quotes.send_quote` | Send quotes to customers |
| `quotes.accept_quote` | Accept quotes |
| `quotes.convert_quote` | Convert accepted quotes to sales or invoices |
| `quotes.manage_settings` | Manage module settings |

## Integration with Other Modules

- **customers**: Links quotes to customer records via foreign key. Customer data is snapshotted on the quote for document stability.

## License

MIT

## Author

ERPlora Team - support@erplora.com
