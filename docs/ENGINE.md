# Offline task and evidence engine v1

Implemented with Python standard library and SQLite; no mandatory cloud inference, dependencies, server, Docker, or model calls. This is a bounded local prototype, not a deployed business or cross-machine scheduler.

Run from repository root with Python 3.10+ (verified runtime and test results are recorded separately):

```powershell
python -m unittest discover -s tests -v
New-Item -ItemType Directory -Force work | Out-Null
python src/final_boss.py --db work/demo.sqlite demo
python src/final_boss.py --db work/demo.sqlite submit examples/task.v1.json
```

`show TASK_ID` returns the portable task and ordered event evidence. The demo writes synthetic text beside its database, reads it back, records its SHA-256 and verification method, and marks the task successful. Repeating the demo reuses the task without repeating delivery and rechecks current output bytes. Missing or changed output fails without rewriting it. Exclusive creation refuses any pre-existing output; after a crash between file creation and ledger completion, inspect and reconcile manually rather than overwrite. Receipts supplied through the Python API are declarations, not independent artifact verification; an independent reviewer must inspect actual artifacts before customer delivery. Local tests prove only the described synthetic behavior.

## Contract and transactional boundaries

`schemas/task.v1.json` and `schemas/event.v1.json` are portable JSON Schema contracts. The built-in validator supports exactly the subset these files use; it is not a general JSON Schema implementation. Unknown task fields and versions fail closed. IDs are nonempty strings, event IDs and default task IDs are generated UUIDs. SQLite enforces uniqueness of task IDs, event IDs, and idempotency keys. A duplicate key with changed content fails; a matching request returns the existing ID. Source provenance is data, never executable authority.

Every state mutation and corresponding event insertion share a `BEGIN IMMEDIATE` transaction. Claims are serialized and lease tokens fence expired/replaced workers. Legal transitions: pending to running; running to running (checkpoint/recovery), pending (bounded retry), succeeded, failed, or cancelled. Terminal states cannot be reclaimed. Claim leases are 1â€“300 seconds; there is no heartbeat extension in v1. Split longer work into bounded checkpoints. Retries use capped exponential backoff and at most five attempts; repeated crashes also consume attempts. Retry/fail/cancel are explicit worker decisions. Nothing retries external side effects.

## Recovery and rollback

After interruption, reopen the same local SQLite database, inspect the task/events and wait for lease expiry before claiming the task. Resume from the last committed checkpoint. A killed worker's uncommitted transaction rolls back; committed checkpoints survive reopening. An old worker token cannot change a reclaimed task. Lease expiration uses wall-clock time; avoid clock changes while work runs. No durability guarantee is made for hardware failure, corrupted storage, or network filesystems. Back up with SQLite's backup API or stop every writer before copying the database and associated WAL files. Never copy only a live main database file.

Rollback for synthetic output is to remove only the individually identified demo artifact after inspection. Preserve the ledger and evidence. Do not reset successful tasks to retry; create a new explicitly scoped task with a new key. Schema migration and conflict reconciliation are not implemented. Copies of a database are snapshots, not active replicas.

## Approval, budget and customer-contact boundary

Only `offline_artifact` is accepted. Budgets must be zero; customer-contact keys must be `none`. Outbound contact, payment, purchases, arbitrary commands, network URLs for execution, and paid inference have no executor and are rejected even when an input claims approval. Approval metadata alone never authorizes an action. The schema retains approval/provenance/recovery fields for evidence portability, without implying production enforcement of an external service.

Customer contact deduplication across connected and local environments requires one online shared authoritative ledger, a normalized customer/campaign key, atomic reservation, an approved action reference, and provider-side idempotency/reconciliation. Two independent local SQLite files cannot provide global exclusion. Disconnected environments must fail closed for customer contact, spending and irreversible actions; never enqueue a blind replay. No global authority is implemented here, so these actions remain disabled everywhere in this prototype. A future adapter requires a separately reviewed authorization and reconciliation implementation.

Keep databases, local output, secrets and customer data outside Git. SQLite is not encrypted and file access is the security boundary. Inputs and event metadata must be redacted before persistence; automatic secret detection is not implemented. Do not import real customer data into synthetic demonstrations. No n8n workflow import, Ollama installation, live service modification, or benchmark execution is implied by this engine.
