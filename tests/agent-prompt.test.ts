import { test } from 'node:test';
import assert from 'node:assert/strict';
import { recommendationInstructions, PROMPT_VERSION } from '../src/agent-prompt.js';

test('prompt version changes when scheduled-slot availability interpretation changes', () => {
  assert.equal(PROMPT_VERSION, 'demo-multiturn-assessment-v1');
});

test('prompt treats an explicit feasible redelivery slot as direct availability evidence', () => {
  assert.match(recommendationInstructions, /affirmative buyer reply.*specific requested redelivery date or time.*availability/i);
  assert.match(recommendationInstructions, /within the known deadline/i);
  assert.match(recommendationInstructions, /relative dates.*case's as-of timestamp/i);
  assert.match(recommendationInstructions, /prior_buyer_question.*conversation context.*not evidence/i);
});
