# Order Rescue MVP readiness

Date: 2026-10-31. Status: **core offline flow is implemented and tested; live-provider/demo readiness remains blocked**. No deployment, publish, or push was performed.

## Current architecture

- Active app layout is at repository root (`src/`, `public/`, `fixtures/`, `tests/`). The nested `volt-app/` directory is an older partial copy; do not use it as the runnable app.
- Hono serves the browser UI and workflow API. The harness performs deterministic lifecycle checks, calls a VoltAgent assessment agent using the server-side OpenAI provider, validates schema and source ownership, runs deterministic policy gates, performs targeted semantic verification before retry, and persists in SQLite.
- Requested model defaults to `gpt-6.1-terra`; `OPENAI_MODEL` and `OPENAI_REASONING_EFFORT` configure it. Assessment and verification calls have `MODEL_TIMEOUT_MS` abort limits and zero SDK retries.
- `demo-multiturn-v1` supports a maximum of two total buyer questions and up to three assessments. It stores an immutable snapshot/hash and assessment history for each assessment, chronological question/reply interactions, final assessment ID and turn, exact final assessment/policy selection, event idempotency, and additive SQLite migrations with a schema version.
- UI shows current turn, chronological interactions, expandable assessment snapshots, provider/model/usage/latency details, final selection, current result, draft SSE separately, and recovers a run on refresh. The production UI remains simulated and recommendation-only.
- Data and policy are synthetic/illustrative. The authoritative BI v2.2 JSON schema, seed data, and test cases are absent. No BI acceptance or real operational readiness is claimed.

## Changed files

- Runtime/configuration: `src/agent.ts`, `src/agent-config.ts`, `src/agent-prompt.ts`, `src/domain.ts`, `src/harness.ts`, `src/server.ts`, `package.json`, `package-lock.json`, `.nvmrc`, `.env.example`.
- UI/browser: `public/index.html`, `playwright.config.ts`, `e2e/ui.spec.ts`, `e2e/test-server.ts`, `scripts/copy-assets.mjs`.
- Tests: `tests/agent-config.test.ts`, `tests/agent-prompt.test.ts`, `tests/agent-lifecycle.test.ts`, `tests/agent-lifecycle-worker.ts`, `tests/harness.test.ts`, `tests/recovery.test.ts`, `tests/recovery-worker.ts`.
- Operator docs/reports: `AGENTS.md`, `README.md`, `reports/implementation-status.md`, `reports/mvp-readiness.md`, `reports/live-check-2026-10-31.md`, and the implementation design/plan documents under `docs/`.

## Changes in this execution

- Removed supporting-text laundering: the exact model quote reaches validation unchanged; unsupported quotes fail closed.
- Added two-round assessment flow, conversation context, early stop, question-budget escalation, no-reply latest-result selection, durable processing states, interruption recovery, stale-state guards, explicit model/verifier timeouts, and semantic verification before retry.
- Added Node 22.14.0 pin and engines constraint; added environment fields, `/healthz`, configurable host/port, and deployment notes.
- Added real-browser → Hono → harness → temporary SQLite two-round/refresh coverage while retaining mocked UI coverage.
- Assessment prompt version is `demo-multiturn-assessment-v1`; multi-turn policy mode is `demo-multiturn-v1`; public assessment still has the six BI keys. The new mode is an explicit extension, not untouched BI v2.2 behavior.

## Runtime and commands

Runtime used for successful offline checks: Node 22.14.0, npm 10.9.2. `npm ci`: PASS on Node 22.14.0 (433 packages installed; npm reported 24 dependency advisories). `better-sqlite3` was rebuilt for this ABI; the prior Node 25 ABI mismatch no longer blocks tests.

- `npm run typecheck`: PASS.
- `npm test`: PASS, 31 tests, including process-restart recovery and a child-process VoltAgent stream/shutdown regression, explicit retry, refusal review, two-round cap, early stop, no-reply after first reply, verifier clarification and neutral NOT_PRESENT handling, expiry at current assessment time, stale failure guard, and unsupported source quote rejection.
- `npm run build`: PASS.
- `npm run test:e2e`: PASS, 3 Playwright tests: mocked UI coverage, real Hono/harness/SQLite two-round flow with refresh, and explicit retry, using deterministic assessor/verifier stubs.
- Compiled server smoke: PASS; `node dist/src/server.js` on `HOST=127.0.0.1 PORT=4402 DB_PATH=/tmp/order-rescue-start-smoke.sqlite`; `/healthz` returned `{"status":"ok","data_mode":"synthetic-demo"}`, `/api/cases` returned four labeled cases, and direct SIGINT shutdown exited 0. `npm start` also served health/cases; npm itself returned 130 on terminal SIGINT.

