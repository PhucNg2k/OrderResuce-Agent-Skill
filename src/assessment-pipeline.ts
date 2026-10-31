import { randomUUID } from 'node:crypto';
import { assessmentSchema, type CaseInput } from './domain.js';
import { extractEvidence, analyzeEvidence } from './agent.js';
import { createDecisionsClient, chooseHypothesis, chooseActionAndSupport, type DecisionCallRecord } from './decisions.js';
import { RUBRIC_VERSION } from './decision-rubrics.js';

export async function assessWithDecisions(input:CaseInput,onToken?:(delta:string)=>void,onCall?:(record:DecisionCallRecord)=>void){
 const started=Date.now(),assessmentId=randomUUID(),snapshotId=randomUUID(),calls:DecisionCallRecord[]=[];
 const client=createDecisionsClient();
 let stage='G1';let g1:any,g2:any,d1:any,d2:any;
 try {
 g1=await extractEvidence(input);onToken?.('Evidence extracted; selecting cause…');
 stage='D1';
 d1=await chooseHypothesis(client,snapshotId,{assessment_id:assessmentId,snapshot_id:snapshotId,assessment_as_of:input.assessment_as_of||input.failed_event.as_of,case_input:input,extracted:g1.data,decision_context:{phase:input.turn_index?'AFTER_REPLY':'INITIAL',turn_index:input.turn_index||0,clarification_rounds_remaining:Math.max(0,(input.max_clarification_rounds||0)-(input.turn_index||0)),eligibility:'UNKNOWN',policy_version:input.operational_context.policy_version}},r=>{if(!calls.some(c=>c.call_id===r.call_id))calls.push(r);onCall?.(r);});
 stage='G2';g2=await analyzeEvidence(input,g1.data,d1.choice.selected_label);onToken?.('Evidence analysis complete; selecting recommendation…');
 stage='D2';d2=await chooseActionAndSupport(client,snapshotId,{assessment_as_of:input.assessment_as_of||input.failed_event.as_of,case_input:input,extracted:g1.data,selected_hypothesis:d1.choice.selected_label,analysis:g2.data,policy_context:{attempts_used:input.attempts_used,return_state:input.return_state,deadline:input.deadline,clarification_rounds_remaining:Math.max(0,(input.max_clarification_rounds||0)-(input.turn_index||0)),verified_ops:input.operational_context.ops}},r=>{if(!calls.some(c=>c.call_id===r.call_id))calls.push(r);onCall?.(r);});
 let effectiveSupport=d2.support.selected_label,guardReason:string|null=null;
 if(effectiveSupport==='HIGH'&&g1.data.evidence.some((e:{verification:string})=>e.verification==='UNVERIFIED_REPORT')&&!g1.data.evidence.some((e:{verification:string})=>e.verification==='DIRECT_BUYER_STATEMENT'||e.verification==='VERIFIED_OPS_SIGNAL')){effectiveSupport='MEDIUM';guardReason='HIGH support capped because extracted evidence has no direct buyer or verified Ops source.';}
 const assessment=assessmentSchema.parse({evidence:g1.data.evidence,hypothesis:d1.choice.selected_label,confidence:effectiveSupport,missing_info:g2.data.missing_info,question_key:d2.action.selected_label==='CLARIFY'?g2.data.question_key:null,candidate_action:d2.action.selected_label});
 return {assessment,decision_facts:{...g1.data.decision_facts,explanation:g2.data.explanation,question_text:d2.action.selected_label==='CLARIFY'?g2.data.question_text:null},meta:{pipeline_version:'decisions-v1',rubric_version:RUBRIC_VERSION,assessment_id:assessmentId,snapshot_id:snapshotId,latency_ms:Date.now()-started,generation:{G1:g1.meta,G2:g2.meta},decisions:{hypothesis:d1.choice,support:d2.support,action:d2.action,raw_support_choice:d2.support.selected_label,effective_support_level:effectiveSupport,support_guard_reason:guardReason,records:calls}}};
 } catch(error) {Object.assign(error instanceof Error?error:new Error(String(error)),{partialPipeline:{stage,assessment_id:assessmentId,snapshot_id:snapshotId,g1:g1?.data||null,d1:d1?.choice||null,g2:g2?.data||null,decision_records:calls}});throw error;}
}
