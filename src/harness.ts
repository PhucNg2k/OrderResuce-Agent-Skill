import Database from 'better-sqlite3';
import { randomUUID, createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { assessmentSchema, questionKeys, type CaseInput, type Assessment, type Policy, type ConversationTurn } from './domain.js';
import { assess as liveAssess, envelopeSchema, generateFollowupQuestion as liveQuestionGenerator, verifySemantics as liveVerify } from './agent.js';

const dbPath = process.env.DB_PATH || 'order-rescue.sqlite';
if (dbPath !== ':memory:') fs.mkdirSync(path.dirname(path.resolve(dbPath)), { recursive: true });
const db = new Database(dbPath);
db.pragma('journal_mode=WAL');
db.exec(`CREATE TABLE IF NOT EXISTS runs(
 id TEXT PRIMARY KEY, case_id TEXT, state TEXT NOT NULL, input TEXT, input_hash TEXT,
 phase2_input TEXT, phase2_hash TEXT, initial TEXT, initial_policy TEXT,
 after_reply TEXT, after_policy TEXT, final TEXT, final_policy TEXT, source INTEGER,
 question TEXT, question_id TEXT, reply TEXT, created TEXT, meta TEXT, precheck TEXT,
 error TEXT, events TEXT DEFAULT '[]', assessment_history TEXT NOT NULL DEFAULT '[]',
 interactions TEXT NOT NULL DEFAULT '[]', final_assessment_id TEXT, final_turn_index INTEGER,
 mode TEXT NOT NULL DEFAULT 'demo-multiturn-v1');
 CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,event_type TEXT NOT NULL,payload_hash TEXT NOT NULL,result_json TEXT NOT NULL,created TEXT NOT NULL);`);
// Existing prototype databases predate multi-turn bookkeeping. Additive migrations preserve their history.
const columns = new Set((db.pragma('table_info(runs)') as { name: string }[]).map(x => x.name));
for (const [name, declaration] of Object.entries({assessment_history:"TEXT NOT NULL DEFAULT '[]'",interactions:"TEXT NOT NULL DEFAULT '[]'",final_assessment_id:'TEXT',final_turn_index:'INTEGER',mode:"TEXT NOT NULL DEFAULT 'demo-multiturn-v1'"})) {
  if (!columns.has(name)) db.exec(`ALTER TABLE runs ADD COLUMN ${name} ${declaration}`);
}
db.exec('CREATE TABLE IF NOT EXISTS schema_meta (version INTEGER NOT NULL)');
const schemaVersion = db.prepare('select version from schema_meta limit 1').get() as { version: number } | undefined;
if (schemaVersion && schemaVersion.version > 2) throw new Error(`Database schema ${schemaVersion.version} is newer than this app supports (2)`);
if (!schemaVersion) db.prepare('insert into schema_meta(version) values(2)').run();
else if (schemaVersion.version < 2) db.prepare('update schema_meta set version=2').run();
const fixtures = JSON.parse(fs.readFileSync(new URL('../fixtures/synthetic/cases.json', import.meta.url), 'utf8')) as any[];
export type TokenCallback = (delta: string) => void;
export type Assessor = (input: CaseInput, onToken?: TokenCallback) => Promise<any>;
let assessor: Assessor = liveAssess;
export function setAssessorForTests(fn: Assessor) { assessor = fn; }
type Verifier = (input: CaseInput, proposed: unknown) => Promise<any>;
let verifier: Verifier = liveVerify;
export function setVerifierForTests(fn: Verifier) { verifier = fn; }
type GeneratedQuestion = { question_key: typeof questionKeys[number] | null; question_text: string | null; metadata?: any };
type QuestionGenerator = (input: CaseInput, unresolvedFacts: string[]) => Promise<GeneratedQuestion | null>;
let questionGenerator: QuestionGenerator = liveQuestionGenerator;
export function setQuestionGeneratorForTests(fn?: QuestionGenerator) { questionGenerator = fn || liveQuestionGenerator; }
const MAX_CLARIFICATION_ROUNDS = Number(process.env.MAX_CLARIFICATION_ROUNDS || 2);
if (!Number.isInteger(MAX_CLARIFICATION_ROUNDS) || MAX_CLARIFICATION_ROUNDS < 1 || MAX_CLARIFICATION_ROUNDS > 2) throw new Error('MAX_CLARIFICATION_ROUNDS must be 1 or 2');
const hash = (x: unknown) => createHash('sha256').update(JSON.stringify(x)).digest('hex');
const now = () => new Date(process.env.NODE_ENV==='test'&&process.env.ORDER_RESCUE_TEST_NOW?process.env.ORDER_RESCUE_TEST_NOW:Date.now());

function inputFor(c: any, interactions: ConversationTurn[] = [], active?: ConversationTurn, assessmentAsOf = now().toISOString()): CaseInput {
  const sources: CaseInput['sources'] = { [`${c.case_id}-FAIL`]: { text: c.failed_event.status, verification: 'SOURCE_RECORD', owner_case: c.case_id, available_phase: 'T0' } };
  const buyer: { source_ref: string; text: string }[] = [];
  if (c.failed_event.courier_note) sources[`${c.case_id}-NOTE`] = { text: c.failed_event.courier_note, verification: 'UNVERIFIED_REPORT', owner_case: c.case_id, available_phase: 'T0' };
  if (c.buyer_context) {
    buyer.push({ source_ref: `${c.case_id}-BUYER-T0`, text: c.buyer_context });
    sources[`${c.case_id}-BUYER-T0`] = { text: c.buyer_context, verification: 'DIRECT_BUYER_STATEMENT', owner_case: c.case_id, available_phase: 'T0' };
  }
  const runtime_context: { source_ref: string; text: string }[] = [];
  interactions.forEach((turn, i) => {
    if (!turn.reply_text) return;
    const source_ref = i === 0 ? `${c.case_id}-REPLY` : `${c.case_id}-REPLY-${i + 1}`;
    runtime_context.push({ source_ref, text: turn.reply_text });
    sources[source_ref] = { text: turn.reply_text, verification: 'DIRECT_BUYER_STATEMENT', owner_case: c.case_id, available_phase: 'AFTER_REPLY' };
  });
  if (active?.reply_text && !interactions.some(t => t.question_id === active.question_id)) {
    const source_ref = `${c.case_id}-REPLY-${active.turn_index}`;
    runtime_context.push({ source_ref, text: active.reply_text });
    sources[source_ref] = { text: active.reply_text, verification: 'DIRECT_BUYER_STATEMENT', owner_case: c.case_id, available_phase: 'AFTER_REPLY' };
  }
  const prior = active || interactions.at(-1) || null;
  return {
    case_id: c.case_id, failed_event: c.failed_event, assessment_as_of: assessmentAsOf, attempts_used: c.attempts_used,
    return_state: c.return_state, deadline: c.deadline, buyer_history: [],
    operational_context: { route: c.route, payment: c.payment, policy_version: 'demo-multiturn-v1', buyer_messages_t0: buyer, ops: c.ops },
    prior_buyer_question: prior ? { question_key: prior.question_key, question_text: prior.question_text } : null,
    conversation_context: [...interactions, ...(active && !interactions.some(t => t.question_id === active.question_id) ? [active] : [])],
    turn_index: interactions.filter(t => t.reply_text).length + (active?.reply_text ? 1 : 0),
    max_clarification_rounds: MAX_CLARIFICATION_ROUNDS, runtime_context, sources,
  };
}
function precheck(c: any, asOf = c.failed_event.as_of) {
  if (!Number.isInteger(c.attempts_used) || c.attempts_used < 0) return { eligibility: 'UNKNOWN', state: 'REVIEW', reason: 'Invalid attempts metadata.' };
  if (c.return_state === 'STARTED' || c.return_state === 'COMPLETED') return { eligibility: 'INELIGIBLE', state: 'BLOCKED', reason: 'Return lifecycle has started or completed.' };
  if (c.return_state !== 'NOT_STARTED' || !c.deadline) return { eligibility: 'UNKNOWN', state: 'REVIEW', reason: 'Lifecycle or logistics deadline is unknown.' };
  const deadline = Date.parse(c.deadline), asof = Date.parse(asOf);
  if (!Number.isFinite(deadline) || !Number.isFinite(asof)) return { eligibility: 'UNKNOWN', state: 'REVIEW', reason: 'Invalid logistics timestamp.' };
  if (asof > deadline) return { eligibility: 'INELIGIBLE', state: 'BLOCKED', reason: 'Logistics deadline has passed.' };
  if (c.attempts_used >= 3) return { eligibility: 'INELIGIBLE', state: 'BLOCKED', reason: 'Documented demo max attempts (3) reached.' };
  return { eligibility: 'ELIGIBLE', state: 'READY', reason: 'Documented lifecycle checks passed.' };
}
function validateSources(input: CaseInput, out: any) {
  for (const e of out.assessment.evidence) {
    const src = input.sources[e.source_ref];
    if (!src || src.owner_case !== input.case_id) throw Error('Unavailable or wrong-owner evidence source');
    if (src.available_phase === 'AFTER_REPLY' && !input.runtime_context.some(x => x.source_ref === e.source_ref)) throw Error('Evidence source unavailable in this phase');
    if (e.verification !== src.verification) throw Error('Evidence verification incompatible with source provenance');
  }
  for (const fact of out.decision_facts.supporting_evidence) {
    const src = input.sources[fact.source_ref];
    if (!src || src.owner_case !== input.case_id) throw Error('Decision fact cites unavailable or foreign source');
    if (src.available_phase === 'AFTER_REPLY' && !input.runtime_context.some(x => x.source_ref === fact.source_ref)) throw Error('Decision fact source unavailable in phase');
    if (!fact.supporting_text || !src.text.includes(fact.supporting_text)) throw Error('Decision fact supporting text is not present in source record');
    if (fact.fact_key === 'intent' && out.decision_facts.intent === 'CONFIRMED' && src.verification !== 'DIRECT_BUYER_STATEMENT') throw Error('Confirmed buyer intent requires direct buyer source');
    if (fact.fact_key === 'availability' && out.decision_facts.availability === 'CONFIRMED' && src.verification !== 'DIRECT_BUYER_STATEMENT') throw Error('Unverified report cannot confirm receiving availability');
    if (fact.fact_key === 'cod_readiness' && out.decision_facts.cod_readiness === 'CONFIRMED' && src.verification !== 'DIRECT_BUYER_STATEMENT') throw Error('Confirmed COD readiness requires direct buyer source');
    if (fact.fact_key === 'cod_readiness' && input.operational_context.payment !== 'COD') throw Error('COD readiness claim without COD context');
    if (fact.fact_key === 'refusal' && out.decision_facts.refusal === 'DIRECT' && src.verification !== 'DIRECT_BUYER_STATEMENT') throw Error('Direct refusal requires direct buyer source');
  }
  for (const key of ['intent','availability','cod_readiness','address','refusal']) if (out.decision_facts[key] === 'CONFIRMED' || out.decision_facts[key] === 'DIRECT' || (key === 'intent' && out.decision_facts.intent === 'REFUSED')) {
    if (!out.decision_facts.supporting_evidence.some((x: any) => x.fact_key === key)) throw Error(`Decision fact ${key} lacks sourced support`);
  }
  if (out.decision_facts.intent === 'REFUSED' && out.decision_facts.refusal !== 'DIRECT') throw Error('Refused intent requires direct buyer refusal evidence');
  if (out.decision_facts.availability === 'CONDITIONAL' && out.assessment.candidate_action === 'STANDARD_REATTEMPT') throw Error('Conditional availability cannot support standard reattempt');
  if (out.decision_facts.availability === 'CONFLICTED' || out.decision_facts.intent === 'CONFLICTED' || out.decision_facts.cod_readiness === 'CONFLICTED') throw Error('Conflicting decision facts require review');
}
function policy(c: any, a: Assessment, f: any, check: any): Policy {
  if (check.eligibility !== 'ELIGIBLE') return { eligibility: check.eligibility, policy_gate: check.state === 'BLOCKED' ? 'BLOCKED' : 'ESCALATED', final_action: 'ESCALATE_REVIEW', reason: check.reason };
  if (c.ops?.verified === true && c.ops.status === 'ACTIVE' && c.ops.route_match === true && c.ops.time_match === true && c.ops.reassess_required === true) return { eligibility: 'ELIGIBLE', policy_gate: 'PERMITTED', final_action: 'HOLD_DISRUPTION', reason: 'Valid hold recommendation: verified active disruption requires reassessment.' };
  if (f.intent === 'REFUSED' || f.refusal === 'DIRECT' || f.address === 'CHANGE_REQUEST' || f.address === 'CONFLICTED') return { eligibility: 'ELIGIBLE', policy_gate: 'ESCALATED', final_action: 'ESCALATE_REVIEW', reason: 'Buyer refusal, address change, or conflicting address facts require operations review.' };
  const ready = f.intent === 'CONFIRMED' && f.availability === 'CONFIRMED' && c.payment !== 'UNKNOWN' && (c.payment !== 'COD' || f.cod_readiness === 'CONFIRMED') && a.missing_info.length === 0 && f.address !== 'CHANGE_REQUEST' && f.refusal !== 'DIRECT';
  if (a.candidate_action === 'STANDARD_REATTEMPT' && ready) return { eligibility: 'ELIGIBLE', policy_gate: 'PERMITTED', final_action: 'STANDARD_REATTEMPT', reason: 'Required sourced facts confirmed.' };
  if (a.candidate_action === 'CLARIFY') return { eligibility: 'ELIGIBLE', policy_gate: 'PERMITTED', final_action: 'CLARIFY', reason: 'A bounded clarification may resolve the missing information.' };
  return { eligibility: 'ELIGIBLE', policy_gate: 'ESCALATED', final_action: 'ESCALATE_REVIEW', reason: 'Required facts are unknown, conflicting or outside permission.' };
}
function rec(id: string) { return db.prepare('select * from runs where id=?').get(id) as any; }
function parse(x: any) { return x && JSON.parse(x); }
function view(r: any) {
  if (!r) return null;
  const events = db.prepare('select event_type,created from events where run_id=? order by created,event_id').all(r.id);
  return { ...r, input: parse(r.input), phase2_input: parse(r.phase2_input), initial: parse(r.initial), initial_policy: parse(r.initial_policy), after_reply: parse(r.after_reply), after_policy: parse(r.after_policy), final: parse(r.final), final_policy: parse(r.final_policy), question: r.question, events, assessment_history: parse(r.assessment_history) || [], interactions: parse(r.interactions) || [], meta: parse(r.meta), precheck: parse(r.precheck) };
}
export const listCases = () => fixtures.map(({ case_id, title }) => ({ case_id, title, fixture_type: 'SYNTHETIC_DEVELOPMENT_ONLY' }));
function recordFailure(runId: string, phase: string, error: unknown) {
  const current = rec(runId), meta = parse(current?.meta) || {};
  const callMeta = (error as any)?.callMeta;
  if (callMeta) meta.failed_call = callMeta;
  meta.failure_phase = phase;
  meta.failure_class = error instanceof SyntaxError ? 'MALFORMED_JSON' : 'MODEL_OR_VALIDATION_ERROR';
  db.prepare("update runs set state='HUMAN_REVIEW',error=?,meta=? where id=? and state in ('ASSESSING','ASSESSING_REPLY','RETRYING')")
    .run(String(error), JSON.stringify(meta), runId);
}
export function recoverInterrupted() {
  const rows = db.prepare("select id from runs where state in ('ASSESSING','ASSESSING_REPLY','RETRYING')").all() as {id:string}[];
  const recover = db.transaction(() => { for (const {id} of rows) db.prepare("update runs set state='HUMAN_REVIEW',error='Interrupted while an assessment was processing; explicit operator review or retry is required.' where id=? and state in ('ASSESSING','ASSESSING_REPLY','RETRYING')").run(id); });
  recover();
  for (const {id} of rows) { const current=view(rec(id)); db.prepare("update events set result_json=? where run_id=? and result_json='{}'").run(JSON.stringify(current),id); }
}
recoverInterrupted();
export function closeHarnessDatabase(){db.close()}
function envelope(raw: any) { return envelopeSchema.parse(raw); }
function makeAssessmentRecord(runId: string, turnIndex: number, triggerEventId: string | null, input: CaseInput, raw: any, out: any, p: Policy): any {
  return { assessment_id: randomUUID(), run_id: runId, turn_index: turnIndex, trigger_event_id: triggerEventId, snapshot: input, snapshot_hash: hash(input), assessment: out.assessment, internal_facts: out.decision_facts, policy: p, metadata: raw.meta || {} };
}
function questionFrom(record: any, turnIndex: number) {
  if ((record.effective_policy || record.policy).final_action !== 'CLARIFY' || (record.question_suppressed && !record.followup_question)) return null;
  const questionKey=record.followup_question?.question_key||record.assessment.question_key;
  const questionText=(record.followup_question?.question_text||record.internal_facts.question_text)?.trim();
  if (!questionKeys.includes(questionKey) || !questionText || questionText.length > 240) return null;
  return { question_id: randomUUID(), question_key: questionKey, question_text: questionText, status: 'PENDING', asked_at: now().toISOString(), turn_index: turnIndex };
}
async function prepareVerifierFollowup(input:CaseInput,out:any,verified:any,record:any,interactions:ConversationTurn[]){
  const unresolved:string[]=verified.clarification_facts||[];
  if(!unresolved.length)return;
  record.question_suppressed=true;
  if(interactions.length>=MAX_CLARIFICATION_ROUNDS)return;
  const priorTexts=new Set((input.conversation_context||[]).map(turn=>turn.question_text.trim().toLocaleLowerCase()));
  const proposedKey=out.assessment.question_key,proposedText=out.decision_facts.question_text?.trim();
  if(proposedKey&&questionKeys.includes(proposedKey)&&proposedText&&proposedText.length<=240&&!priorTexts.has(proposedText.toLocaleLowerCase())){
    record.followup_question={question_key:proposedKey,question_text:proposedText};
    record.followup_question_source='ASSESSMENT_PROPOSAL';
    record.question_suppressed=false;
    return;
  }
  const generated=await questionGenerator(input,unresolved);
  if(!generated){record.followup_question_status='NO_USEFUL_QUESTION';return;}
  const key=generated.question_key,text=generated.question_text?.trim();
  record.followup_question_metadata=generated.metadata||null;
  if(!key&&!text){record.followup_question_status='NO_USEFUL_QUESTION';return;}
  if(key!=='CONFIRM_INTENT'||!text||text.length>240||priorTexts.has(text.toLocaleLowerCase()))throw Error('Generated follow-up question failed topic, length, or duplication validation');
  record.followup_question={question_key:key,question_text:text};
  record.followup_question_source='SEMANTIC_VERIFIER_FOLLOWUP';
  record.followup_question_status='GENERATED';
  record.question_suppressed=false;
}
async function verifyRetry(input: CaseInput, facts: unknown, candidatePolicy: Policy) {
  if (candidatePolicy.final_action !== 'STANDARD_REATTEMPT') return { policy: candidatePolicy, verification: null };
  const verification = await verifier(input, facts);
  const checks = new Map(verification.checks.map((x: any) => [x.fact_key, x.verdict]));
  const proposed = facts as any;
  const prerequisites = ['intent','availability', ...(input.operational_context.payment === 'COD' ? ['cod_readiness'] : [])];
  const failedPrerequisites = prerequisites.filter(key => checks.get(key) !== 'SUPPORTED');
  const addressNotPresent = proposed.address === 'UNKNOWN' && checks.get('address') === 'NOT_PRESENT';
  const refusalNotPresent = proposed.refusal === 'NONE' && checks.get('refusal') === 'NOT_PRESENT';
  const failedGuards = [
    ...(checks.get('address') !== 'SUPPORTED' && !addressNotPresent ? ['address'] : []),
    ...(checks.get('refusal') !== 'SUPPORTED' && !refusalNotPresent ? ['refusal'] : []),
  ];
  const failed = [...failedPrerequisites, ...failedGuards];
  const canAskBuyer = failedPrerequisites.length > 0 && failedGuards.length === 0;
  const reason = `Semantic verification did not support retry prerequisites: ${failed.join(', ')}.`;
  const policy = !failed.length ? candidatePolicy : canAskBuyer
    ? { ...candidatePolicy, policy_gate: 'PERMITTED' as const, final_action: 'CLARIFY' as const, reason: `${reason} A bounded buyer clarification may resolve these facts.` }
    : { ...candidatePolicy, policy_gate: 'ESCALATED' as const, final_action: 'ESCALATE_REVIEW' as const, reason };
  return { policy, verification, clarification_facts: canAskBuyer ? failed : [] };
}
function selectedFinalPolicy(record: any, exhausted: boolean) {
  const effective = record.effective_policy || record.policy;
  return exhausted ? { ...effective, policy_gate: 'ESCALATED', final_action: 'ESCALATE_REVIEW', reason: `Clarification budget exhausted; unresolved information: ${record.assessment.missing_info.join(', ') || 'buyer-resolvable details remain unclear'}.` } : effective;
}
function updateEventResult(eventId: string, payload: any, result: any) { db.prepare('update events set result_json=? where event_id=? and payload_hash=?').run(JSON.stringify(result), eventId, hash(payload)); }

export async function start(caseId: string, onToken?: TokenCallback) {
  const c = fixtures.find(x => x.case_id === caseId); if (!c) throw Error('Unknown synthetic case');
  const id = randomUUID(), assessmentAsOf = now().toISOString(), check = precheck(c, assessmentAsOf), inp = inputFor(c, [], undefined, assessmentAsOf), snap = JSON.stringify(inp), ih = hash(inp);
  db.prepare('insert into runs(id,case_id,state,input,input_hash,created,precheck) values(?,?,?,?,?,?,?)').run(id, caseId, check.state === 'READY' ? 'ASSESSING' : check.state, snap, ih, assessmentAsOf, JSON.stringify(check));
  if (check.state !== 'READY') return view(rec(id));
  try {
    const raw = await assessor(inp, onToken), out = envelope(raw), a = assessmentSchema.parse(out.assessment); validateSources(inp, out);
    const assessedPolicy = policy(c, a, out.decision_facts, check), verified = await verifyRetry(inp, out.decision_facts, assessedPolicy), p = verified.policy, record = makeAssessmentRecord(id, 0, null, inp, raw, out, assessedPolicy);
    await prepareVerifierFollowup(inp,out,verified,record,[]);
    record.effective_policy = p; record.policy_override = p.final_action===assessedPolicy.final_action?null:{kind:verified.clarification_facts?.length&&p.final_action==='CLARIFY'?'SEMANTIC_VERIFIER_FOLLOWUP':'SEMANTIC_VERIFIER',from:assessedPolicy.final_action,to:p.final_action,reason:p.reason};
    record.verification = verified.verification;
    const q = questionFrom(record, 1), history = [record];
    const terminal = !q;
    const finalP = !q && p.final_action === 'CLARIFY' ? { ...p, policy_gate: 'ESCALATED' as const, final_action: 'ESCALATE_REVIEW', reason: `No useful buyer question is available; unresolved information: ${a.missing_info.join(', ') || 'clarification cannot change the next action'}.` } : p;
    db.prepare('update runs set state=?,initial=?,initial_policy=?,question=?,question_id=?,assessment_history=?,final=?,final_policy=?,source=?,final_assessment_id=?,final_turn_index=?,meta=? where id=? and state=?')
      .run(q ? 'WAITING_FOR_BUYER' : 'COMPLETED', JSON.stringify(a), JSON.stringify(p), q && JSON.stringify(q), q?.question_id || null, JSON.stringify(history), terminal ? JSON.stringify(a) : null, terminal ? JSON.stringify(finalP) : null, terminal ? 1 : null, terminal ? record.assessment_id : null, terminal ? 0 : null, JSON.stringify({ ...raw.meta, explanation: out.decision_facts.explanation, input_hash: ih, phase: 'initial', assessment_calls: 1, verification: verified.verification, question_generation: record.followup_question_metadata || null, mode: 'demo-multiturn-v1' }), id, 'ASSESSING');
    return view(rec(id));
  } catch (e) { recordFailure(id, 'initial', e); return view(rec(id)); }
}
function priorEvent(eventId: string, runId: string, payload: any) {
  const h = hash(payload), old = db.prepare('select * from events where event_id=?').get(eventId) as any;
  if (!old) return null; if (old.run_id !== runId || old.payload_hash !== h) throw Error('EVENT_ID_PAYLOAD_CONFLICT'); if (old.result_json === '{}') throw Error('EVENT_IN_PROGRESS'); return JSON.parse(old.result_json);
}
export async function reply(id: string, qid: string, text: string, eventId: string, onToken?: TokenCallback) {
  const r = rec(id); if (!r) throw Error('Run not found');
  const payload = { type: 'BUYER_REPLY', run_id: id, question_id: qid, text }, duplicate = priorEvent(eventId, id, payload); if (duplicate) return duplicate;
  if (r.state !== 'WAITING_FOR_BUYER' || r.question_id !== qid) throw Error('Mismatched or non-pending question');
  const c = fixtures.find(x => x.case_id === r.case_id)!, interactions: ConversationTurn[] = parse(r.interactions) || [], active = parse(r.question) as ConversationTurn, replyAt=now().toISOString();
  db.transaction(() => db.prepare('insert into events values(?,?,?,?,?,?)').run(eventId, id, 'BUYER_REPLY', hash(payload), '{}', replyAt))();
  active.status = 'REPLIED'; active.reply_text = text; interactions.push(active);
  const inp = inputFor(c, interactions, undefined, replyAt), ih = hash(inp), turnIndex = interactions.filter(t => t.reply_text).length;
  const reserved = db.transaction(() => { const cur=rec(id); if(cur.state!=='WAITING_FOR_BUYER'||cur.question_id!==qid) throw Error('Run changed before reply reservation'); db.prepare("update runs set state='ASSESSING_REPLY',interactions=?,reply=? where id=? and state='WAITING_FOR_BUYER'").run(JSON.stringify(interactions),text,id); })();
  try {
    const raw = await assessor(inp, onToken), out = envelope(raw); validateSources(inp, out);
    const assessedPolicy = policy(c, out.assessment, out.decision_facts, precheck(c, replyAt)), verified = await verifyRetry(inp, out.decision_facts, assessedPolicy), p = verified.policy;
    const history = (parse(r.assessment_history) || []) as any[], record = makeAssessmentRecord(id, turnIndex, eventId, inp, raw, out, assessedPolicy); await prepareVerifierFollowup(inp,out,verified,record,interactions); record.effective_policy=p; record.policy_override=p.final_action===assessedPolicy.final_action?null:{kind:verified.clarification_facts?.length&&p.final_action==='CLARIFY'?'SEMANTIC_VERIFIER_FOLLOWUP':'SEMANTIC_VERIFIER',from:assessedPolicy.final_action,to:p.final_action,reason:p.reason}; record.verification = verified.verification; history.push(record);
    const proposedQuestion = questionFrom(record, turnIndex + 1), q = interactions.length < MAX_CLARIFICATION_ROUNDS ? proposedQuestion : null, exhausted = !q && p.final_action === 'CLARIFY' && interactions.length >= MAX_CLARIFICATION_ROUNDS;
    const finalP = !q && p.final_action === 'CLARIFY' && !exhausted ? { ...p, policy_gate: 'ESCALATED' as const, final_action: 'ESCALATE_REVIEW', reason: `No useful buyer question is available; unresolved information: ${out.assessment.missing_info.join(', ') || 'clarification cannot change the next action'}.` } : selectedFinalPolicy(record, exhausted), terminal = !q;
    const result = db.transaction(() => {
      const cur = rec(id); if (cur.state !== 'ASSESSING_REPLY' || cur.question_id !== qid) throw Error('Run changed during assessment');
      const state = q ? 'WAITING_FOR_BUYER' : 'COMPLETED';
      db.prepare('update runs set state=?,phase2_input=?,phase2_hash=?,after_reply=?,after_policy=?,final=?,final_policy=?,source=2,reply=?,question=?,question_id=?,assessment_history=?,interactions=?,final_assessment_id=?,final_turn_index=?,meta=? where id=? and state=?')
        .run(state, JSON.stringify(inp), ih, JSON.stringify(out.assessment), JSON.stringify(p), terminal ? JSON.stringify(out.assessment) : null, terminal ? JSON.stringify(finalP) : null, text, q && JSON.stringify(q), q?.question_id || null, JSON.stringify(history), JSON.stringify(interactions), terminal ? record.assessment_id : null, terminal ? turnIndex : null, JSON.stringify({ ...parse(r.meta), phase2: { ...raw.meta, explanation: out.decision_facts.explanation }, assessment_calls: (parse(r.meta)?.assessment_calls || 1) + 1, current_turn_index: turnIndex, verification: verified.verification, question_generation: record.followup_question_metadata || null, mode: 'demo-multiturn-v1' }), id, 'ASSESSING_REPLY');
      const result = view(rec(id)); updateEventResult(eventId, payload, result); return result;
    })(); return result;
  } catch (e) { recordFailure(id, `reply_${turnIndex}`, e); updateEventResult(eventId, payload, view(rec(id))); throw e; }
}
export function noReply(id: string, qid: string, eventId: string) {
  const r = rec(id); if (!r) throw Error('Run not found');
  const payload = { type: 'USER_NO_REPLY', run_id: id, question_id: qid }, duplicate = priorEvent(eventId, id, payload); if (duplicate) return duplicate;
  if (r.state !== 'WAITING_FOR_BUYER' || r.question_id !== qid) throw Error('Mismatched or non-pending question');
  return db.transaction(() => {
    const cur = rec(id); if (cur.state !== 'WAITING_FOR_BUYER' || cur.question_id !== qid) throw Error('Run changed before no-reply finalization');
    const q = parse(cur.question); q.status = 'NO_REPLY';
    const history = parse(cur.assessment_history) || [], latest = history.at(-1);
    const eligibility=precheck(fixtures.find(x=>x.case_id===cur.case_id),now().toISOString()), finalPolicy=eligibility.eligibility==='ELIGIBLE'?(latest.effective_policy||latest.policy):{eligibility:eligibility.eligibility,policy_gate:eligibility.state==='BLOCKED'?'BLOCKED':'ESCALATED',final_action:'ESCALATE_REVIEW',reason:eligibility.reason};
    db.prepare('update runs set state=?,question=?,final=?,final_policy=?,source=?,final_assessment_id=?,final_turn_index=? where id=? and state=?')
      .run('COMPLETED', JSON.stringify(q), JSON.stringify(latest.assessment), JSON.stringify(finalPolicy), latest.turn_index === 0 ? 1 : 2, latest.assessment_id, latest.turn_index, id, 'WAITING_FOR_BUYER');
    db.prepare('insert into events values(?,?,?,?,?,?)').run(eventId, id, 'USER_NO_REPLY', hash(payload), '{}', now().toISOString());
    const result = view(rec(id)); updateEventResult(eventId, payload, result); return result;
  })();
}
export const getRun = (id: string) => { const r = rec(id); if (!r) throw Error('Run not found'); return view(r); };

/** Explicit, operator initiated retry. Every attempt has a distinct event ID and is never replayed automatically. */
export async function retry(runId: string, attemptId: string, onToken?: TokenCallback) {
  const run = rec(runId); if (!run) throw Error('Run not found');
  const payload = { type: 'MANUAL_RETRY', run_id: runId, attempt_id: attemptId };
  const duplicate = priorEvent(attemptId, runId, payload); if (duplicate) return duplicate;
  if (run.state !== 'HUMAN_REVIEW') throw Error('Only HUMAN_REVIEW runs can be retried');
  const c = fixtures.find(x => x.case_id === run.case_id)!, retryAt=now().toISOString();
  const interactions = (parse(run.interactions) || []) as ConversationTurn[];
  const inp = inputFor(c, interactions, undefined, retryAt), phase = interactions.length ? `retry_reply_${interactions.length}` : 'retry_initial';
  db.transaction(() => {
    const cur = rec(runId); if (cur.state !== 'HUMAN_REVIEW') throw Error('Run changed before retry reservation');
    db.prepare('insert into events values(?,?,?,?,?,?)').run(attemptId,runId,'MANUAL_RETRY',hash(payload),'{}',retryAt);
    db.prepare("update runs set state='RETRYING',error=NULL,meta=json_set(coalesce(meta,'{}'),'$.retry_attempts',coalesce(json_extract(meta,'$.retry_attempts'),0)+1) where id=? and state='HUMAN_REVIEW'").run(runId);
  })();
  try {
    const raw=await assessor(inp,onToken), out=envelope(raw); validateSources(inp,out);
    const turnIndex=interactions.length, history=(parse(run.assessment_history)||[]) as any[];
    const checked=policy(c,out.assessment,out.decision_facts,precheck(c,retryAt)), verified=await verifyRetry(inp,out.decision_facts,checked), p=verified.policy;
    const record=makeAssessmentRecord(runId,turnIndex,attemptId,inp,raw,out,checked); await prepareVerifierFollowup(inp,out,verified,record,interactions); record.effective_policy=p; record.policy_override=p.final_action===checked.final_action?null:{kind:verified.clarification_facts?.length&&p.final_action==='CLARIFY'?'SEMANTIC_VERIFIER_FOLLOWUP':'SEMANTIC_VERIFIER',from:checked.final_action,to:p.final_action,reason:p.reason}; record.verification=verified.verification; history.push(record);
    const q=interactions.length<MAX_CLARIFICATION_ROUNDS?questionFrom(record,interactions.length+1):null;
    const exhausted=!q&&p.final_action==='CLARIFY'&&interactions.length>=MAX_CLARIFICATION_ROUNDS;
    const finalP=!q&&p.final_action==='CLARIFY'&&!exhausted?{...p,policy_gate:'ESCALATED' as const,final_action:'ESCALATE_REVIEW',reason:`No useful buyer question is available; unresolved information: ${out.assessment.missing_info.join(', ')||'clarification cannot change the next action'}.`}:selectedFinalPolicy(record,exhausted);
    const terminal=!q, initialPhase=interactions.length===0, finalTurn=turnIndex;
    const result=db.transaction(()=>{
      const cur=rec(runId);if(cur.state!=='RETRYING')throw Error('Run changed during explicit retry');
      db.prepare(`update runs set state=?,initial=case when ? then ? else initial end,initial_policy=case when ? then ? else initial_policy end,phase2_input=case when ? then phase2_input else ? end,phase2_hash=case when ? then phase2_hash else ? end,after_reply=case when ? then after_reply else ? end,after_policy=case when ? then after_policy else ? end,final=?,final_policy=?,source=?,question=?,question_id=?,assessment_history=?,final_assessment_id=?,final_turn_index=?,meta=? where id=? and state='RETRYING'`)
        .run(q?'WAITING_FOR_BUYER':'COMPLETED',initialPhase?1:0,JSON.stringify(out.assessment),initialPhase?1:0,JSON.stringify(p),initialPhase?1:0,JSON.stringify(inp),initialPhase?1:0,hash(inp),initialPhase?1:0,JSON.stringify(out.assessment),initialPhase?1:0,JSON.stringify(p),terminal?JSON.stringify(out.assessment):null,terminal?JSON.stringify(finalP):null,terminal?(initialPhase?1:2):null,q&&JSON.stringify(q),q?.question_id||null,JSON.stringify(history),terminal?record.assessment_id:null,terminal?finalTurn:null,JSON.stringify({...parse(run.meta),retry_phase:phase,retry_meta:raw.meta,explanation:out.decision_facts.explanation,verification:verified.verification,question_generation:record.followup_question_metadata||null,mode:'demo-multiturn-v1'}),runId);
      const done=view(rec(runId));updateEventResult(attemptId,payload,done);return done;
    })();return result;
  } catch(error) { recordFailure(runId,phase,error); updateEventResult(attemptId,payload,view(rec(runId))); throw error; }
}
