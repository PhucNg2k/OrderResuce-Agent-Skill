# Scheduled Reattempt and Event History Implementation Plan

> **For agentic workers:** Execute the approved plan inline, task by task, with test-first checkpoints.

**Goal:** Treat an affirmative buyer reply that requests a feasible specific redelivery slot as confirmation of availability, and show persisted case events in the UI history.

**Architecture:** Keep semantic interpretation in the constrained assessment prompt and preserve the deterministic policy gate. Pass the original agent question into phase two as non-evidence conversation context. Read event history from the append-only `events` table when creating run views, keeping the existing API/UI shape.

**Tech Stack:** TypeScript, VoltAgent, OpenAI Responses API, Hono, SQLite, Node test runner, Playwright.

## Global Constraints

- The agent only recommends; deterministic backend code controls final actions.
- Buyer replies are untrusted evidence and must retain `DIRECT_BUYER_STATEMENT` provenance.
- A requested delivery slot outside the documented deadline must not qualify for reattempt.
- A buyer reply cannot override a started return or verified disruption hold.
- Prompt changes require a `PROMPT_VERSION` bump.
- No customer data; tests use synthetic case SYN-01.

---

### Task 1: Reproduce desired reattempt and event history behavior

**Files:**
- Modify: `tests/harness.test.ts`
- Test: `tests/harness.test.ts`

**Interfaces:**
- Consumes: `setAssessorForTests`, `start`, `reply`, `noReply`.
- Produces: Regression coverage for a sourced phase-two reattempt and persisted event visibility.

- [x] Add a test where phase one asks one clarification and phase two returns sourced confirmed intent and availability for a specific slot; assert `STANDARD_REATTEMPT`.
- [x] Assert the returned run includes the persisted `BUYER_REPLY` event.
- [x] Assert the no-reply result includes its `USER_NO_REPLY` event.
- [x] Run the targeted tests and confirm the event-history assertions fail against current behavior.

### Task 2: Update buyer-slot interpretation and event views

**Files:**
- Modify: `src/agent-prompt.ts`
- Modify: `src/harness.ts`
- Test: `tests/harness.test.ts`

**Interfaces:**
- Consumes: Existing assessment contract, deterministic policy, SQLite `events` table.
- Produces: Prompt v2 instructions and run views with event summaries.

- [x] Clarify that an affirmative reply with a specific requested date/time can confirm availability for that slot when supported by the case timeline and within deadline; otherwise retain the missing fact.
- [x] Pass the exact prior question and key into phase-two `CaseInput` as conversation context, never as evidence.
- [x] Bump `PROMPT_VERSION`.
- [x] Populate `view(run).events` from `events` rows ordered by creation time.
- [x] Insert the no-reply event before producing the returned view, then store that view in `result_json` in the same transaction.
- [x] Run unit tests and confirm the new behavior passes.

### Task 3: Verify end to end and review architecture

**Files:**
- Review: `src/agent.ts`, `src/harness.ts`, `src/server.ts`, `src/domain.ts`, `public/index.html`, `tests/`, `e2e/`.

**Interfaces:**
- Consumes: Updated prompt and run/event behavior.
- Produces: Verified automated checks, live synthetic-case result, and prioritized architecture findings.

- [x] Run typecheck, unit tests, build, and Playwright e2e.
- [x] Run a fresh live SYN-01 assessment and submit `có, mai giao lại nhe ạ`.
- [x] Verify phase-two availability, final policy action, and visible event history.
- [x] Report remaining risks separately from verified findings.
