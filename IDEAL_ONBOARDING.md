# MailerLite Connector — Ideal Onboarding Flow

1. **Prerequisites:**
   - Active MailerLite account (Free or Growing Business plan).
   - Generated API Key from Integrations settings.
2. **Setup:**
   - Open MailerLite Connector panel in Imperal Cloud.
   - Enter friendly label and paste API Key.
   - Click Connect.
3. **Verification:**
   - The connector validates credentials by calling `GET /subscribers?limit=1`.
   - On success, connection is saved and available for workflows.
