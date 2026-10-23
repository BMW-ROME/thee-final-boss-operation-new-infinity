# Local Orchestrator

Status: role specification; this file does not deploy an autonomous agent. Read AGENTS.md and SECURITY.md first.

## Mission

Run bounded local tasks without mandatory cloud inference.

## Inputs

Validated v1 task, local database and approved artifact destination.

## Outputs

Durable state/events and verified local artifacts.

## Available tools

Python CLI, SQLite and optional local Ollama adapter.

## Permissions

Synthetic/offline jobs only in current prototype.

## Forbidden actions

Outbound contact/charges; remote inference substitution; loading multiple large models.

## Evidence standards

Runtime receipts, task ownership, artifact digest and state transitions.

## Success criteria

Duplicate submission and interruption recovery do not duplicate completed work.

## Escalation conditions

Unknown state, insufficient RAM, unreconciled side effect or incompatible schema.

## Recovery procedure

Stop worker; preserve database; inspect events and checkpoint; recover only replay-safe tasks.
