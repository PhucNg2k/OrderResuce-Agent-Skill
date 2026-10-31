# Order Rescue UI and Streaming Implementation Plan

> **For agentic workers:** Execute inline. Steps use checkboxes for progress.

**Goal:** Replace the raw JSON page with a compact workbench and stream the agent's draft output while preserving validated decision semantics.

**Architecture:** `src/agent.ts` uses VoltAgent `streamText` and emits text deltas through an optional callback. The harness accepts that callback during initial and reply assessment. Hono exposes SSE endpoints that send progress, deltas, final persisted run, or an error. The browser incrementally displays a clearly labeled draft, then renders validated assessment and policy results.

**Tech Stack:** TypeScript, VoltAgent, Hono SSE, plain HTML/CSS/JS, Node test runner, Playwright.

## Global Constraints

- Keep model execution inside `Agent.streamText`; no direct provider call.
- Partial output is a draft only. Final display waits for full parse, schema/provenance validation, deterministic policy, and persistence.
- Never render hidden chain-of-thought; show only validated evidence, concise explanation, and policy reasons.
- Keep no-reply model-free and keep human-review behavior on failures.
- Escape all streamed and model-authored content before HTML rendering.

## Files

- Modify `src/agent.ts`: stream output tokens and return the validated assessment metadata.
- Modify `src/harness.ts`: optional stream callbacks for initial and reply flows; preserve existing APIs/tests.
- Modify `src/server.ts`: SSE initial/reply endpoints and existing JSON routes.
- Modify `public/index.html`: responsive workbench and SSE client.
- Modify `tests/harness.test.ts` and `e2e/ui.spec.ts`: stream callback and UI behavior.

## Tasks

### Task 1: Stream token deltas through the assessor and harness

1. Added and ran a test proving assessor token callback receives partial output while the harness returns a validated result; observed the expected initial failure.
2. Changed `Assessor` to accept an optional `(delta: string) => void` callback and passed it through `start` and `reply`.
3. Replaced `agent.generateText` with `agent.streamText`, buffered deltas, forwarded each chunk, parsed after stream completion, and kept Zod/provenance checks.
4. `npm run typecheck` and `npm test` pass.

### Task 2: Expose SSE routes

1. Added Hono SSE routes for initial and reply assessments with `stage`, `token`, `result`, and `error` events; kept the existing JSON routes and model-free no-reply route.
2. Verified event framing through Playwright route interception.

### Task 3: Rebuild the UI

1. Replaced `public/index.html` with a responsive dark workbench: case/input card, 3-step progress, assessment/decision, response input, compact history, collapsible raw input.
2. Added an SSE client that writes token deltas as escaped text in a draft panel and renders final results only from the persisted result event.
3. Preserved manual no-reply, resume, case switching, and reply flow.
4. Extended Playwright for SSE initial/reply flow, final state, explanation, and safe rendering; E2E passes.

### Task 4: Verify and review

1. `npm run typecheck`, `npm test` (7 tests), `npm run build`, and `npm run test:e2e` pass.
2. Ran `git diff --check` and visually inspected the running UI at `http://localhost:3000`.
3. Confirmed partial tokens are written only to the draft panel; policy/final output uses the persisted result. No environment values are included in diffs.
