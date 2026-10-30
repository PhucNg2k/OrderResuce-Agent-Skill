# VoltAgent Root Migration Implementation Plan

> **For agentic workers:** Execute inline task by task, checking each command result before continuing.

**Goal:** Promote the standalone VoltAgent TypeScript app to the repository root on `volt-agent-implementation` and push the verified branch.

**Architecture:** Preserve the existing history and branch from `main`. Move source-controlled TypeScript app files to root, remove the Python prototype from this branch, and update root safety and run documentation.

**Tech Stack:** Node.js, TypeScript, VoltAgent, Hono, SQLite, npm, Playwright.

## Global Constraints

- Work only on `volt-agent-implementation`.
- Exclude `.env`, `node_modules/`, `dist/`, SQLite files, Playwright output, test results, caches, `.DS_Store`, and `volt-app.zip`.
- Keep this as a synthetic recommendation demo; do not introduce real logistics actions or real customer data.
- Run npm typecheck, tests, build, and E2E before committing and pushing.

## File map

- `src/`, `tests/`, `e2e/`, `public/`, `fixtures/synthetic/`: application code, tests, UI, synthetic inputs.
- `package.json`, `package-lock.json`, `tsconfig.json`, `playwright.config.ts`, `.env.example`, `.gitignore`: root Node configuration.
- `README.md`, `AGENTS.md`: root project and safety instructions.
- Python `runtime/`, `skills/`, `tests/`, `fixtures/`, and `pyproject.toml`: removed from this branch.

## Tasks

### Task 1: Promote the TypeScript app and remove the Python prototype

1. Confirm current branch and inspect ignored/generated app files.
2. Move tracked app files to root: `.env.example`, `.gitignore`, `e2e/`, `fixtures/synthetic/`, `package-lock.json`, `package.json`, `playwright.config.ts`, `public/`, `reports/`, `src/`, `tests/`, and `tsconfig.json`.
3. Remove Python runtime, skills, Python tests, Python fixtures, and `pyproject.toml` from this branch.
4. Update root `.gitignore` for Node dependencies/builds, local env, SQLite, test output, and OS files.
5. Verify `git status` lists no generated or local database files for addition.

### Task 2: Replace root guidance

1. Replace `README.md` with prerequisites, `.env` setup, run/test commands, architecture summary, and demo limitations.
2. Replace `AGENTS.md` with the fixed TypeScript workflow order, safety invariants, test commands, and synthetic-only warning.
3. Keep the migration spec and plan under `docs/superpowers/`.
4. Run `git diff --check` and inspect the full staged diff.

### Task 3: Verify, commit, and push

1. Run `npm ci`.
2. Run `npm run typecheck`, `npm test`, `npm run build`, and `npm run test:e2e`.
3. Stage only the intended app/docs files and inspect staged names and diff.
4. Commit with `feat: promote VoltAgent app to repository root`.
5. Push with `git push -u origin volt-agent-implementation`.
6. Confirm the branch/upstream and final worktree status.
