# OpenAI Terra Provider Implementation Plan

> **For agentic workers:** Execute inline, with verification after each change.

**Goal:** Configure the VoltAgent assessor to use OpenAI `gpt-6.1-terra` with `OPENAI_API_KEY`.

**Architecture:** Swap the AI SDK provider while keeping VoltAgent orchestration and the current assessment validation/policy pipeline intact. Make the API model configurable through `OPENAI_MODEL`, defaulting to `gpt-6.1-terra`.

**Tech Stack:** TypeScript, VoltAgent, Vercel AI SDK OpenAI provider, Zod.

## Global Constraints

- Never print or commit the API key value.
- Preserve the existing no-tools agent boundary and deterministic policy gates.
- Preserve human review on model/schema/provenance failure.

## Tasks

1. Replace the DeepSeek provider with `@ai-sdk/openai`, configured from `OPENAI_API_KEY` and `OPENAI_MODEL || 'gpt-6.1-terra'`.
2. Replace DeepSeek environment instructions with OpenAI instructions in `.env.example`, README, AGENTS, and assessment metadata.
3. Install from/update the npm lockfile and run `npm run typecheck`, `npm test`, `npm run build`, and `npm run test:e2e`.
4. Inspect diff and worktree; report whether a key is configured without displaying its value.
