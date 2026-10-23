# Two environments, one contract

Environment A uses connected research, GitHub and approved service tools. Environment B runs the same versioned task contract through local Python and SQLite, with optional bounded Ollama inference and a manually imported n8n template. Core deterministic execution needs no cloud inference or model. Neither environment can operate a real online business without customers/network/payment access.

## Minimal boundary

Inputs → validated task → transactional state/events → deterministic artifact → verification → local completion.

Commercial discovery and offer preparation are independent of infrastructure completion. A customer response never waits for a model benchmark. The research packet and manual operator are the first sales workflow; no autonomous sales agent is deployed.

SQLite is sufficient for a single-machine prototype and concurrent local processes. Do not place its database in a synchronizing cloud folder or share it across disconnected machines as if it were a distributed lock. Use its backup API for consistent snapshots, then copy closed/verified exports. Inspect exact implemented guarantees in ENGINE.md.

## Preventing duplicate irreversible actions

Current runtime deliberately implements NO customer contact, payments or external mutations. Approval fields are provenance, not a credential or proof of authority. A future external-action executor requires one authoritative connected ledger, atomic reservation, stable operation/customer identity, authenticated approvals, provider idempotency where supported, and reconciliation of uncertain outcomes. A disconnected copy must refuse such actions. Never promise exactly-once delivery across two independent stores.

For later failover: freeze old executor, reconcile provider receipts, transfer authority with an explicit epoch, verify task/event history and only then enable the new executor. Unknown outcomes go to manual review, never blind retry. Database uniqueness alone cannot prevent a remote service acting before a local crash.

## Adapter selection

Direct Python functions and JSON are default. n8n is optional scheduling/orchestration after the manual path is valuable. MCP is optional context/tool interoperability, not a business requirement. No new database server, hosted AI, model download or public listener is required for this prototype.

## Rollback

Preserve Git baseline and runtime store separately. Revert code through Git without deleting customer artifacts or databases. Stop new work before restoring a backup. Reconcile all events after backup time; restore is not permission to replay external effects. Local audit does not restart or modify existing services.

Sources (accessed 2026-10-22): https://docs.python.org/3/library/sqlite3.html ; https://www.sqlite.org/lockingv3.html ; https://modelcontextprotocol.io/docs/learn/architecture . Python runtime version and SQLite module availability must be checked locally; the default online Python docs may describe a newer release.
