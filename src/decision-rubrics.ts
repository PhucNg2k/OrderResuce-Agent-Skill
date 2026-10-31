import { candidates, hypotheses } from './domain.js';

export const RUBRIC_VERSION = 'order-rescue-decisions-v1';
export const HYPOTHESIS_CHOICES = [
  { value: 'AVAILABILITY_ISSUE', description: 'Evidence supports inability to receive at the failed attempt.' },
  { value: 'ADDRESS_ISSUE', description: 'Evidence supports unclear details or access at the registered location.' },
  { value: 'CONTACT_ISSUE', description: 'Evidence supports an unusable communication channel.' },
  { value: 'BUYER_INTENT_ISSUE', description: 'Evidence supports unwillingness to accept or continue receiving.' },
  { value: 'PAYMENT_ISSUE', description: 'Evidence supports payment as a barrier; COD alone is insufficient.' },
  { value: 'LOGISTICS_ISSUE', description: 'Evidence supports a concrete operational cause.' },
  { value: 'UNKNOWN_CAUSE', description: 'Cause is unknown, conflicting, or not distinguishable from the sources.' },
] as const satisfies ReadonlyArray<{value:typeof hypotheses[number];description:string}>;
export const ACTION_CHOICES = [
  { value:'CLARIFY', description:'A permitted buyer-known gap can change the recommendation and clarification budget remains.' },
  { value:'STANDARD_REATTEMPT', description:'Current intent, feasible receiving arrangement, and applicable prerequisites are supported.' },
  { value:'HOLD_DISRUPTION', description:'A structured verified active disruption requires reassessment.' },
  { value:'ESCALATE_REVIEW', description:'A blocker, conflict, refusal, exhausted clarification, or unsupported path requires human review.' },
  { value:'NO_ACTION', description:'Compatibility label only; no business path currently permits this recommendation.' },
] as const satisfies ReadonlyArray<{value:typeof candidates[number];description:string}>;
export const SUPPORT_CHOICES = [
  { value:'LOW', description:'Status-only, unknown cause, vague evidence, or material conflict.' },
  { value:'MEDIUM', description:'Specific relevant evidence exists but is indirect or unverified.' },
  { value:'HIGH', description:'Direct buyer evidence confirms the cause, or a scoped verified Ops signal supports it, without material conflict. Courier-only reports cannot be HIGH.' },
] as const;
