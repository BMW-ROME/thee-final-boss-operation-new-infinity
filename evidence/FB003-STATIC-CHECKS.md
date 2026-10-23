# FB-003 checks
Status: static-only checks; no claim of live n8n execution.
- Four nodes exist: webhook, validate, mock provider, respond.
- Three edges form a connected linear path.
- Workflow active=false.
- No credentials or remote API destinations.
- Valid synthetic support payload should produce 200/helpdesk.
- Invalid intent should produce 400 with errors.
Actual n8n schema acceptance, Code node execution, and response behavior remain unverified until local import/tests.
