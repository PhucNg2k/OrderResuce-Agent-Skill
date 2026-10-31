import assert from 'node:assert/strict';
import { Agent, AgentRegistry } from '@voltagent/core';
import { MockLanguageModelV3, simulateReadableStream } from 'ai/test';
import { agent as assessor, shutdownAgentTelemetry } from '../src/agent.js';

const registry = AgentRegistry.getInstance();
const sharedObservability = registry.getGlobalObservability();
assert.ok(sharedObservability, 'application observability is registered globally');
assert.equal(
  (assessor as unknown as { getObservability(): unknown }).getObservability(),
  sharedObservability,
  'the production assessor must use the instance closed during shutdown',
);

const model = new MockLanguageModelV3({
  doStream: async () => ({
    stream: simulateReadableStream({
      chunks: [
        { type: 'stream-start', warnings: [] },
        { type: 'text-start', id: 'probe' },
        { type: 'text-delta', id: 'probe', delta: 'ok' },
        { type: 'text-end', id: 'probe' },
        {
          type: 'finish',
          finishReason: 'stop' as const,
          usage: {
            inputTokens: { total: 1, noCache: 1, cacheRead: 0, cacheWrite: 0 },
            outputTokens: { total: 1, text: 1, reasoning: 0 },
          },
        },
      ] as any,
    }),
  }),
});

const probeAgent = new Agent({ name: 'shutdown-probe', instructions: 'Answer briefly.', model });
const result = await probeAgent.streamText('local shutdown probe');
for await (const _ of result.textStream) { /* Drain the complete model stream. */ }
await result.usage;
await result.finishReason;
await shutdownAgentTelemetry();
await new Promise<void>(resolve => setImmediate(resolve));

const resources = process.getActiveResourcesInfo();
assert.deepEqual(resources.filter(resource => resource === 'Timeout'), []);
console.log(JSON.stringify({ shared_observability: true, resources }));
