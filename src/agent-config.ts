export const reasoningEfforts = ['none', 'low', 'medium', 'high', 'xhigh', 'max'] as const;
export type ReasoningEffort = typeof reasoningEfforts[number];

export function resolveReasoningEffort(value = process.env.OPENAI_REASONING_EFFORT): ReasoningEffort {
  const effort = value || 'high';
  if (!reasoningEfforts.includes(effort as ReasoningEffort)) {
    throw new Error(`Invalid OPENAI_REASONING_EFFORT: ${effort}`);
  }
  return effort as ReasoningEffort;
}
