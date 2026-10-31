# Bounded live checks — 2026-10-31

All inputs used synthetic fixture `SYN-01`; requested model was `gpt-6.1-terra`; no SDK retries were enabled. Aggregate external requests: **12/12**. No request was repeated automatically.

## Attempt 1 — assessment plus verifier (2 requests)

The initial VoltAgent assessment ran; the targeted verifier returned a source span that did not match its cited source. The harness failed closed with `Semantic verifier returned unsupported source span`. No recommendation was produced. Usage/latency were not captured in that historical error path. The process needed SIGINT (exit 130) after the result because of an open telemetry handle.

## Attempt 2 — initial plus reply assessment (2 requests)

The initial assessment succeeded in 11,044 ms: 2,506 input tokens, 597 output tokens (314 reasoning tokens), 3,103 total. The reply assessment produced incomplete JSON (`Unexpected end of JSON input`) and was persisted as HUMAN_REVIEW. No retry was issued. Historical failure-call usage/latency were unavailable. Process needed SIGINT (exit 130).

## Attempt 3 — initial, buyer reply and verifier (2 requests)

- Initial assessment: 9,627 ms; 2,506 input tokens, 547 output tokens (286 reasoning tokens), 3,053 total; finish reason `stop`.
- Reply assessment: 12,328 ms; 2,798 input tokens, 958 output tokens (516 reasoning tokens), 3,756 total; finish reason `stop`.
- Targeted semantic verifier: 11,449 ms; 810 input tokens, 853 output tokens (614 reasoning tokens), 1,663 total; finish reason `stop`.
- The verifier returned schema-valid checks with exact spans. It supported intent, availability, and no refusal, but marked address support `UNSUPPORTED`; the policy override was `ESCALATE_REVIEW`. The run completed with review, not a retry recommendation. One buyer question was asked; the reply did not trigger an unnecessary second question.
- The process again retained a telemetry handle and was interrupted with SIGINT (exit 130).

The third attempt shows actual VoltAgent + OpenAI assessment and verifier execution, but live readiness remains **not passed**: earlier runs had verifier span and JSON parse failures, and this successful verifier was conservative about address evidence. Usage/latency on current failure paths are now stored when the SDK provides them. The app never executed logistics actions. No further calls were made.

## Attempt 4 — shutdown probe (1 request)

A synthetic initial assessment completed in 10,888 ms (2,506 input, 702 output, 3,208 total tokens) and entered WAITING_FOR_BUYER. The probe called `forceFlush()`, `shutdown()`, and closed the harness database, but the process did not exit naturally. It was interrupted with SIGINT (exit 130).

## Attempt 5 — active-handle probe (1 request)

A second initial assessment completed in 11,144 ms (2,506 input, 736 output, 3,242 total tokens). After telemetry shutdown and DB close, the process still had two `Socket` handles and one `TLSSocket`. It was interrupted with SIGINT (exit 130).

The VoltAgent observability flush/shutdown API was called on application shutdown, but it did not close the remaining network handle(s) in the short-lived live probe. Do not claim natural process exit after model calls based on these attempts. Aggregate count at that point was 8/12.

## Attempt 6 — global dispatcher shutdown probe (1 request)

An initial assessment completed in 9,742 ms (3,183 total tokens). Closing Undici's global dispatcher did not make the process exit naturally within 40 seconds. It was interrupted with SIGINT (exit 130). This attempt showed that closing the global dispatcher alone did not resolve shutdown.

## Attempt 7 — dedicated dispatcher probe (1 request)

After switching the OpenAI provider to a dedicated Undici dispatcher, an initial assessment completed in 8,914 ms (3,102 total tokens). The process did not exit naturally within 30 seconds and was interrupted with SIGINT (exit 130).

## Attempt 8 — post-shutdown handle probe (1 request)

An initial assessment completed in 10,721 ms (3,294 total tokens). The dedicated dispatcher removed the OpenAI TLS socket: after telemetry shutdown and DB close, `process._getActiveHandles()` contained only the two stdio sockets. The process still did not exit naturally within 30 seconds and was interrupted with SIGINT (exit 130).

## Attempt 9 — final shared-observability shutdown check (1 request)

After registering the application's observability instance with `AgentRegistry`, a synthetic initial assessment completed in 9,533 ms (3,170 total tokens), finish reason `stop`, and state `WAITING_FOR_BUYER`. The post-shutdown resource snapshot contained stdio pipes and a transient `Immediate`; the process exited naturally with code 0. This used the final allowed request.

The prior interval-leak hypothesis was incorrect. Local instrumentation established the cause: `Agent` does not take an `observability` constructor option. Each agent lazily creates its own instance unless an application-wide instance is registered in `AgentRegistry`; shutdown had been flushing a separate instance. The app now registers and shuts down the shared instance. The regression test streams through VoltAgent using a mock model, shuts down the production observability instance, and verifies that the child exits without `Timeout` resources. The dedicated Undici dispatcher also closes the provider connection.

Aggregate external requests: **12/12**. No further live calls are permitted under this plan's cap. Live model execution and clean process shutdown after an initial assessment are now demonstrated. Live assessment reliability is **not passed**: prior calls failed closed on an unsupported source span and incomplete JSON, and a later semantic verifier conservatively marked address support unsupported, correctly yielding `ESCALATE_REVIEW`. No logistics action was executed. The authoritative BI 30-case evaluation remains unavailable because its JSON data is missing.

## Offline verifier follow-up change (no additional live calls)

After inspecting the recorded SYN-01 run, the verifier was updated to distinguish unresolved buyer-resolvable prerequisites from address/refusal guard checks. Uncertain intent/availability/COD readiness can lead to a bounded follow-up; absent address-change or refusal evidence is represented by `NOT_PRESENT` and does not claim an address is unchanged. Deterministic lifecycle and policy gates remain authoritative. The added path passes offline stub-backed harness tests, but has not been checked against another live model response because the 12-request cap was already exhausted. The historical run and its stored decision were not rewritten.

The assessment timestamp is now passed separately from the original failure timestamp so relative buyer scheduling language is interpreted against the current conversation. Deadline eligibility is rechecked on assessments, replies, manual retries, and no-reply finalization. The stale synthetic fixture deadlines were moved from 2026-10-28 to 2026-11-30 so the demo can run on 2026-10-31; a new run after 2026-11-30 still stops before model assessment. This deterministic deadline behavior is covered by offline tests. The older stored run retains its original 2026-10-28 snapshot.
