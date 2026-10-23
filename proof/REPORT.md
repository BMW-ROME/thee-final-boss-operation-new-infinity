# Synthetic n8n contract QA demonstration
Observed 2026-10-23 02:52 UTC (October 22 Eastern). n8n 2.41.6, JavaScript runner.
Self-initiated synthetic example; no client work, production system, paid provider or customer data.

## Result
The broken workflow passed 1/8 checks; the corrected workflow passed 8/8.
Checks: valid order, zero quantity, two distinct request IDs, duplicate ID, missing quantity, negative quantity, numeric string, empty ID.
Broken behavior converted zero to one, reused the first request ID, and accepted invalid inputs.
The correction preserves IDs and zero, validates types/ranges, and rejects duplicate IDs within a batch.
This is not durable cross-run idempotency; that is separately tested in the SQLite engine.

## Evidence and reproduction
Inactive exports: n8n-broken.json and n8n-fixed.json. Sanitized actual corrected outputs: result-fixed.json.
Executed CLI import and execute --id against a temporary SQLite database/user folder, separate from existing production PostgreSQL configuration. No production saved workflows changed.
The deprecated execute --file command returned zero with "--id has to be set!" and did not prove execution. Actual runData and all eight JSON outputs were inspected on subsequent --id runs.
Python runner unavailable warning appeared; the JavaScript runner completed the checks.
Temporary database remains for inspection; no automatic cleanup or destructive operation.

## Limits
Eight chosen fixtures, one small Code node: not concurrency/load, voice quality, security certification, external API behavior, or customer acceptance.
No revenue or hiring outcome. Sharing requires owner approval; do not share the private project repository as a portfolio.
