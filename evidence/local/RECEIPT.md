# Local evidence receipt â€” FB-002

Observation date: 2026-10-22. Method: selected read-only Windows CIM fields, WSL list, Docker version and running-container metadata, n8n version command, n8n-container Node fetch to host Ollama, Windows listener enumeration, Ollama `/api/version`, `/api/tags`, `/api/ps`, Python benchmark resource gate and unit tests. Evidence is sanitized; no environment values, credentials, workflow records or customer data were captured.

Initial restricted-shell CIM/WSL/Docker reads returned access denied. Approved read-only execution then returned the runtime observations documented in `local/README.md`; no error was interpreted as absent software.

| ID | Claim | State | Limit / next gate |
|---|---|---|---|
| FB-L001 | Windows, WSL2, Docker, n8n versions and hardware inspected | smoke-tested read-only | Selected metadata only; no endurance/reboot test |
| FB-L002 | Ollama 0.31.2 localhost metadata reachable | smoke-tested read-only | No inference |
| FB-L003 | n8n container to host.docker.internal Ollama route returned 200 | smoke-tested read-only | Not a workflow run |
| FB-L004 | Local benchmark resource gate executed, zero trials | blocked safely | Insufficient free RAM; raw sanitized result in benchmark-result.json |
| FB-L005 | Benchmark unit checks: 12 passed | tested preparation | Does not prove model quality or failure recovery |
| FB-L006 | Manual inactive n8n template prepared and JSON validated | prepared | No import or workflow execution |
| FB-L007 | Wildcard listeners observed at 11434 and 5678 | observed | External reachability unverified; security review pending |

Paid inference cost: $0; no generation requests were sent. Model portfolio consolidation is deferred until actual benchmark evidence exists. Existing configurations/models/containers remained intact.
