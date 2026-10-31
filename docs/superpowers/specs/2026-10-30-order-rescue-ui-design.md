# Order Rescue UI and streaming design

## Goal

Replace the raw JSON page with a simpler, polished workbench inspired by the supplied dark dashboard and add live progress for agent output.

## Layout

Use a dark navy canvas with restrained teal/blue accents. On desktop, show case selection and key input facts in a narrow left panel, the workflow and main assessment in a wide center panel, and buyer response/final decision/history in a right panel. On mobile, stack those panels. Show three human-readable stages: choose case, agent assessment, buyer response (when applicable). Keep raw snapshots and event history behind disclosure controls.

## Agent visibility

Use VoltAgent's `Agent.streamText` through the existing OpenAI provider. The backend streams progress and generated text deltas to the browser with server-sent events. The browser labels partial text as a draft and only renders an authoritative assessment/policy after the full response has parsed, passed Zod/provenance validation, and passed the deterministic policy gate. Display a concise explanation grounded in the validated evidence and policy checks. Do not expose hidden internal chain-of-thought.

## Failure handling

Precheck outcomes may complete without model tokens. Provider, parse, schema, or provenance failures close the stream with an error event and preserve the existing human-review persistence. Buyer reply assessment follows the same stream path. Manual no-reply remains model-free.

## Verification

Test token forwarding and validation before finalization, keep existing harness tests, and run Playwright coverage for initial run, streamed draft, final result, reply/no-reply controls, and safe rendering.
