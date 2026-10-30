# Order Rescue VoltAgent Demo

A synthetic delivery-failure workflow demo for operations teams. It recommends a next step and records the decision; it does not perform delivery, messaging, refund, cancellation, or other logistics actions.

All examples are synthetic. The included business rules are illustrative and are not SPX or Shopee policy. The authoritative BI v2.2 case and test datasets were not available when this demo was built, so the fixtures are development examples rather than a BI acceptance suite.

## Requirements

- Node.js 20 or newer
- npm
- A DeepSeek API key for live assessments (offline tests do not need one)

## Run locally

```bash
npm ci
cp .env.example .env
# Set DEEPSEEK_API_KEY in .env for live assessments
npm run dev
```

Open <http://localhost:3000>. Keep the API key server-side; do not commit `.env`.

## Verify

```bash
npm run typecheck
npm test
npm run build
npm run test:e2e
```

## Workflow

The Hono server serves the browser UI and API. The harness loads synthetic case inputs, runs eligibility checks, asks the VoltAgent assessment agent to interpret the available evidence, validates provenance and the response schema, applies deterministic policy gates, and stores immutable workflow decisions in SQLite. Buyer replies and manual no-reply events are persisted with idempotency checks. Model or validation failures go to human review.

The model has no tools and cannot take operational actions. Courier notes and buyer replies are untrusted data. The database is local demo state and should not be populated with real customer information.
