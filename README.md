# Order Rescue VoltAgent Demo

A synthetic delivery-failure workflow demo for operations teams. It recommends a next step and records the decision; it does not perform delivery, messaging, refund, cancellation, or other logistics actions.

All examples are synthetic. The included business rules are illustrative and are not SPX or Shopee policy. The authoritative BI v2.2 case and test datasets were not available when this demo was built, so the fixtures are development examples rather than a BI acceptance suite.

## Requirements

- Node.js 22.14.0 (`.nvmrc`; better-sqlite3 must be installed for this ABI)
- npm
- An OpenAI API key for live assessments (offline tests do not need one)

## Run locally

```bash
npm ci
cp .env.example .env
# Set OPENAI_API_KEY in .env for live assessments
# OPENAI_REASONING_EFFORT defaults to high (supported: none, low, medium, high, xhigh, max)
npm run dev
```

Open <http://localhost:3000>. Keep the API key server-side; do not commit `.env`.
The database defaults to `./runtime/order-rescue.sqlite`, outside the static asset tree. Keep that directory on persistent storage when hosting. The SQLite MVP is intended for one backend worker. `HOST` and `PORT` configure the listener; `/healthz` is a simple health endpoint. Do not expose a hosted demo publicly without access protection and spending controls.

## Verify

```bash
npm run typecheck
npm test
npm run build
npm run test:e2e
```

## Workflow

The Hono server serves the browser UI and API. The harness loads synthetic case inputs, runs eligibility checks, asks the VoltAgent assessment agent (OpenAI `gpt-6.1-terra` by default, reasoning effort `high`) to interpret the available evidence, validates provenance and the response schema, applies deterministic policy gates, and stores immutable workflow decisions in SQLite. Set `OPENAI_MODEL` to select another compatible OpenAI model and `OPENAI_REASONING_EFFORT` to change the effort (`none`, `low`, `medium`, `high`, `xhigh`, or `max`). Higher effort may increase latency and token use. Initial and reply assessments stream draft tokens to the UI over SSE; the final assessment and policy only appear after validation and persistence. The explanation panel shows concise evidence-based reasons and policy outcomes, not hidden internal model reasoning. Buyer replies and manual no-reply events are persisted with idempotency checks. Model or validation failures go to human review.

The model has no tools and cannot take operational actions. Courier notes and buyer replies are untrusted data. The database is local demo state and should not be populated with real customer information.

## Tomorrow's deployment checklist

Use Node 22.14.0, `npm ci`, `npm run build`, then `npm start`. Set `OPENAI_API_KEY` only in the server environment; configure `OPENAI_MODEL`, `OPENAI_REASONING_EFFORT`, `DB_PATH`, `HOST`, and `PORT` there as needed. Persist the directory containing `DB_PATH`, run one backend worker, and put authentication/access control plus request-spend limits in front of any public deployment. This repository is a synthetic illustration and has not passed the absent BI v2.2 30-case evaluation. Do not describe it as production-ready.
