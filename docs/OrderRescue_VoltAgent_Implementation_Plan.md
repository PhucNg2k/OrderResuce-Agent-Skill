# Order Rescue — Implementation Plan
## VoltAgent + DeepSeek + Case Harness + UI
Updated: 2026-10-29. Planning document; implementation and live tests have not run.

## 1. Baseline and authority
Base repository: https://github.com/PhucNg2k/OrderResuce-Agent-Skill
Reviewed baseline: e52194f4af805c6d41d283c2fb19c3f1aed8c69c.

This revision replaces the earlier plan, especially its timeout and question-template behavior.
Read applicable AGENTS.md files and BOTH actual files in BI ref completely before coding.
The user's requirements and the supplied BI contract govern the new application.
Existing Python behavior is a baseline, not necessarily the new business specification.
Do not modify BI source files or expected answers to make tests pass.
Confirm actual BI filenames, versions, pairing, schemas and policy profiles.
The Business Rules v2.2 document was read during planning; the two new BI ref files were not directly accessible. Verify their contents locally rather than assuming they match.

## 2. Goal and scope
Build a small TypeScript app under volt-app/ alongside the existing Python application.
One VoltAgent, direct DeepSeek API, thin case harness, SQLite, adapted existing HTML/JS UI.
First prove one live BI case end to end, then expand representative cases and the complete BI suite.
Preserve runtime/, skills/, fixtures/ and tests/ as an independently runnable baseline.
No Python RPC bridge, Pi runtime, multi-agent, RAG, Workspace Skills or new React frontend required.
No fork, push, deployment or publishing as part of local implementation.
Use synthetic data; no real messages or logistics actions.

## 3. Architecture
UI -> business API -> Case Harness -> VoltAgent + DeepSeek.
Harness reads/writes SQLite and always runs validation and policy before publishing decisions.
Agent interprets language and proposes. Backend controls eligibility, interaction state and final selection.
Do not expose a direct agent endpoint as a shortcut around the business harness.

Suggested structure:
volt-app/
  package.json, package-lock.json, tsconfig.json, .env.example, AGENTS.md
  src/
    server.ts, config.ts
    agent/      provider.ts, orderRescueAgent.ts, instructions.md, runAssessment.ts
    domain/     schemas.ts, biAdapter.ts, snapshot.ts, sourceRegistry.ts,
                validate.ts, policy.ts, compose.ts
    harness/    caseHarness.ts, eventReducer.ts
    storage/    db.ts, repository.ts, migrations.sql
    api/        routes.ts, views.ts
    telemetry/  events.ts
  public/index.html
  tests/unit/, integration/, live/, ui/
  reports/implementation-status.md

Merge small modules when appropriate; do not build a generic platform.

## 4. Reuse map
| Existing component | New implementation |
|---|---|
| runtime/pipeline.py | Reference for mandatory boundaries; new TS harness owns execution |
| runtime/simulator.py | Reuse fixture/event concepts; replace legacy timeout flow with BI semantics |
| runtime/models.py | Reference only; derive authoritative schemas from actual BI |
| runtime/api.py | Preserve Python baseline; new app uses custom business endpoints |
| runtime/static/index.html | Adapt into volt-app/public/index.html |
| skills/load-case | Port applicable eligibility checks |
| skills/build-evidence | Reuse source filtering; LLM extracts evidence from BI raw records |
| skills/assess-case/prompt.md | Adapt to new BI prompt/schema version |
| skills/assess-case/skill.py | Replace model path with VoltAgent/direct DeepSeek |
| skills/validate-output | Retain provenance checks, do not copy semantic regex/source-count heuristic |
| skills/policy-gate | Port applicable invariants using actual BI policy profile |
| skills/compose-recommendation | Reuse neutral presentation, not mandatory old question templates |
| skills/audit-log | Preserve history principle; SQLite stores state and immutable snapshots |
| fixtures/replay | Keep legacy hand-authored seeds separate from live recordings |
| tests + legacy expected | Baseline tests remain; new BI behavior has separate tests |

Read root instructions and document the user-requested new app in scoped instructions.
Do not silently rewrite baseline policy/prompt to match the new application.

## 5. BI adapter
Read both files fully: model/schema, seed_data, source_ref_index, demo_policy_profile,
scripted replies and expected labels where present.
Keep simulator/evaluator data out of agent input.

Under BI v2.2, construct seven core fields:
case_id, failed_event, attempts_used, return_state, deadline, buyer_history,
operational_context, with runtime_context separate when interactions occur.

Join case -> order -> failed event and verify the event belongs to the same order.
Use authoritative attempts_used, not counts of incomplete event history.
Parse timestamps/timezones; filter by assessment cutoff and interaction availability.
BUYER_CONTEXT at T0 is not the pending question's BUYER_REPLY.
Unknown return state or missing deadline must not default to eligibility.
Buyer history may legitimately be empty. Do not invent attempts, addresses, COD amounts
or operational signals.
Check payment inconsistencies rather than arbitrarily selecting one value.
Do not send future replies, expected outputs, scenario titles revealing answers,
or prior assessments as raw input for the initial assessment.
Respect BI table/field/null semantics; app-owned telemetry may be separate.

