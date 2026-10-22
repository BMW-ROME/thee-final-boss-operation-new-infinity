# Practical integration routes

Researched 2026-10-22. These are implementation recipes and acceptance gates, not installation claims.

| Route | Minimal implementation | Costs / limits | Verification before use |
|---|---|---|---|
| Python local | Standard library reads authorized JSON/CSV, validates, writes Markdown/HTML and hashes | No incremental API charge; labor and machine cost remain | Deterministic sample, malformed input, reviewed output, no network |
| Local model API | Python HTTP request to an existing Ollama localhost /api/chat endpoint with a downloaded model | Local compute and model license; cloud models have separate auth/cost | Check runtime, model identity, local-only routing, timeout, quality/latency on one sample [S5] |
| Python MCP | Official SDK exposes one narrow read-only function over stdio; add authenticated HTTP only if needed | SDK does not supply inference or hosting | Pin package; validate schema; exercise tool list/call; reject forbidden paths [S3,S4] |
| n8n direct API workflow | Manual trigger -> validation -> HTTP Request -> transform -> review artifact | Community self-hosting is distinct from Cloud subscription; APIs can still bill | Inspect existing instance/version, synthetic run, bounded retries, credential redaction [S1,S2] |
| n8n MCP | MCP Server Trigger -> explicitly attached workflow tools | Same hosting/provider costs; broader tool exposure adds risk | Auth required; verify client transport; test URL before production; inspect execution [S6] |
| Hugging Face Space | Small Gradio function exposed as API/MCP for a demo | Basic CPU options exist; free hosting is not unlimited GPU or an SLA | Confirm current quota, visibility, model license, cold start, input handling [S7,S8] |
| Connected creative plugin | Chat -> Adobe transformation/export; optional Runway/Higgsfield generation | Installed plugin does not establish credits, subscription inclusion or API entitlement | Read plan/credits; one approved sample; inspect media and usage rights |
| Customer handoff | Export files plus operating notes to approved destination | Storage and support costs must be included | User-approved recipient, preview, checksum and acceptance |

## Selection

Start with Python file processing and existing document/creative tools. Use direct APIs before adding an MCP wrapper when only one fixed operation is needed. Add n8n after the manual delivery has succeeded repeatedly and scheduling or retries justify it. Add shared databases only when file-based evidence is insufficient.

## n8n licensing boundary

The current official help article says Community use can include operator-built client workflows when customers only receive outputs. Letting external customers build/configure workflows, including via API/MCP/agents, or hosting n8n as a service can require commercial licensing. Confirm the exact business design against current terms before selling it. This is a documented distinction, not an account-specific license determination. [S1]

## Failure controls

Unavailable provider -> preserve input and mark blocked; do not silently substitute paid providers.
Timeout -> bounded retry with request identity; check prior side-effect result first.
Malformed output -> reject and retain redacted diagnostic; never mark delivered.
Quota exhausted -> stop; no automatic upgrade.
Quality failure -> manual correction or refund decision by owner; no invented success.

