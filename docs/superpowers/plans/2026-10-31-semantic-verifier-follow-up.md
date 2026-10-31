# Semantic verifier follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Route verifier-uncertain buyer facts to one targeted bounded follow-up when possible, while keeping policy code authoritative and unsupported facts unable to permit retry.

**Architecture:** Extend the verifier contract with a neutral `NOT_PRESENT` result for address/refusal screening. Add a separate VoltAgent question generator, inject it through a test seam, and persist its output separately from the immutable assessment. Integrate the fallback in initial, reply, and manual-retry finalization paths.

**Tech Stack:** TypeScript, VoltAgent `Agent.streamText`, Zod, SQLite, Node test runner.

## Global Constraints

- Use synthetic fixtures only; no OpenAI requests after the aggregate 12/12 cap.
- Never let the verifier or question generator choose a final operation; deterministic harness policy does.
- Never turn `UNSUPPORTED` or `UNCERTAIN` retry prerequisites into permission to retry.
- Ask no more than two buyer questions per case; do not ask for real PII or operational facts.
- Preserve original assessments and verification records; new question generation is separately audited.

---

### Task 1: Verifier uncertainty routes to a bounded follow-up

**Files:**
- Modify: `tests/harness.test.ts`
- Modify: `src/harness.ts`
- Modify: `src/agent.ts`
- Modify: `src/domain.ts` only if shared schema types are needed
- Test: `tests/harness.test.ts`

**Interfaces:**
- Test seam: `setQuestionGeneratorForTests(fn)` injects a generator returning `{ question_key, question_text, metadata? }` or `null`.
- Production generator: receives the phase input and unresolved verifier fact keys, returns one question under the existing `questionKeys` enum and 240-character cap.
- Verifier verdict `NOT_PRESENT` is allowed only for `address` and `refusal` and may have null source/span.

- [x] **Step 1: Write failing harness tests** for: uncertain availability with one question remaining stores a generated question and waits; supported verification permits reattempt; exhausted question budget escalates without generation; generator failure escalates without a fabricated question.
- [x] **Step 2: Run `npm test -- --test-name-pattern='verifier uncertainty|verifier-supported|question generation'`** and confirm the new behavior assertions fail because the current harness finalizes immediately.
- [x] **Step 3: Implement the neutral verifier verdict and targeted VoltAgent question generator** with strict schema, no PII, approved topic keys, and timeout/output bounds.
- [x] **Step 4: Integrate shared fallback finalization** into initial, buyer-reply, and explicit-retry paths; store question/model metadata separately and preserve original assessment/verifier values.
- [x] **Step 5: Rerun focused tests, then typecheck, full unit tests, build, and Playwright tests.** Do not run a live request; the cap is exhausted.
- [x] **Step 6: Update readiness and live-check notes** to identify this as offline-verified only pending new live budget.

### Task 2: Use the assessment timestamp for deadline and relative-date checks

- [x] Compare eligibility against the current assessment/reply/retry timestamp, not the original failure timestamp.
- [x] Pass the assessment timestamp to semantic verification so relative buyer language uses the current conversation date.
- [x] Recheck deadlines when closing a pending no-reply event; an expired deadline yields review.
- [x] Add a regression test proving expired SYN-01 is blocked before model calls and set the browser test clock to a date inside the fixture deadline.

## Self-review

- All required behavior is covered by Task 1 and remains subject to the repository's two-question, three-assessment, and deterministic-policy gates.
- The verifier can block retry, but only the harness decides whether to ask, finish, or escalate.
- No live-provider claim will be made for the new question-generation path.
