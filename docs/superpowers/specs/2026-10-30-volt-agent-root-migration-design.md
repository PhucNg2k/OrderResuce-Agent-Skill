# VoltAgent root migration design

## Goal

Replace the Python prototype on the `volt-agent-implementation` branch with the standalone TypeScript application currently staged in `volt-app/`. The branch remains reviewable against `main`; `main` is not modified.

## Chosen approach

Promote the contents of `volt-app/` to the repository root on a normal branch created from `main`. This preserves the existing Git history and presents the migration as a conventional pull-request diff. We will not use an orphan branch or retain both applications as a monorepo.

## Repository layout

The root application will contain the TypeScript sources, tests, browser test, public UI, synthetic fixtures, reports, Node package manifests, and TypeScript/Playwright configuration from `volt-app/`.

The old Python runtime, skills, tests, fixtures, Python packaging, and Python-specific documentation will be removed from this branch. Root documentation will be updated so commands, architecture, safety boundaries, and synthetic-data limitations describe the VoltAgent implementation.

Generated or local state will not be promoted: `node_modules/`, `dist/`, `.env`, SQLite database files and WAL files, Playwright output, test results, `.DS_Store`, the source ZIP, and other caches remain untracked.

## Runtime behavior and safety

The migration changes packaging and repository structure, not the existing TypeScript workflow behavior. The application remains a synthetic demonstration that recommends outcomes and persists workflow state; it does not connect to real logistics actions.

The implementation keeps lifecycle prechecks before model execution, structured assessment validation, provenance checks, policy gating, immutable assessment snapshots, idempotent reply/no-reply handling, and durable human-review outcomes for model or validation failures.

## Migration sequence

1. Establish a clean root `.gitignore` for Node, local secrets, databases, generated builds, test output, and caches.
2. Remove the tracked Python application from this branch.
3. Move the source-controlled `volt-app/` files to the root without moving generated/local artifacts.
4. Replace root README and AGENTS instructions with VoltAgent-specific documentation.
5. Install from the lockfile and run type checking, unit/integration tests, build, and browser tests.
6. Commit the migration and push `volt-agent-implementation` to `origin`.

## Verification and acceptance

The migration is accepted when:

- `npm ci` succeeds from the repository root.
- `npm run typecheck` passes.
- `npm test` passes.
- `npm run build` passes.
- `npm run test:e2e` passes, or a concrete environment limitation is reported.
- `git status` contains no generated output or secret/database files selected for commit.
- The branch is pushed to `origin/volt-agent-implementation` without modifying `main`.

## Known limitations

The supplied app uses synthetic fixtures and does not include the missing authoritative BI v2.2 JSON datasets. Live DeepSeek execution requires a user-provided server-side key and is not required for offline migration verification. Existing SQLite databases from prototype iterations are local state and are deliberately excluded.
