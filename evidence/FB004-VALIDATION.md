# FB-004 evidence receipt

Recorded 2026-10-23, America/New_York. Claims below have separate provenance.

| Claim | Source / method | Result | Limit / next gate |
|---|---|---|---|
| FB-003 four nodes green; HTTP 200 and 106-byte body | Owner report in current request; read_thread recovered historical terminal output, conversation 6ad96997-e5d4-83ea-b5bb-ac51a50b324c, message 9a3ce741-7a91-42f8-bb96-5afdef546613 | USER-OBSERVED success | Agent did not rerun this result or inspect screenshot pixels; historical imported workflow identity not established |
| Repository state | GitHub get_repo, search_prs and fresh clone | private; default main; PRs #2/#3 merged; base 31c6dc5 | Branch publication recorded by PR; no production publication |
| Exported workflow behavior and graph | Node v22.19.0: node --test prototypes/test-fb004.cjs | AGENT-RUN 29/29 pass | Executes actual Code-node JS in VM, not n8n response engine or HTTP |
| HTTP probe contract and transport constraints | Python 3.13.7: python -m unittest discover -s prototypes -p test_fb004_http_probe.py -v | AGENT-RUN 3/3 pass | Mocked transport tests; not live HTTP acceptance |
| n8n health endpoint | GET http://127.0.0.1:5678/healthz | AGENT-RUN HTTP 200 | Does not identify imported workflow/version or prove isolation |
| invalid-intent HTTP probe | POST fixed local test endpoint | AGENT-RUN FAIL: expected HTTP 400, got 404 | Test route unavailable; re-arm and confirm updated inactive workflow. Initial attempt reported generic ValueError; diagnostic was improved and one manual rerun identified 404 |
| invalid-email / invalid-request-id live HTTP | Not run after route failure | PENDING | Must run separately after re-arming; no passing HTTP 400 claim |
| Current listener/container isolation | Get-NetTCPConnection returned no listener record; docker ps denied local config/pipe access | INCONCLUSIVE | Health HTTP proves reachability, not bind/firewall safety; no remediation attempted |

Historical success body, preserved verbatim:

```json
{"ok":true,"request_id":"final_001","provider":"local-mock","result":{"route":"helpdesk","accepted":true}}
```

User reported length 106. The preceding historical 200/empty-body attempt was not a pass; later supplied output superseded it for that user-observed happy path only.

Security review and reproduction: ../operations/FB-004-WORK-PACKET.md. Costs: zero incremental paid-service calls or purchases; no outreach; labor not timed. Evidence state: offline regression tested, historical user-observed n8n happy path, live negative acceptance pending. Original revenue objective not achieved.