## 6. Assessment and semantic extraction
Preserve the exact six-field BI assessment:
evidence, hypothesis, confidence, missing_info, question_key, candidate_action.
Each evidence item contains source_ref, fact, verification.
Do not add final_action or reasoning fields to this public assessment.

LLM extracts evidence and interprets intent, availability, COD readiness,
address requests and uncertainty.
Store internal structured decision facts separately, with source references
and supporting text. One internal model envelope may contain both assessment
and decision_facts; persist assessment with exactly the BI keys.

Backend source registry determines actual provenance.
Model cannot upgrade a courier report into direct buyer confirmation or verified Ops.
Keep contradictory observations and unresolved facts explicit.
Positive intent alone does not establish availability, COD readiness or original cause.
HIGH confidence and missing_info=[] do not replace required policy facts.

Generate question text separately according to actual BI requirements.
Expected reference wording is an example, not an answer/template to copy.
If question generation uses a separate model call, account for it explicitly;
it is not assessment 2. After reply, preserve the question key used where BI requires it.

## 7. Validation without semantic regex
Do not use regex, keyword dictionaries or string contains checks to infer intent,
availability, COD, refusal, address meaning, root cause or confidence.
Do not map case IDs/statuses to expected answers.

Use:
- Zod for structure/enums/keys.
- Code for source existence, ownership, availability, metadata and state constraints.
- LLM for natural-language interpretation into sourced structured facts.
- Deterministic versioned policy for permissions.

Quote-presence checks may use normalization/substrings for provenance only.
They do not prove semantic entailment. Schema pass does not prove interpretation correct.
Do not add an LLM judge to every request by default; evaluate extraction with meaningful cases.
Unknown/conflicted required facts must follow BI clarification/review rules.

Attempt limits, lifecycle restrictions and one-question rules belong in code/config.
They are not forbidden case-answer hardcoding.
Read values from BI policy profiles; action vocabulary membership is not permission.

## 8. Correct BI v2.2 workflow
Verify against actual local files; report differences.

1. Load raw snapshot, validate and precheck.
2. Run assessment 1, validate and evaluate policy.
3. Persist initial_assessment and initial_policy_output before asking.
4. Contact gate -> generate/store simulated question -> WAITING_FOR_BUYER.
5. Receive one matching outcome:

BUYER_REPLY:
- Validate same case, pending question_id, no previous outcome.
- Store interaction, rebuild raw snapshot with actual reply.
- Run a complete assessment 2 and policy.
- Persist after_reply_assessment and after_reply_policy_output.
- final_assessment_source=2; final copies after-reply assessment/policy exactly.

USER_NO_REPLY:
- Manual demo control, not a timed event.
- Do not call the assessment agent again.
- after_reply_assessment and after_reply_policy_output remain null.
- final_assessment_source=1; final copies initial assessment/policy exactly.
- Do not modify confidence, missing_info or candidate to produce a cleaner final.
- A retained CLARIFY candidate does not authorize another question.

6. Finalize once; COMPLETED means recommendation completed, not delivery success.

Final is selection, never a third assessment call.
No automatic timeout, reply deadline, virtual-clock no-reply or background scheduler.
Logistics deadline is separate from buyer interaction.
BI v2.2 question_wait_state has question_id, question_key, question_text, status, asked_at.
Do not turn no reply into refusal or NO_ACTION.
If question_key=null/no-question behavior is not defined, record the ambiguity;
do not force a question or invent a finalization rule.

## 9. Harness and persistence
Suggested functions:
startCase(caseId, mode)
submitBuyerReply(runId, questionId, text, eventId)
markUserNoReply(runId, questionId, eventId)
getRun(runId)
getAssessment(runId, phase)

caseId is business identity; runId scopes a cloned demo execution.
Clone/reset seed per run; do not contaminate new raw input with previous outputs.
Persist BI fields plus immutable snapshots, execution metadata and versions.

Use transactions and affected-row/state guards:
- One outcome per pending question.
- Duplicate event idempotency; same ID/different payload -> conflict.
- Initial and final written once.
- Atomic after-reply/final writes consistent with BI guards.
- No write transaction open while LLM is running.
- Recheck state before publishing stale results.
- Restart restores waiting state; interrupted execution is recorded explicitly.
- Late events do not automatically reopen COMPLETED cases.
State guards protect publication; do not promise exactly-once model billing after crashes.

## 10. DeepSeek integration and compatibility
Read DEEPSEEK_API_KEY only server-side; DEEPSEEK_MODEL configurable.
Never print credentials or expose them to the browser.
Use direct @ai-sdk/deepseek provider instance passed into VoltAgent.

Inspect compatible package versions and pin a lockfile.
Reviewed VoltAgent main manifest was 2.11.0 with ai ^6.0.0;
this is not proof of npm release availability or compatibility with latest AI SDK v7.
Check current model IDs against official docs/live API; do not blindly use old aliases.
Prefer current generateText/streamText with output rather than deprecated generateObject.

