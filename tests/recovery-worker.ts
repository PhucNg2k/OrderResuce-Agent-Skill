import Database from 'better-sqlite3';
import { start, getRun, setAssessorForTests, closeHarnessDatabase } from '../src/harness.js';
import { shutdownAgentTelemetry } from '../src/agent.js';
const [mode, runId] = process.argv.slice(2);
if (mode === 'seed') {
  setAssessorForTests(async () => ({ assessment: { evidence: [{ source_ref: 'SYN-01-NOTE', fact: 'Synthetic note.', verification: 'UNVERIFIED_REPORT' }], hypothesis: 'AVAILABILITY_ISSUE', confidence: 'LOW', missing_info: ['CURRENT_BUYER_INTENT'], question_key: 'CONFIRM_INTENT', candidate_action: 'CLARIFY' }, decision_facts: { intent: 'UNKNOWN', availability: 'UNKNOWN', cod_readiness: 'UNKNOWN', address: 'UNKNOWN', refusal: 'NONE', supporting_evidence: [], explanation: 'Synthetic seed.', question_text: 'What receiving arrangement would work?' } }));
  const run = await start('SYN-01');
  const db = new Database(process.env.DB_PATH!);
  db.prepare("update runs set state='ASSESSING_REPLY'").run();
  db.close();
  console.log(run.id);
  closeHarnessDatabase();
  await shutdownAgentTelemetry();
} else if (mode === 'inspect') { console.log(JSON.stringify(getRun(runId!))); closeHarnessDatabase(); await shutdownAgentTelemetry(); }
else throw new Error(`Unknown mode ${mode}`);
