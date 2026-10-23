# FB-003: Local n8n Proof of Capability

Status: **workflow JSON authored; n8n import and runtime execution NOT verified**.

## Purpose
Showcase webhook intake → bounded input validation → API-style mock routing → structured JSON response using only local n8n Code nodes. No model, account, outside API, or paid cloud dependency.

## Import (only while parked/at your PC)
1. Download `fb003-local-api-demo.json`, open local n8n (previously reported at version 2.41.6), and import the file as a workflow.
2. Keep workflow **inactive**. Select **Listen for Test Event** on Webhook.
3. Send one synthetic test request to the test URL shown in n8n, e.g.:
```powershell
$body = @{request_id='test_001';email='demo@example.org';intent='support'} | ConvertTo-Json
Invoke-RestMethod -Method Post -ContentType 'application/json' -Body $body -Uri 'http://localhost:5678/webhook-test/fb003-demo'
```
4. Expected valid result: HTTP 200, `ok:true`, `provider:local-mock`, `route:helpdesk`.
5. Change intent to `sales` (expected `sales-queue`), then to `unknown` (expected 400 with validation errors). Inspect actual responses and execution logs. **Do not claim passing runtime tests before running them.**

## Security
This webhook has no authentication. **Never activate/publish this endpoint or expose it to the internet as-is.** Before a real buyer integration: add authorization, rate limiting, payload-size limits, replay protection, audit retention policy, idempotency, and approved outbound destination credentials. No real client data; this demo deliberately avoids writing email addresses to output.

## Scope limitations
The provider is a local simulation. No remote HTTP Request node is called. This tests reusable flow/control structure, not HubSpot/Slack/CRM API credentials or an actual client integration.

## Market offer hypothesis
Offer a **fixed-scope n8n webhook/API diagnostic** with up-front acceptance criteria, an authorized staging environment, and a labor-inclusive quote. Pricing and buyer interest must be verified, not inferred from sample packages.

## QA gates
- Static JSON graph and JavaScript syntax checks: see corresponding evidence in PR; no claim of actual n8n execution.
- Run the above 3 tests in n8n locally.
- Capture sanitized outputs and environment versions.
- Record pass/fail and next steps in issue #1 before outreach.