Probe:
A. Basic generateText.
B. Structured envelope via Output.object + Zod.
C. If native schema path is unsupported, explicit JSON-mode configuration,
JSON example prompt -> JSON.parse -> Zod.
Never regex-extract JSON, fabricate output or silently switch model/provider.

V0 memory:false and maxSteps=1 with a complete snapshot.
Bound timeout, retries and total requests.
Auth/quota failure blocks live tests; transient errors may have limited retries.
Malformed/empty/truncated output becomes explicit failure/review.
Store available usage/latency/model/output-mode metadata. Unknown usage=null.
Do not display/store internal chain-of-thought.

Separate legacy replay and new recordings.
New replay keys include snapshot hash + prompt/schema/policy/model configuration.
Changed free-text reply must not reuse another reply's recording.
No silent live/replay fallback.

## 11. API and UI
Use one server, custom Hono business endpoints through the harness:
GET /api/cases
POST /api/runs
GET /api/runs/:runId
POST /api/runs/:runId/replies
POST /api/runs/:runId/no-reply
GET /api/runs/:runId/assessments/:phase
GET /api/runs/:runId/execution-events?after=sequence

Adapt existing UI:
- Case catalog and resume run.
- Raw input/sources.
- Initial assessment/policy.
- Generated question, free-text reply, clearly marked scripted controls.
- Manual no-reply.
- After-reply, final and final source.
- Evidence provenance and candidate versus final policy action.
- Historical snapshot selection, never latest evidence on an old assessment.
- Real loading/errors, mode/model, available usage/latency.

Polling is enough; do not simulate tool calls or progress.
Escape raw user/model text. Disable duplicate submissions and preserve draft on errors.
Selecting an existing run must not start a new run.
Questions are simulated messages, not confirmed real sends.

## 12. Phases and gates
| Phase | Work | Gate |
|---|---|---|
| P0 | Read repo/BI, record versions, run Python baseline tests | Actual results and contract map |
| P1 | Pin dependencies, typecheck/build, DeepSeek probes | One real BI snapshot returns valid envelope |
| P2 | Adapter, source registry, policy, SQLite | Offline domain/state tests pass |
| P3 | One full reply flow and manual no-reply flow | Correct BI persistence/final selection |
| P4 | Adapt UI and history/resume | Meaningful browser E2E passes |
| P5 | Representative semantic tests, then supplied BI suite | Report actual mismatches and limitations |
| P6 optional | One useful read-only tool for existing BI data | Actual scoped tool call/result/final works |

Absent credentials/network must mark live gate BLOCKED, not PASSED.
Continue independent offline work without inventing live evidence.
Tools are optional until the vertical slice works; do not expose policy/audit as skippable tools.

## 13. Tests and live-test budget
Offline:
- Wrong schema, invented/unavailable source, provenance upgrade.
- Mismatched event/order, invalid lifecycle/deadline/attempts.
- Duplicate event, mismatched question, outcome race and final write once.
- No reply: after-reply null, exact initial copy, zero second assessment call.
- Reply: full assessment 2, exact final selection.
- Restart waiting state, interrupted runs, immutable history.
- Model errors cannot produce permitted results.

Live semantics:
- Intent only versus receiving arrangement.
- Negation/conditional availability, receiving proxy.
- Explicit COD readiness versus missing COD evidence.
- Landmark clarification versus address change.
- Unverified report versus direct buyer refusal.
- Reply confirming intent without confirming cause.
- Conflicts, prompt injection in raw notes.
- Verified disruption not cleared by positive buyer intent.

Use synthetic data only. Start approximately 8–12 assessment calls with a configurable cap.
Count question generation and technical retries separately.
Rerun relevant failed checks after changes; no unlimited API loops.
Golden labels apply only to their scripted replies.
Compare evidence/reason by meaning and provenance, not exact wording or item count.
Do not use same-model judging as unquestioned ground truth.

## 14. Deliverables and definition of done
- New app startup instructions and .env.example.
- Python baseline preserved.
- One live vertical slice or a clearly documented blocked live gate.
- No semantic regex/case-answer lookup.
- Correct initial/after-reply/final workflow and SQLite persistence.
- Working reply/no-reply UI with immutable history.
- reports/implementation-status.md including:
  actual files/versions/model, BI versions, decisions and ambiguities;
  commands and PASSED/FAILED/BLOCKED/NOT_RUN results;
  actual API call counts and available usage/latency;
  known issues and exact startup/test instructions.
- No claim of real carrier integration, measured business impact or perfect semantic reliability.

## 15. Official technical references
https://voltagent.dev/docs/agents/overview/
https://github.com/VoltAgent/voltagent/blob/main/packages/core/package.json
https://voltagent.dev/docs/getting-started/providers-models/
https://ai-sdk.dev/providers/ai-sdk-providers/deepseek
https://api-docs.deepseek.com/api/create-chat-completion/
https://api-docs.deepseek.com/guides/json_mode/
https://api-docs.deepseek.com/guides/tool_calls/
https://voltagent.dev/docs/agents/hooks/
https://voltagent.dev/docs/api/custom-endpoints/
https://voltagent.dev/docs/agents/memory/overview/

Recheck docs against installed versions during implementation.
