import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
test('a fresh process reconciles interrupted assessments to review', () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'order-rescue-recovery-'));
  const dbPath = path.join(dir, 'state.sqlite');
  const worker = path.resolve('tests/recovery-worker.ts');
  const tsx = path.resolve('node_modules/.bin/tsx');
  const env = { ...process.env, DB_PATH: dbPath };
  try {
    const runId = execFileSync(tsx, [worker, 'seed'], { env, encoding: 'utf8' }).trim();
    const recovered = JSON.parse(execFileSync(tsx, [worker, 'inspect', runId], { env, encoding: 'utf8' }));
    assert.equal(recovered.state, 'HUMAN_REVIEW');
    assert.match(recovered.error, /Interrupted while an assessment was processing/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});
