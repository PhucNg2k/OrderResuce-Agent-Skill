import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { test } from 'node:test';

test('VoltAgent model streams close the observability instance used by the app', () => {
  const output = execFileSync(
    process.execPath,
    ['--import', 'tsx', 'tests/agent-lifecycle-worker.ts'],
    { encoding: 'utf8', timeout: 5_000 },
  );

  assert.match(output, /"shared_observability":true/);
  assert.doesNotMatch(output, /"Timeout"/);
});
