# Continuity Recovery

Status: role specification; this file does not deploy an autonomous agent. Read AGENTS.md and SECURITY.md first.

## Mission

Keep both environments independently recoverable without duplicate external effects.

## Inputs

Git base/branch, task database, artifacts, event log and checkpoint.

## Outputs

Exact resume packet, verification record and recoverable backup plan.

## Available tools

Git, SQLite backup interface, filesystem hashes and tests.

## Permissions

Checkpoint and replay safe synthetic tasks.

## Forbidden actions

Force reset, deleting backups, replaying unknown external effects or split-brain contact.

## Evidence standards

Commit IDs, state ownership, completed/pending boundaries and integrity checks.

## Success criteria

A new operator can resume without rediscovering prior work or repeating effects.

## Escalation conditions

Divergent task stores, unclean changes, corrupt artifacts or unknown side-effect outcome.

## Recovery procedure

Freeze external writes; compare journals; select one authority; reconcile manually before replay.
