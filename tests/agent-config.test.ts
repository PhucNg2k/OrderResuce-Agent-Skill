import { test } from 'node:test';
import assert from 'node:assert/strict';
import { resolveReasoningEffort } from '../src/agent-config.js';

test('reasoning defaults to high and accepts supported OpenAI effort values', () => {
  assert.equal(resolveReasoningEffort(undefined), 'high');
  assert.equal(resolveReasoningEffort('medium'), 'medium');
  assert.equal(resolveReasoningEffort('max'), 'max');
});

test('unsupported reasoning effort fails before provider request', () => {
  assert.throws(() => resolveReasoningEffort('turbo'), /OPENAI_REASONING_EFFORT/);
});
