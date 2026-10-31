import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
const testDir = fs.mkdtempSync(path.join(os.tmpdir(), 'order-rescue-e2e-'));
process.env.DB_PATH = path.join(testDir, 'state.sqlite');
process.env.NODE_ENV = 'test';
process.env.ORDER_RESCUE_TEST_NOW = '2026-10-25T12:00:00.000Z';
const { setAssessorForTests, setVerifierForTests, closeHarnessDatabase } = await import('../src/harness.js');
const { shutdownAgentTelemetry } = await import('../src/agent.js');
let failFirstRetryCase = true;
setVerifierForTests(async (_input, facts) => Object.fromEntries(Object.keys(facts).map(key => [key, { status: 'SUPPORTED', source_ref: 'SYN-01-REPLY', supporting_span: 'synthetic test response' }])));
setAssessorForTests(async input => {
  if (input.case_id === 'SYN-02' && failFirstRetryCase) { failFirstRetryCase = false; throw new Error('deterministic test failure requiring explicit retry'); }
  const noteRef = Object.keys(input.sources).find(ref => ref.endsWith('-NOTE'))!;
  return ({
  assessment: { evidence: [{ source_ref: noteRef, fact: 'Synthetic note available in fixture.', verification: 'UNVERIFIED_REPORT' }], hypothesis: 'AVAILABILITY_ISSUE', confidence: 'LOW', missing_info: ['CURRENT_BUYER_INTENT', 'RECEIVING_AVAILABILITY'], question_key: 'CONFIRM_INTENT', candidate_action: 'CLARIFY' },
  decision_facts: { intent: 'UNKNOWN', availability: 'UNKNOWN', cod_readiness: 'UNKNOWN', address: 'UNKNOWN', refusal: 'NONE', supporting_evidence: [], explanation: `Deterministic test assessment turn ${input.turn_index || 0}.`, question_text: 'For this synthetic test, what receiving arrangement works for you?' },
  meta: { model: 'deterministic-e2e-stub', prompt_version: 'e2e-stub-v1', latency_ms: 1, usage: { inputTokens: 0, outputTokens: 0 } },
  });
});
const { app } = await import('../src/server.js');
const { serve } = await import('@hono/node-server');
const port = Number(process.env.PORT || 4387);
const server = serve({ fetch: app.fetch, port, hostname: '127.0.0.1' });
let closing = false;
const cleanup = async () => { if (closing) return; closing = true; server.close(); await shutdownAgentTelemetry(); closeHarnessDatabase(); fs.rmSync(testDir, { recursive: true, force: true }); };
process.once('SIGINT', () => { void cleanup(); });
process.once('SIGTERM', () => { void cleanup(); });
console.log(`Stubbed real-backend e2e server listening on ${port}`);
