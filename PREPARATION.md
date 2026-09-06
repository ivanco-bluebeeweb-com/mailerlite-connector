# MailerLite Connector — Preparation

## Product Scope
Build a comprehensive Imperal connector for **MailerLite** under category **C30. Email Marketing & Newsletter**. The integration interfaces directly with the official **MailerLite REST API** (`https://connect.mailerlite.com/api`), providing full visibility and control over subscribers, campaigns, subscriber groups/lists, dynamic segments, automations, email templates, and audience health auditing.

## Official API Specifications
- **API Architecture:** RESTful JSON API
- **Base URL:** `https://connect.mailerlite.com/api`
- **Core Endpoints:**
  - `GET /subscribers` — list subscribers with status filtering and cursor pagination
  - `GET /subscribers/{id}` — detailed subscriber record with custom fields
  - `POST /subscribers` — create or upsert subscriber record
  - `DELETE /subscribers/{id}` — delete subscriber
  - `GET /campaigns` — list email broadcast campaigns
  - `GET /campaigns/{id}` — detailed campaign status and delivery metrics
  - `GET /groups` — static audience mailing lists (groups)
  - `GET /segments` — dynamic condition-based audience segments
  - `GET /automations` — multi-step nurture workflows
  - `GET /templates` — reusable email layout HTML templates
- **Authentication Model:** Bearer Token via `Authorization: Bearer <api_key>`
- **Mandatory Requirements:**
  - Strict error classification: HTTP 429 rate limits with Retry-After extraction, HTTP 401/403 differentiation (Standard B8/B10).
  - Sanitization of Bearer tokens in error traces and diagnostic payloads (Standard B8).
  - Multi-tenant connection tracking and isolation via `connection_id` (Standard B9).

## Delivery Gates
1. [x] Official API discovery completed with MailerLite REST API specifications.
2. [x] Core resource endpoints and Bearer auth verified against official docs.
3. [x] Five mandatory specification documents authored.
4. [x] Client implemented with B8-B10 compliance, secret redaction, and error mapping.
5. [x] Panels and schemas strictly validated against SDK contracts.
6. [ ] Live authenticated sandbox tests with real credentials (pending test account).
7. [ ] Post-audit PST Part D execution before Marketplace Review.
