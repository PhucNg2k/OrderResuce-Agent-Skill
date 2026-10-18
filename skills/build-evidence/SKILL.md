---
name: build-evidence
description: Builds the case snapshot the model is allowed to see - only facts and evidence available at the virtual "now", with presenter-only fields removed.
---

# build-evidence

**Runs:** after Gate 1 passes. **Calls a model:** no.

## Input
- `state.run`: case file, applied events, virtual clock, question state.

## Output
- `state.snapshot`: JSON sent to the model.
- `state.evidence_index`: `{evidence_id: Evidence}` used by `validate-output` and `policy-gate`.

## What goes in the snapshot
- Case facts needed for the decision (status, attempts, deadline, area, payment, address completeness).
- Starting evidence with `observed_at <= now`.
- Evidence derived from applied events, with id `EV-<event_id>`:

| Event type | Derived evidence type | Source |
|---|---|---|
| `BUYER_REPLY` | `BUYER_REPLY` | `buyer` |
| `ADDRESS_CHANGE_REQUEST` | `BUYER_REPLY` | `buyer` |
| `DISRUPTION_RESOLVED` | `DISRUPTION_UPDATE` | `disruption_feed` |
| `NO_REPLY_TIMEOUT` | `CONTACT_LOG` | `contact_system` |

- Question state: how many questions were asked, which key, the reply deadline.

## What never goes in the snapshot
- `title` (it would leak the expected answer).
- Prepared events that have not been applied (the future).
- Expected results and replay outputs.
