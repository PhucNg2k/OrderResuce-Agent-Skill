import Database from 'better-sqlite3';
import {test} from 'node:test';import assert from 'node:assert/strict';import {mkdtempSync,rmSync} from 'node:fs';import {tmpdir} from 'node:os';import path from 'node:path';
const dir=mkdtempSync(path.join(tmpdir(),'rescue-'));process.env.DB_PATH=path.join(dir,'test.sqlite');process.env.NODE_ENV='test';process.env.ORDER_RESCUE_TEST_NOW='2026-10-25T12:00:00.000Z';
const h=await import('../src/harness.js');const {shutdownAgentTelemetry}=await import('../src/agent.js');let calls=0;const output=(reply=false)=>({assessment:{evidence:[{source_ref:'SYN-01-NOTE',fact:'A family member reports buyer was at work; not buyer verified.',verification:'UNVERIFIED_REPORT'}],hypothesis:'AVAILABILITY_ISSUE',confidence:'MEDIUM',missing_info:['CURRENT_BUYER_INTENT','RECEIVING_AVAILABILITY'],question_key:'CONFIRM_INTENT',candidate_action:'CLARIFY'},decision_facts:{intent:'UNKNOWN',availability:'UNKNOWN',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',supporting_evidence:[],explanation:'Unverified report only.',question_text:'Lần trước bạn gặp trở ngại gì và hiện có thể nhận ở địa điểm cũ khi nào?'} });
test('reply flow snapshots both phases, final exact copy, duplicate idempotency and payload conflict',async()=>{h.setAssessorForTests(async(input)=>{calls++;return input.runtime_context.length?{...output(),assessment:{...output().assessment,candidate_action:'ESCALATE_REVIEW',question_key:null},decision_facts:{...output().decision_facts,question_text:null}}:output()});const r=await h.start('SYN-01');assert.equal(r.state,'WAITING_FOR_BUYER');const q=r.question_id;const done=await h.reply(r.id,q,'I still want it; unknown schedule.','evt-1');assert.equal(calls,2);assert.equal(done.state,'COMPLETED');assert.deepEqual(done.final,done.after_reply);assert.deepEqual(done.final_policy,done.after_policy);assert.ok(done.phase2_input);assert.equal(done.phase2_hash.length,64);const dup=await h.reply(r.id,q,'I still want it; unknown schedule.','evt-1');assert.deepEqual(dup.final,done.final);await assert.rejects(()=>h.reply(r.id,q,'changed','evt-1'),/PAYLOAD_CONFLICT/)});
test('USER_NO_REPLY copies initial and never makes second assessment',async()=>{calls=0;h.setAssessorForTests(async()=>{calls++;return output()});const r=await h.start('SYN-01');const done=h.noReply(r.id,r.question_id,'evt-nr');assert.equal(calls,1);assert.equal(done.after_reply,null);assert.equal(done.after_policy,null);assert.deepEqual(done.final,done.initial);assert.deepEqual(done.final_policy,done.initial_policy);assert.equal(done.source,1);assert.ok(done.events.some((event:any)=>event.event_type==='USER_NO_REPLY'));assert.deepEqual(h.noReply(r.id,r.question_id,'evt-nr').final,done.final)});
test('precheck persists lifecycle review/block without calling assessor',async()=>{calls=0;h.setAssessorForTests(async()=>{calls++;throw Error('must not run')});const r=await h.start('SYN-04');assert.equal(calls,0);assert.equal(r.state,'BLOCKED');assert.ok(r.precheck)});
test('expired deadline is checked against the current assessment time, not the original failure timestamp',async()=>{
  calls=0;h.setAssessorForTests(async()=>{calls++;return output()});process.env.ORDER_RESCUE_TEST_NOW='2026-10-31T03:00:00.000Z';
  const expired=await h.start('SYN-01');
  assert.equal(calls,0);assert.equal(expired.state,'BLOCKED');assert.match(expired.precheck.reason,/deadline has passed/i);
  process.env.ORDER_RESCUE_TEST_NOW='2026-10-25T12:00:00.000Z';
});
test('source provenance mismatch persists HUMAN_REVIEW without invented assessment',async()=>{h.setAssessorForTests(async()=>({ ...output(),assessment:{...output().assessment,evidence:[{source_ref:'SYN-01-NOTE',fact:'claimed ops verified',verification:'VERIFIED_OPS_SIGNAL'}]}}));const r=await h.start('SYN-01');assert.equal(r.state,'HUMAN_REVIEW');assert.equal(r.initial,null);assert.ok(r.error)});
test.after(async()=>{await shutdownAgentTelemetry();h.closeHarnessDatabase();rmSync(dir,{recursive:true,force:true})});

test('model errors persist review without fabricated output',async()=>{h.setAssessorForTests(async()=>{throw new Error('injected provider failure')});const r=await h.start('SYN-01');assert.equal(r.state,'HUMAN_REVIEW');assert.equal(r.initial,null);assert.equal(r.final,null);assert.match(r.error,/injected provider failure/)});
test('initial assessment forwards draft deltas but returns only validated policy result',async()=>{const chunks:string[]=[];h.setAssessorForTests(async(_input,onToken)=>{onToken?.('{"assessment":');return output()});const r=await h.start('SYN-01',chunk=>chunks.push(chunk));assert.deepEqual(chunks,['{"assessment":']);assert.equal(r.state,'WAITING_FOR_BUYER');assert.equal(r.initial_policy.final_action,'CLARIFY');assert.equal(r.final,null)});

test('affirmative reply with a specific feasible slot permits sourced reattempt and appears in history',async()=>{
  calls=0;
  let priorQuestion:string|undefined;
  h.setVerifierForTests(async()=>({checks:['intent','availability','address','refusal'].map(fact_key=>({fact_key,verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'có, mai giao lại nhe ạ',explanation:'Direct source supports proposed fact.'}))}));
  h.setAssessorForTests(async(input)=>{
    calls++;
    if(input.runtime_context.length===0)return output();
    priorQuestion=(input as any).prior_buyer_question?.question_text;
    const replyRef='SYN-01-REPLY';
    const noteRef='SYN-01-NOTE';
    const replyText=input.sources[replyRef].text;
    return {
      assessment:{
        evidence:[
          {source_ref:noteRef,fact:'Earlier absence was reported by a family member.',verification:'UNVERIFIED_REPORT'},
          {source_ref:replyRef,fact:'Buyer agrees to the requested redelivery slot.',verification:'DIRECT_BUYER_STATEMENT'},
        ],
        hypothesis:'AVAILABILITY_ISSUE',confidence:'MEDIUM',missing_info:[],question_key:'CONFIRM_INTENT',candidate_action:'STANDARD_REATTEMPT',
      },
      decision_facts:{
        intent:'CONFIRMED',availability:'CONFIRMED',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',
        supporting_evidence:[
          {fact_key:'intent',source_ref:replyRef,supporting_text:replyText},
          {fact_key:'availability',source_ref:replyRef,supporting_text:replyText},
        ],
        explanation:'The buyer directly confirms intent and a feasible delivery slot.',question_text:null,
      },
    };
  });
  const first=await h.start('SYN-01');
  assert.equal(first.initial_policy.final_action,'CLARIFY');
  const done=await h.reply(first.id,first.question_id,'có, mai giao lại nhe ạ','evt-slot');
  assert.equal(calls,2);
  assert.equal(done.state,'COMPLETED');
  assert.equal(priorQuestion,JSON.parse(first.question).question_text);
  assert.equal(done.after_policy.final_action,'STANDARD_REATTEMPT');
  assert.equal(done.final_policy.final_action,'STANDARD_REATTEMPT');
  assert.ok(done.events.some((event:any)=>event.event_type==='BUYER_REPLY'));
});

function clarificationOutput(questionText:string, candidate:'CLARIFY'|'ESCALATE_REVIEW'='CLARIFY', replyRef?:string) {
  const evidence = replyRef
    ? [{source_ref:replyRef,fact:'Buyer reply is included for reassessment.',verification:'DIRECT_BUYER_STATEMENT'}]
    : [{source_ref:'SYN-01-NOTE',fact:'Third-party note remains unverified.',verification:'UNVERIFIED_REPORT'}];
  const support:any[] = [];
  return {
    assessment:{evidence,hypothesis:'AVAILABILITY_ISSUE',confidence:'MEDIUM',missing_info:candidate==='CLARIFY'?['RECEIVING_AVAILABILITY']:[],question_key:candidate==='CLARIFY'?'CONFIRM_INTENT':null,candidate_action:candidate},
    decision_facts:{intent:'UNKNOWN',availability:'UNKNOWN',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',supporting_evidence:support,explanation:'A reassessment of the available conversation.',question_text:candidate==='CLARIFY'?questionText:null},
  };
}

test('demo-multiturn allows two total questions then ends in review without a third',async()=>{
  calls=0;
  h.setAssessorForTests(async input=>{
    calls++;
    if(calls===1)return clarificationOutput('When could someone receive it?');
    const replyRef=input.runtime_context.at(-1)!.source_ref;
    return clarificationOutput(calls===2?'Can someone receive at that time?':'Please share any other detail?', 'CLARIFY', replyRef);
  });
  const first=await h.start('SYN-01');
  assert.equal(first.state,'WAITING_FOR_BUYER');
  const after1=await h.reply(first.id,first.question_id,'I still want the parcel.','multi-r1');
  assert.equal(after1.state,'WAITING_FOR_BUYER');
  assert.equal(after1.interactions.length,1);
  const after2=await h.reply(first.id,after1.question_id,'I do not know when anyone will be there.','multi-r2');
  assert.equal(calls,3);
  assert.equal(after2.state,'COMPLETED');
  assert.equal(after2.interactions.length,2);
  assert.equal(after2.interactions.filter((x:any)=>x.status==='PENDING').length,0);
  assert.equal(after2.assessment_history.length,3);
  assert.equal(after2.final_turn_index,2);
  assert.equal(after2.final_assessment_id,after2.assessment_history[2].assessment_id);
  assert.equal(after2.final_policy.final_action,'ESCALATE_REVIEW');
  await assert.rejects(()=>h.reply(first.id,after2.question_id,'third reply','multi-r3'),/Mismatched/);
});

test('demo-multiturn early stop selects the first reply assessment',async()=>{
  calls=0;
  h.setAssessorForTests(async input=>{
    calls++;
    if(calls===1)return clarificationOutput('When can someone receive it?');
    const replyRef=input.runtime_context.at(-1)!.source_ref;
    return clarificationOutput('', 'ESCALATE_REVIEW', replyRef);
  });
  const first=await h.start('SYN-01');
  const done=await h.reply(first.id,first.question_id,'Please send this to a different address.','early-stop');
  assert.equal(calls,2);
  assert.equal(done.state,'COMPLETED');
  assert.equal(done.final_turn_index,1);
  assert.deepEqual(done.final,done.after_reply);
  assert.deepEqual(done.final_policy,done.after_policy);
  assert.equal(done.question,null);
});

test('no-reply after round one selects exact latest assessment and policy without another model call',async()=>{
  calls=0;
  h.setAssessorForTests(async input=>{
    calls++;
    if(calls===1)return clarificationOutput('When can someone receive it?');
    return clarificationOutput('Can someone receive in the evening?', 'CLARIFY', input.runtime_context.at(-1)!.source_ref);
  });
  const first=await h.start('SYN-01');
  const after1=await h.reply(first.id,first.question_id,'I want it, but I am away during the day.','nr-after-r1');
  assert.equal(after1.state,'WAITING_FOR_BUYER');
  const latest=after1.assessment_history[1];
  const done=h.noReply(first.id,after1.question_id,'nr-final');
  assert.equal(calls,2);
  assert.equal(done.state,'COMPLETED');
  assert.deepEqual(done.final,latest.assessment);
  assert.deepEqual(done.final_policy,latest.policy);
  assert.equal(done.final_assessment_id,latest.assessment_id);
  assert.equal(done.final_turn_index,1);
  assert.equal(JSON.parse(done.question).status,'NO_REPLY');
});


test('semantic verifier uncertainty blocks retry and asks one existing buyer-resolvable follow-up',async()=>{
  calls=0;
  h.setAssessorForTests(async(input)=>{
    if(!input.runtime_context.length)return output();
    const ref=input.runtime_context.at(-1)!.source_ref, text=input.sources[ref].text;
    return {assessment:{evidence:[{source_ref:ref,fact:'Buyer reply received.',verification:'DIRECT_BUYER_STATEMENT'}],hypothesis:'AVAILABILITY_ISSUE',confidence:'HIGH',missing_info:[],question_key:'CONFIRM_INTENT',candidate_action:'STANDARD_REATTEMPT'},decision_facts:{intent:'CONFIRMED',availability:'CONFIRMED',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',supporting_evidence:[{fact_key:'intent',source_ref:ref,supporting_text:text},{fact_key:'availability',source_ref:ref,supporting_text:text}],explanation:'Buyer facts asserted.',question_text:'Will you or someone else be available to receive it tomorrow morning?'}};
  });
  h.setVerifierForTests(async()=>({checks:[{fact_key:'intent',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'Yes',explanation:'Intent.'},{fact_key:'availability',verdict:'UNCERTAIN',source_ref:null,supporting_text:null,explanation:'No clear time.'},{fact_key:'address',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'Yes',explanation:'No change.'},{fact_key:'refusal',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'Yes',explanation:'No refusal.'}]}));
  const first=await h.start('SYN-01');
  const waiting=await h.reply(first.id,first.question_id,'Yes, I still want it.','verify-uncertain');
  assert.equal(waiting.state,'WAITING_FOR_BUYER');
  assert.equal(JSON.parse(waiting.question).question_text,'Will you or someone else be available to receive it tomorrow morning?');
  assert.equal(waiting.final,null);
  assert.equal(waiting.after_policy.final_action,'CLARIFY');
  assert.equal(waiting.assessment_history[1].assessment.candidate_action,'STANDARD_REATTEMPT');
  assert.equal(waiting.assessment_history[1].effective_policy.final_action,'CLARIFY');
  assert.equal(waiting.assessment_history[1].verification.checks.find((x:any)=>x.fact_key==='availability').verdict,'UNCERTAIN');
});

test('neutral absence of address change or refusal does not block supported retry facts',async()=>{
  h.setAssessorForTests(async input=>{
    if(!input.runtime_context.length)return output();
    const ref=input.runtime_context.at(-1)!.source_ref,text=input.sources[ref].text;
    return {assessment:{evidence:[{source_ref:ref,fact:'Buyer confirms a feasible receiving slot.',verification:'DIRECT_BUYER_STATEMENT'}],hypothesis:'AVAILABILITY_ISSUE',confidence:'HIGH',missing_info:[],question_key:null,candidate_action:'STANDARD_REATTEMPT'},decision_facts:{intent:'CONFIRMED',availability:'CONFIRMED',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',supporting_evidence:[{fact_key:'intent',source_ref:ref,supporting_text:text},{fact_key:'availability',source_ref:ref,supporting_text:text}],explanation:'Intent and a feasible receiving slot are directly supported.',question_text:null}};
  });
  h.setVerifierForTests(async()=>({checks:[
    {fact_key:'intent',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'Yes, tomorrow morning works.',explanation:'Intent.'},
    {fact_key:'availability',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'Yes, tomorrow morning works.',explanation:'Receiving slot.'},
    {fact_key:'address',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No address change request appears in the available conversation.'},
    {fact_key:'refusal',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No refusal appears in the available conversation.'},
  ]}));
  const first=await h.start('SYN-01');
  const done=await h.reply(first.id,first.question_id,'Yes, tomorrow morning works.','verify-not-present');
  assert.equal(done.state,'COMPLETED');
  assert.equal(done.final_policy.final_action,'STANDARD_REATTEMPT');
});

test('verifier uncertainty generates a distinct follow-up when the assessor supplied none',async()=>{
  let generated=0;
  h.setQuestionGeneratorForTests(async(_input:any,facts:string[])=>{
    generated++;
    assert.deepEqual(facts,['availability']);
    return {question_key:'CONFIRM_INTENT',question_text:'Will you or someone else be available to receive it tomorrow morning?',metadata:{version:'stub-question-v1'}};
  });
  h.setAssessorForTests(async input=>{
    if(!input.runtime_context.length)return output();
    const ref=input.runtime_context.at(-1)!.source_ref,text=input.sources[ref].text;
    return {assessment:{evidence:[{source_ref:ref,fact:'Buyer reply received.',verification:'DIRECT_BUYER_STATEMENT'}],hypothesis:'AVAILABILITY_ISSUE',confidence:'HIGH',missing_info:[],question_key:null,candidate_action:'STANDARD_REATTEMPT'},decision_facts:{intent:'CONFIRMED',availability:'CONFIRMED',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',supporting_evidence:[{fact_key:'intent',source_ref:ref,supporting_text:text},{fact_key:'availability',source_ref:ref,supporting_text:text}],explanation:'The reply proposes a slot but does not clearly confirm a receiver.',question_text:null}};
  });
  h.setVerifierForTests(async()=>({checks:[
    {fact_key:'intent',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'Yes, tomorrow morning.',explanation:'Intent.'},
    {fact_key:'availability',verdict:'UNCERTAIN',source_ref:'SYN-01-REPLY',supporting_text:'Yes, tomorrow morning.',explanation:'A receiver is not explicit.'},
    {fact_key:'address',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No address change request appears.'},
    {fact_key:'refusal',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No refusal appears.'},
  ]}));
  const first=await h.start('SYN-01');
  const waiting=await h.reply(first.id,first.question_id,'Yes, tomorrow morning.','verify-generate-question');
  const last=waiting.assessment_history.at(-1);
  assert.equal(generated,1);
  assert.equal(waiting.state,'WAITING_FOR_BUYER');
  assert.equal(JSON.parse(waiting.question).question_text,'Will you or someone else be available to receive it tomorrow morning?');
  assert.equal(last.assessment.question_key,null);
  assert.equal(last.internal_facts.question_text,null);
  assert.equal(last.followup_question.question_text,JSON.parse(waiting.question).question_text);
  assert.equal(last.followup_question_metadata.version,'stub-question-v1');
  assert.equal(last.effective_policy.final_action,'CLARIFY');
  assert.equal(last.verification.checks.find((x:any)=>x.fact_key==='availability').verdict,'UNCERTAIN');
  h.setQuestionGeneratorForTests();
});

test('follow-up generation failure leaves the reply in human review without a fabricated question',async()=>{
  h.setQuestionGeneratorForTests(async()=>{throw new Error('injected follow-up generation failure')});
  h.setAssessorForTests(async input=>{
    if(!input.runtime_context.length)return output();
    const ref=input.runtime_context.at(-1)!.source_ref,text=input.sources[ref].text;
    return {assessment:{evidence:[{source_ref:ref,fact:'Buyer reply received.',verification:'DIRECT_BUYER_STATEMENT'}],hypothesis:'AVAILABILITY_ISSUE',confidence:'HIGH',missing_info:[],question_key:null,candidate_action:'STANDARD_REATTEMPT'},decision_facts:{intent:'CONFIRMED',availability:'CONFIRMED',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',supporting_evidence:[{fact_key:'intent',source_ref:ref,supporting_text:text},{fact_key:'availability',source_ref:ref,supporting_text:text}],explanation:'Availability remains uncertain.',question_text:null}};
  });
  h.setVerifierForTests(async()=>({checks:[
    {fact_key:'intent',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'Tomorrow morning.',explanation:'Intent.'},
    {fact_key:'availability',verdict:'UNCERTAIN',source_ref:null,supporting_text:null,explanation:'Receiver is not explicit.'},
    {fact_key:'address',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No address change request appears.'},
    {fact_key:'refusal',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No refusal appears.'},
  ]}));
  const first=await h.start('SYN-01');
  await assert.rejects(()=>h.reply(first.id,first.question_id,'Tomorrow morning.','verify-question-error'),/injected follow-up generation failure/);
  const failed=h.getRun(first.id);
  assert.equal(failed.state,'HUMAN_REVIEW');
  assert.equal(failed.final,null);
  assert.equal(failed.question,first.question);
  h.setQuestionGeneratorForTests();
});

test('explicit retry can ask the verifier follow-up after a prior reply failure',async()=>{
  h.setQuestionGeneratorForTests(async()=>({question_key:'CONFIRM_INTENT',question_text:'Will you or someone else be available tomorrow morning?',metadata:{version:'retry-question-stub-v1'}}));
  h.setAssessorForTests(async input=>{
    if(!input.runtime_context.length)return output();
    throw new Error('injected reply assessment failure');
  });
  const first=await h.start('SYN-01');
  await assert.rejects(()=>h.reply(first.id,first.question_id,'Tomorrow morning works.','retry-q-first-reply'),/injected reply assessment failure/);
  const review=h.getRun(first.id);
  assert.equal(review.state,'HUMAN_REVIEW');
  h.setAssessorForTests(async input=>{
    const ref=input.runtime_context.at(-1)!.source_ref,text=input.sources[ref].text;
    return {assessment:{evidence:[{source_ref:ref,fact:'Buyer proposes a delivery slot.',verification:'DIRECT_BUYER_STATEMENT'}],hypothesis:'AVAILABILITY_ISSUE',confidence:'HIGH',missing_info:[],question_key:null,candidate_action:'STANDARD_REATTEMPT'},decision_facts:{intent:'CONFIRMED',availability:'CONFIRMED',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',supporting_evidence:[{fact_key:'intent',source_ref:ref,supporting_text:text},{fact_key:'availability',source_ref:ref,supporting_text:text}],explanation:'The buyer proposes a slot but availability remains uncertain.',question_text:null}};
  });
  h.setVerifierForTests(async()=>({checks:[
    {fact_key:'intent',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY',supporting_text:'Tomorrow morning works.',explanation:'Intent.'},
    {fact_key:'availability',verdict:'UNCERTAIN',source_ref:null,supporting_text:null,explanation:'Receiver is not explicit.'},
    {fact_key:'address',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No address change request appears.'},
    {fact_key:'refusal',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No refusal appears.'},
  ]}));
  const waiting=await h.retry(first.id,'retry-verifier-question');
  assert.equal(waiting.state,'WAITING_FOR_BUYER');
  assert.equal(JSON.parse(waiting.question).question_text,'Will you or someone else be available tomorrow morning?');
  assert.equal(waiting.assessment_history.at(-1).followup_question_source,'SEMANTIC_VERIFIER_FOLLOWUP');
  h.setQuestionGeneratorForTests();
});

test('verifier uncertainty does not generate a third question after the two-question budget',async()=>{
  let generated=0;calls=0;
  h.setQuestionGeneratorForTests(async()=>{generated++;return {question_key:'CONFIRM_INTENT',question_text:'A third question must not be asked.'}});
  h.setAssessorForTests(async input=>{
    calls++;
    if(calls===1)return clarificationOutput('When can someone receive it?');
    const ref=input.runtime_context.at(-1)!.source_ref,text=input.sources[ref].text;
    if(calls===2)return clarificationOutput('Can someone receive at that time?','CLARIFY',ref);
    return {assessment:{evidence:[{source_ref:ref,fact:'Buyer reply received.',verification:'DIRECT_BUYER_STATEMENT'}],hypothesis:'AVAILABILITY_ISSUE',confidence:'HIGH',missing_info:[],question_key:null,candidate_action:'STANDARD_REATTEMPT'},decision_facts:{intent:'CONFIRMED',availability:'CONFIRMED',cod_readiness:'UNKNOWN',address:'UNKNOWN',refusal:'NONE',supporting_evidence:[{fact_key:'intent',source_ref:ref,supporting_text:text},{fact_key:'availability',source_ref:ref,supporting_text:text}],explanation:'The reply remains unclear on a receiver.',question_text:null}};
  });
  h.setVerifierForTests(async()=>({checks:[
    {fact_key:'intent',verdict:'SUPPORTED',source_ref:'SYN-01-REPLY-2',supporting_text:'I still want it.',explanation:'Intent.'},
    {fact_key:'availability',verdict:'UNCERTAIN',source_ref:null,supporting_text:null,explanation:'No receiver is confirmed.'},
    {fact_key:'address',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No address change request appears.'},
    {fact_key:'refusal',verdict:'NOT_PRESENT',source_ref:null,supporting_text:null,explanation:'No refusal appears.'},
  ]}));
  const first=await h.start('SYN-01');
  const after1=await h.reply(first.id,first.question_id,'I still want it.','verify-budget-r1');
  assert.equal(after1.state,'WAITING_FOR_BUYER');
  const final=await h.reply(first.id,after1.question_id,'I am not sure.','verify-budget-r2');
  assert.equal(calls,3);
  assert.equal(generated,0);
  assert.equal(final.interactions.length,2);
  assert.equal(final.question,null);
  assert.equal(final.final_policy.final_action,'ESCALATE_REVIEW');
  h.setQuestionGeneratorForTests();
});


test('accepted reply and processing state persist before assessor failure; stale completion cannot replace review',async()=>{
  let release!:()=>void; let entered!:()=>void;
  const enteredPromise=new Promise<void>(resolve=>{entered=resolve});
  const gate=new Promise<void>(resolve=>{release=resolve});
  h.setAssessorForTests(async input=>{if(input.runtime_context.length){entered();await gate;throw new Error('late provider failure')}return output()});
  const first=await h.start('SYN-01');
  const pending=h.reply(first.id,first.question_id,'I still want it.','persist-before-call');
  await enteredPromise;
  const processing=h.getRun(first.id);
  assert.equal(processing.state,'ASSESSING_REPLY');
  assert.equal(processing.interactions[0].reply_text,'I still want it.');
  release();
  await assert.rejects(()=>pending,/late provider failure/);
  const failed=h.getRun(first.id);
  assert.equal(failed.state,'HUMAN_REVIEW');
  assert.equal(failed.interactions[0].reply_text,'I still want it.');
  const replay=await h.reply(first.id,first.question_id,'I still want it.','persist-before-call');
  assert.equal(replay.state,'HUMAN_REVIEW');
});

test('unsupported model supporting text is preserved and rejected instead of replaced by source text', async () => {
  h.setAssessorForTests(async () => ({
    ...output(),
    decision_facts: { ...output().decision_facts, intent: 'CONFIRMED', supporting_evidence: [{ fact_key: 'intent', source_ref: 'SYN-01-NOTE', supporting_text: 'I can receive the parcel tomorrow.' }] },
  }));
  const run = await h.start('SYN-01');
  assert.equal(run.state, 'HUMAN_REVIEW');
  assert.match(run.error, /supporting text is not present/);
  assert.equal(run.initial, null);
});

test('manual retry is explicit, recorded with a distinct attempt identity, and idempotent',async()=>{
  calls=0;
  h.setAssessorForTests(async()=>{calls++;throw new Error('first call failed')});
  const failed=await h.start('SYN-01');
  assert.equal(failed.state,'HUMAN_REVIEW');assert.equal(calls,1);
  h.setAssessorForTests(async()=>{calls++;return clarificationOutput('When could someone receive it?')});
  const retried=await h.retry(failed.id,'retry-attempt-1');
  assert.equal(calls,2);assert.equal(retried.state,'WAITING_FOR_BUYER');
  assert.ok(retried.events.some((x:any)=>x.event_type==='MANUAL_RETRY'));
  const duplicate=await h.retry(failed.id,'retry-attempt-1');
  assert.equal(calls,2);assert.deepEqual(duplicate.question,retried.question);
  await assert.rejects(()=>h.retry(failed.id,'retry-attempt-2'),/Only HUMAN_REVIEW/);
});

test('new demo runs preserve older run history',async()=>{
  h.setAssessorForTests(async()=>clarificationOutput('When could someone receive it?'));
  const one=await h.start('SYN-01'),two=await h.start('SYN-01');
  assert.notEqual(one.id,two.id);
  assert.equal(h.getRun(one.id).id,one.id);
  assert.equal(h.getRun(two.id).id,two.id);
});


test('late retry failure cannot overwrite a newer terminal run state',async()=>{
  h.setAssessorForTests(async()=>{throw new Error('initial failure')});
  const failed=await h.start('SYN-01');
  let entered!:()=>void,release!:()=>void;
  const enteredCall=new Promise<void>(resolve=>{entered=resolve}), gate=new Promise<void>(resolve=>{release=resolve});
  h.setAssessorForTests(async()=>{entered();await gate;throw new Error('late retry failure')});
  const pending=h.retry(failed.id,'retry-stale-guard');await enteredCall;
  const db=new Database(process.env.DB_PATH!);
  db.prepare("update runs set state='COMPLETED',final='{}',final_policy='{}',source=1 where id=?").run(failed.id);db.close();
  release();await assert.rejects(()=>pending,/late retry failure/);
  const current=h.getRun(failed.id);assert.equal(current.state,'COMPLETED');
  assert.equal(current.error,null);
  assert.equal(current.events.find((x:any)=>x.event_type==='MANUAL_RETRY')!==undefined,true);
});

test('explicit buyer refusal cannot be turned into another clarification by the model',async()=>{
  h.setAssessorForTests(async(input)=>{if(!input.runtime_context.length)return output();const ref=input.runtime_context.at(-1)!.source_ref,text=input.sources[ref].text;return {...output(),assessment:{...output().assessment,candidate_action:'CLARIFY'},decision_facts:{...output().decision_facts,intent:'REFUSED',refusal:'DIRECT',supporting_evidence:[{fact_key:'intent',source_ref:ref,supporting_text:text},{fact_key:'refusal',source_ref:ref,supporting_text:text}]}}});
  const first=await h.start('SYN-01');const run=await h.reply(first.id,first.question_id,'I do not want it.','refusal-clarify');
  assert.equal(run.state,'COMPLETED');
  assert.equal(run.final_policy.final_action,'ESCALATE_REVIEW');
  assert.equal(run.question,null);
});

test('wrong active question ID is rejected without another model call or state transition',async()=>{
  calls=0;h.setAssessorForTests(async()=>{calls++;return output()});
  const run=await h.start('SYN-01');
  await assert.rejects(()=>h.reply(run.id,'stale-question','A synthetic reply.','wrong-question'),/Mismatched/);
  assert.equal(calls,1);assert.equal(h.getRun(run.id).state,'WAITING_FOR_BUYER');
});
