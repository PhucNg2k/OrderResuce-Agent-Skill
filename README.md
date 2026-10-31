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

The harness performs synthetic lifecycle checks, then generation extracts evidence, Decisions (`gpt-6-luna`) selects cause and candidate action, and generation summarizes gaps. Deterministic policy and the existing semantic verifier still gate recommendations. Configure generation with `OPENAI_MODEL` and `OPENAI_REASONING_EFFORT`; configure Decisions separately with `DECISIONS_MODEL`, `DECISIONS_TIMEOUT_MS`, and `DECISIONS_MAX_RETRIES=0`. Probability distributions and API confidence are stored as decision metadata. Public LOW/MEDIUM/HIGH confidence describes evidence support, not calibrated delivery success. No automatic legacy fallback occurs when Decisions fails. The current simulated demo allows up to two clarification rounds. The authoritative BI v2.2 datasets remain unavailable, so this is not a BI acceptance or operational readiness claim.

The model has no tools and cannot take operational actions. Courier notes and buyer replies are untrusted data. The database is local demo state and should not be populated with real customer information.

## Tomorrow's deployment checklist

Use Node 22.14.0, `npm ci`, `npm run build`, then `npm start`. Set `OPENAI_API_KEY` only in the server environment; configure `OPENAI_MODEL`, `OPENAI_REASONING_EFFORT`, `DB_PATH`, `HOST`, and `PORT` there as needed. Persist the directory containing `DB_PATH`, run one backend worker, and put authentication/access control plus request-spend limits in front of any public deployment. This repository is a synthetic illustration and has not passed the absent BI v2.2 30-case evaluation. Do not describe it as production-ready.
