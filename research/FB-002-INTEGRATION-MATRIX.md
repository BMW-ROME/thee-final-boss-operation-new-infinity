# FB-002 capability classification

2026-10-22. Categories overlap intentionally: paid/quota restrictions do not prove availability, and local-only does not mean zero operating cost.

| Capability | Classification | Evidence and chosen role | Next gate |
|---|---|---|---|
| GitHub connector + Git | Connected and verified | Fresh private clone, branch/checkpoint; linked connector previously verified and used for PR | Remote commit/PR verification at publication |
| Python/SQLite | Local-only | Standard-library runtime is implementation target; tests report actual coverage | See execution report, no remote mutation adapter |
| Web search | Connected and verified | Current primary-source and buyer research | Recheck buyer availability before contact |
| n8n/Ollama/Docker/WSL | Local-only; live state audited separately | evidence/local and local/ contain fresh results | Low-memory gate may block inference; template is not deployment |
| MCP Python SDK | Research candidate, not installed by this packet | Official SDK is optional interoperability | Pin/review/test only when a buyer delivery needs MCP |
| Existing SQLite templates/contracts | Available and configured in this repository when tests pass | Single-machine offline execution, not distributed coordination | Failover/external-effects remain manual |
| Adobe, Higgsfield, Runway | Installed metadata from baseline; paid/quota-restricted or unverified entitlements | Optional creative delivery; no generation required here | Account credits, price, rights and approved sample |
| Sites | Available tool; deployment not configured for this project | Optional demo; avoided for smallest implementation | Audience, terms and deployment evidence |
| Supabase | Available tool; not configured for this project | Defer; no hosted database required | Only add for measured shared persistence need |
| Hugging Face CPU Spaces | Free option with documented limits; account eligibility unverified | Research option, not used or required | Current quota, license, visibility, sleep behavior |
| AccurateScribe/Yaps | Available tool/skill; runtime not tested here | Defer unless authorized audio is the deliverable | Account/local engine and input authorization |
| Provider APIs | Unavailable or unverified for this packet | No key created, no paid inference | Separate API entitlement, budget and secret destination |
| Outreach/payment plugins | Not configured or exercised | All drafts remain local | Explicit recipient/action authorization and operator eligibility |

Plugin discovery refreshed for GitHub/n8n/Ollama: only GitHub returned installed=true. Search coverage is non-exhaustive, so missing results are not proof of absence. The baseline full tool/skill catalog remains an as-of snapshot; cached files are not integration proof.

## Commercial rights and costs

n8n Community licensing distinguishes operator-built output services from external users configuring workflows/hosted service access; do not sell an unrestricted customer workflow builder under an assumed free license. Check the exact business design and current terms. No software license has been added to this private project; public distribution rights are not implied.

Primary sources: research/SOURCES.md S1–S8 (rechecked n8n help article during this packet); https://docs.python.org/3/library/sqlite3.html ; https://modelcontextprotocol.io/docs/learn/architecture . No mandatory paid cloud dependency was introduced. Electricity, owner time, hardware and existing subscriptions remain costs.
