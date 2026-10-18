---
name: audit-log
description: Appends each decision to the run's decision history (JSONL). Write-once per decision ID, so a restarted step never duplicates history. Earlier decisions are never overwritten.
---

# audit-log

**Runs:** always, last. **Calls a model:** no.

## Input
- `state.decision`, `state.validation_issues`, `state.trace`, `state.snapshot`.

## Output
- One line in `runs/<run_id>/decisions.jsonl`.

## Each entry contains
Decision ID, run and case IDs, trigger (event), decision time (virtual clock), status, action, cause, confidence, evidence IDs, question key and text, reasons, blocked actions, next owner, reassess time, model/prompt/policy versions, replay source, the model's explanation (audit only), validation issues and the skills that ran.

## Rules
- Write-once: if the decision ID is already in the file, skip.
- A new event creates a new decision. Never edit an earlier line.
- This is the business decision history, separate from any workflow checkpoint.
- Operations accepting a recommendation is a review event. It is not proof of delivery.
