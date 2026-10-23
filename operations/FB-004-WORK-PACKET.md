# FB-004: close the local validation evidence gap

Date: 2026-10-23 (America/New_York). Base: main at 31c6dc5; PRs #2 and #3 verified merged. Work branch: fb-004-negative-input-evidence. Audience: existing private repository only.

## Outcome and acceptance

Preserve FB-003 user-observed success, test the exported validation code, provide bounded negative HTTP probes, and return to commercial qualification. This is a technical milestone, not revenue or production readiness.

- User evidence recorded separately in ../evidence/FB004-VALIDATION.md.
- Actual exported Code nodes reject invalid intent/email/request ID with statusCode 400 and field errors in offline tests.
- Invalid IDs become null instead of reflecting arbitrary input; malformed bodies cannot fall back to webhook-envelope fields. Valid routing is unchanged.
- Live acceptance requires HTTP 400, application/json and exact error body for each negative case. **Pending:** current test endpoint returns 404. Do not count it as a validation pass or activate the workflow to bypass it.
- Stop after this boundary; no general orchestration, new providers or production hardening project.

## Run locally

From repository root, Python 3 and Node 22 suffice; no installation or paid service required:

```powershell
node --test prototypes/test-fb004.cjs
python -m unittest discover -s prototypes -p test_fb004_http_probe.py -v
```

For actual n8n HTTP evidence, inspect/import the updated prototypes/fb003-local-api-demo.json into a disposable **inactive** local workflow. Preserve the existing workflow; avoid concurrent test registrations using the same path. Confirm the Code nodes match this branch and Respond to Webhook uses JSON body and dynamic response code. Before **each** command select Listen for Test Event, then run that one command:

```powershell
python prototypes/fb004_http_probe.py valid
python prototypes/fb004_http_probe.py invalid-intent
python prototypes/fb004_http_probe.py invalid-email
python prototypes/fb004_http_probe.py invalid-request-id
```

These are four separate operator steps, not an unattended batch. Expected statuses: 200, 400, 400, 400. Probe checks exact error strings, false ok, no provider/result on errors, and null for invalid ID. A missing listener, empty 200, redirect, HTML, unexpected fields or wrong error fails with exit 1. Capture sanitized result lines, date, n8n version and imported workflow hash; classify user-run evidence as user-observed. Never replace the historical FB-003 receipt with a newly inferred result.

## Security review

Export is inactive, has four local nodes, no credentials, pinned data, HTTP Request node or paid provider. Response mode is responseNode; responseCode reads statusCode; responseBody serializes only the constructed response. Email and raw body are not returned. Invalid ID reflection removed. Email validation is basic shape checking, not ownership/deliverability verification. Request IDs are not idempotency enforcement.

Probe is fixed to 127.0.0.1:5678/webhook-test/fb003-demo, bypasses proxy/DNS, has a 10-second socket timeout, reads at most 4097 bytes, rejects oversized responses and never follows redirects or retries automatically. It prints no remote body/header/error text.

Unauthenticated workflow is still unsuitable for public access. Inactive state and localhost test requests do **not** prove host isolation: listener/firewall/tunnel exposure remains unverified. Existing STATUS.md noted wildcard listeners historically; that is not a current bind inspection. Do not change or expose services. Before a buyer environment, separately agree authentication, access boundaries, rate/body limits, retention and replay/idempotency needs. n8n can retain webhook input in execution history even when response omits email; use synthetic input only. No machine logs, credentials or customer data belong in Git.

Official references checked 2026-10-23: [Webhook testing](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/workflow-development/) and [Respond to Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/). They document test registration and response-code configuration; they do not verify this machine.

## CI decision and rollback

No CI workflow added. Repeatable local regression commands cover this bounded change; private-repository Actions allowance/billing was not verified and no spending is authorized. Reconsider a static-only CI job if recurring changes justify it and budget/runner availability is established. No deployment, secrets, package downloads or n8n activation in CI.

Rollback: revert this branch's workflow edit or reimport the prior JSON into an inactive scratch copy. No existing live workflow was edited, no service restarted, no database modified.

## Commercial gate first

Use the existing operations/DIRECT_OFFER.md qualification draft. Before any send: owner confirms sender account, delivery availability and explicit one-message authorization; recheck C11 availability and scope fit. Budget/deadline/identity remain unqualified; USD100 is a conditional proposal, not accepted pricing. Do not tailor further engineering until the buyer's problem fits. No customer outreach, invoices, paid calls or spending occurred in FB-004; incremental paid-service calls: 0. Operator labor was not timed and is not represented as free. Revenue remains unverified/zero recorded.
