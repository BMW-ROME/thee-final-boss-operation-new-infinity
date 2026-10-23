# Independent engine review

Reviewer: local audit agent, separate from the engine producer. Date: 2026-10-22.

Scope: `src/final_boss.py`, `schemas/task.v1.json`, `schemas/event.v1.json`, `tests/test_engine.py`, `docs/ENGINE.md`. Reviewed source, schema contract and evidence claims; ran producer tests and added bounded adversarial artifact tests. No engine code changed during this review.

## Executed baseline

`python -m unittest discover -s tests -v`: original 8 tests passed. These exercise concurrent claims, process interruption after committed checkpoint, stale-token fencing, bounded retries/crash recovery, idempotency conflicts, schema rejection, transaction rollback and the happy-path demo.

`python -m unittest discover -s tests -p test_review_regressions.py -v`: two test methods produced three failing assertions against the reviewed version. Temporary synthetic files only; no real user files were removed or modified.

## Actionable findings at review time

1. **P2 â€” Successful demo rerun does not verify its surviving output.** Run the demo, delete or alter its generated `.demo.txt`, then rerun. The program exits zero and returns the same `succeeded` / `passed` task because a terminal task is not claimed, and artifact reading occurs only inside the newly claimed branch. This is valid historical ledger state, but insufficient evidence of current deliverable integrity. The documentation's read-back description and repeatable demo could be read as current verification. Preserve the historical receipt; re-read and check its SHA-256 on rerun, return nonzero with an explicit integrity failure when absent/changed, and do not silently regenerate.

2. **P2 â€” Initial demo overwrites output with unknown provenance.** If the database-derived `.demo.txt` exists before the first run, unconditional `write_bytes` replaces it. This violates the handoff's preservation requirement. Use exclusive creation or explicitly accept only an already matching synthetic output during recovery; refuse different existing content. The new test verifies preservation and nonzero rejection.

Both issues are covered in `tests/test_review_regressions.py`. They must be repaired and rerun before claiming the independent artifact-integrity gate passes. The root agent owns remediation and subsequent verification; append its result rather than silently erasing these observations.

## Boundaries confirmed

The engine imports no HTTP client, inference SDK or shell executor. Its CLI operates on SQLite, user-selected input JSON and a synthetic adjacent file. Test subprocesses invoke the local Python engine and a synthetic interruption fixture only. No live customer contact, payment, paid inference, n8n import or network request was executed by these engine tests.

The API accepts artifact receipts as declarations and documentation explicitly says they are not independent file verification. That limitation is correctly stated. SQLite transactions and claim fencing are meaningful local protections, not distributed global deduplication. The docs correctly disable customer/spending actions and warn that copied ledgers cannot coordinate independent environments. These checks do not prove production recovery, disk corruption survival, arbitrary tool safety, model performance or revenue.

## Remediation by root

Both P2 findings repaired using exclusive creation and current-byte verification on rerun. Full suite rerun: 10 tests passed in 2.082 seconds on Python 3.13.7. Historical ledger receipt is preserved on failed re-verification. Crash between file creation and state completion intentionally requires manual artifact reconciliation; no blind overwrite.
