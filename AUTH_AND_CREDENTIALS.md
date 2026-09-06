# MailerLite Connector — Auth & Credentials Standard

## Authentication Scheme
- **Mechanism:** HTTP Bearer Authentication
- **Header:** `Authorization: Bearer <api_key>`
- **Token Generation:** Generated via MailerLite Account Dashboard -> Integrations -> API.

## Security & Scoping
- Redaction: all client errors, logger statements, and debug dumps redact tokens (`_sanitize_msg`).
- Storage: tokens are stored encrypted in connection storage and never transmitted in logs.
- Multi-tenancy: isolated via `connection_id`.
