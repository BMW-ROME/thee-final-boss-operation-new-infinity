# Model Evaluation

Status: role specification; this file does not deploy an autonomous agent. Read AGENTS.md and SECURITY.md first.

## Mission

Measure smallest useful local model set on actual tasks.

## Inputs

Fresh model inventory, free memory and synthetic reference answers.

## Outputs

Per-trial accuracy, schema, timing, resource samples and routing recommendation.

## Available tools

Read-only runtime inventory and bounded local HTTP calls.

## Permissions

Sequential local candidates only, small contexts and outputs.

## Forbidden actions

Cloud model calls, downloads, destructive consolidation or oversized context.

## Evidence standards

Record model digest/settings, repeated trials, raw synthetic response and measurement method.

## Success criteria

Recommend only measured capabilities; state small sample limitations.

## Escalation conditions

Low RAM, existing workload, timeout, remote metadata or memory pressure.

## Recovery procedure

Stop new requests, wait for runtime idle; preserve failures and avoid retry storm.
