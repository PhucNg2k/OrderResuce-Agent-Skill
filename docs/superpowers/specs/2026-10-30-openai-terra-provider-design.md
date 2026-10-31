# OpenAI GPT-6.1 Terra provider design

## Goal

Use OpenAI's `gpt-6.1-terra` API model for the existing VoltAgent assessment call, authenticated with `OPENAI_API_KEY`.

## Design

Replace the DeepSeek AI SDK provider with the OpenAI AI SDK provider. Read `OPENAI_API_KEY` at assessment time and select `OPENAI_MODEL`, defaulting to the official model ID `gpt-6.1-terra`. Keep the existing VoltAgent `Agent.generateText` call, JSON parsing, Zod validation, provenance checks, deterministic policy gate, persistence, and human-review handling unchanged.

Update `.env.example`, README, and AGENTS instructions to describe the OpenAI configuration. No API key value will be added to source control or printed. No operational tools or actions are introduced.

## Verification

Run typecheck, unit/integration tests, and production build. E2E can be run as a regression check. A live provider request is only useful if `OPENAI_API_KEY` is present in the local environment; never expose its value.
