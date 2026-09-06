# MailerLite Connector — Connector Discovery

## Discovery Overview
- **Vendor:** MailerLite (`https://www.mailerlite.com`)
- **API Documentation:** `https://developers.mailerlite.com/docs`
- **OpenAPI Reference:** `https://connect.mailerlite.com/api`
- **Target Category:** C30. Email Marketing & Newsletter

## Resource Schema Coverage
| Resource | Supported Operations | Official Path | Description |
|---|---|---|---|
| Subscribers | List, Get, Create, Update, Delete | `/subscribers` | Contact records with email, status, and fields |
| Campaigns | List, Get, Create, Update, Delete | `/campaigns` | Newsletter and marketing broadcast campaigns |
| Lists / Groups | List, Get, Create, Update, Delete | `/groups` | Static mailing lists |
| Segments | List, Get, Create, Update, Delete | `/segments` | Dynamic filter-based audience segments |
| Automations | List, Get, Create, Update, Delete | `/automations` | Workflow automations and triggers |
| Templates | List, Get, Create, Update, Delete | `/templates` | Reusable responsive email HTML templates |
| Audits | Health Check, Analytics | Composite | Bounce rate, spam complaint, and deliverability checks |

## Rate Limits and Quotas
- Default rate limit: 120 requests per minute per API token.
- Returns HTTP 429 with standard `Retry-After` header.
