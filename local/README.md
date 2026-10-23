# FB-002 local execution checkpoint

Observed 2026-10-22. No installation, restart, model deletion/download, workflow import, paid call, or global setting change occurred.

## Verified runtime

Windows 11 Home 10.0.26200, AMD Ryzen 7 5825U, 16 logical processors, AMD Radeon graphics (reported AdapterRAM 2 GiB; this is not proof of a dedicated GPU). No NVIDIA adapter appeared in the enumeration. OS reports 14,513,528 KiB usable RAM (~13.84 GiB). Free RAM during inventory was only 794,352 KiB (~0.76 GiB).

Ubuntu and docker-desktop are running WSL2 distributions. Docker server 28.5.1 is running. Existing containers include n8n, Ollama, PostgreSQL and Qdrant; no database/customer/workflow content was inspected. n8n reports 2.41.6. Python 3.13 executable was available and ran the checks. Ollama reports 0.31.2 on Windows localhost. Its `/api/ps` returned no loaded models.

The n8n container reached `http://host.docker.internal:11434/api/version`: HTTP 200 and Ollama 0.31.2. This proves the container-to-host read route, not workflow execution or inference.

Windows listener enumeration reports `::` for ports 11434 and 5678, plus `::1` for 5678. This is a wildcard listener observation; firewall/NAT and external reachability were not tested. Do not call these loopback-isolated or internet-exposed. Review existing host firewall and Docker publish bindings before accepting customer data; no network configuration was changed.

## Models and decision

| Observed tag | Model bytes | Decision |
|---|---:|---|
| qwen2.5-coder:3B | 1929912626 | Conditional small-model benchmark candidate |
| llama3.2:3B | 2019393189 | Conditional small-model benchmark candidate |
| phi3:latest | 2176178913 | Conditional small-model benchmark candidate |
| phi4-mini:latest | 2491876884 | Reserve candidate; avoid redundant runs |
| nomic-embed-text:latest | 274302450 | Embedding role; not tested as a chat model |
| llava:latest | 4733363377 | Excluded from this memory-bounded run |
| gemma4:latest | 9608350736 | Excluded; oversized for current free RAM |
| glm-5.3:cloud | 293 | Remote/cloud tag; never invoked |

No local-model performance claim or smallest effective portfolio can be justified yet. Current free memory prevented inference. No models were unloaded to make room, and the earlier large KV-cache failure was not repeated.

## Executed and prepared

`python -m unittest discover -s local -v`: 12 tests passed (eligibility, cloud exclusion, output grading, context/token limits). `python local/benchmark.py --output evidence/local/benchmark-result.json`: executed the live resource gate and stopped with zero trials. See the JSON for its distinct timestamp and memory snapshot.

The benchmark uses only Python standard library, synthetic extraction, localhost requests, an allowlist, model-size-plus-2-GiB free-memory threshold, 1024 context tokens, 128 output tokens, two CPU threads, temperature zero, sequential two trials per eligible model, and keep_alive zero. It stops on occupied Ollama or resource/error gates. It collects system CPU/free memory samples (shared-machine measurements, not isolated inference resource attribution), wall latency, JSON/schema/exact-value accuracy, model load duration and reliability. An invalid-model 404 followed by a successful trial is the planned recovery test, not a claim of executed recovery. Timeout stops further requests; a timed-out server operation may still run, so inspect `/api/ps` before retrying. Other software may allocate memory between checks; the gate is conservative, not a hard memory reservation.

`n8n-ollama-health.json` is an inactive, manual-trigger health template with no credentials or generation. JSON structure is checked; it has not been imported or executed by n8n. Its HTTP route was separately smoke-tested inside the running n8n container. Import it manually only if useful; no workflow modification is required for the proven route.

## Resume and costs

Resume when normal owner-managed workload completion leaves at least model bytes plus 2 GiB free RAM (about 3.80 GiB for the smallest candidate), and no model is loaded. Run the benchmark command above. Review exact accuracy, repeated success and latency before retaining any model role. Do not infer suitability for factual research from this narrow synthetic test. No cloud is needed for these scripts; opportunity discovery/customer/payment activity still needs internet.

Incremental paid API/services: $0. Existing electricity, hardware wear and owner labor were not measured and are not zero. No cloud quota was consumed by inference. Production gates: inference benchmark, actual n8n workflow execution, interruption recovery, concurrent workload safety, reboot restoration, security binding review and customer-data consent remain pending.