## Bounded live observation

See [live-check-2026-10-31.md](live-check-2026-10-31.md). Nine bounded synthetic attempts used 12/12 requests total. One completed initial+reply+verifier in 9.6s / 12.3s / 11.4s and correctly ended in `ESCALATE_REVIEW` because address support was uncertain. Other attempts failed closed on an unsupported source span and incomplete JSON. The final initial assessment completed in 9.5s / 3,170 total tokens; after the shared-observability fix, the process exited naturally with code 0. Live initial execution and clean shutdown are demonstrated; live semantic reliability remains **not passed** because of the earlier failed/overly conservative outputs. The cause was that `Agent` ignores an `observability` constructor option and lazily creates per-agent instances unless a global `AgentRegistry` observability is set. The app now registers one shared instance and shuts it down. SDK usage/latency and finish reasons are retained for parse/validation failures when available.

## BI baseline vs demo extension

| Area | BI v2.2 baseline | `demo-multiturn-v1` extension | Current implementation |
|---|---|---|---|
| Buyer questions | One question and one reply | Up to two total questions, three maximum assessments | Implemented and tested offline |
| Final source | Enum 1 or 2 | Separate final assessment ID and turn index; enum remains 1/2 | Implemented; source stays 1/2 |
| No reply | Select initial result before reply | Select most recent assessed result after a reply | Implemented; no assessor call |
| Semantic assurance | No original 30-case result without datasets | Targeted verifier before retry | Implemented; stub denial tested, live verifier failed closed |
| Original evaluation | 30 authoritative cases | Not replaced by demo tests | Blocked; JSON inputs absent |

## Remaining blockers and limits

- The semantic verifier now distinguishes unresolved buyer-resolvable retry prerequisites from address/refusal guard checks. Uncertain intent/availability/COD readiness can trigger one bounded, targeted follow-up question, while neutral absence of address-change/refusal evidence does not require a positive quote. This behavior passed offline stub-backed harness tests only; the exhausted live request quota means the change has not been live-verified.
- Lifecycle deadline checks now use current assessment time and run on new assessments, buyer replies, manual retries, and no-reply finalization. The synthetic SYN-01 deadline is 2026-10-28, so a fresh run on 2026-10-31 is blocked before model calls; the older screenshot's saved decision remains historical and unchanged.

- Live verifier conservatism and output reliability need review: an earlier verifier supplied an unsupported span, a reply response parsed as incomplete JSON, and a later verifier conservatively rejected address support. Continue to fail closed; validate cases with business reviewers.
- Shared VoltAgent observability shutdown and dedicated OpenAI transport cleanup are wired and passed a live natural-exit check. The bounded live budget is exhausted. Earlier live model outputs included unsupported evidence and incomplete JSON; continue to fail closed and have business reviewers assess semantic quality.
- Manual retry is available for HUMAN_REVIEW with a distinct attempt event and is covered by unit/browser tests. New demo runs preserve prior runs. A separate reset action is not provided.
- Browser integration uses deterministic boundary stubs. Live-model browser behavior was not tested.
- Public demo access protection/spending controls are not implemented. Do not expose the API publicly without them.
- No semantic verifier can guarantee ground truth; model interpretation can remain wrong. Current verifier is same-model, and source-span matching is only a necessary grounding check.
- No real customer or shipment data is supported. Use synthetic fixtures only.

## Five-minute rehearsal script

1. Use Node 22.14.0. Copy `.env.example` to `.env`, configure a server-side key only if doing a live run, then `npm ci`, `npm run build`, `npm start` (or `npm run dev` for development).
2. Open `http://127.0.0.1:3000` and choose a synthetic case. Point out that the data and policy are simulated.
3. Start assessment. Explain that streamed text is draft only; validated assessment and policy appear after persistence.
4. If asked, provide a synthetic intent-only reply. Show the second bounded question and current `1/2` or `2/2` indicator. Refresh and confirm the run resumes with its chat/history.
5. Provide another synthetic response or choose no-reply. Show the selected final turn, policy result, and next owner. State that live semantic reliability, public access controls, and the absent BI suite remain limitations.
