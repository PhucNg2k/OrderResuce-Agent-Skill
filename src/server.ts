import 'dotenv/config';
import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import { streamSSE } from 'hono/streaming';
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import { listCases, start, reply, noReply, getRun, retry, closeHarnessDatabase } from './harness.js';
import { shutdownAgentTelemetry } from './agent.js';

export const app = new Hono();

app.get('/healthz', c => c.json({ status: 'ok', data_mode: 'synthetic-demo' }));

async function sendToken(stream: { writeSSE: (event: { event: string; data: string }) => Promise<void> }, delta: string) {
  await stream.writeSSE({ event: 'token', data: JSON.stringify({ delta }) });
}

app.get('/api/cases', c => c.json(listCases()));

app.post('/api/runs', async c => {
  try { return c.json(await start((await c.req.json()).case_id)); }
  catch (e) { return c.json({ error: String(e) }, 400); }
});

app.post('/api/runs/stream', async c => {
  const { case_id } = await c.req.json();
  return streamSSE(c, async stream => {
    let writes = Promise.resolve();
    try {
      await stream.writeSSE({ event: 'stage', data: JSON.stringify({ stage: 'assessing' }) });
      const result = await start(case_id, delta => { writes = writes.then(() => sendToken(stream, delta)); });
      await writes;
      await stream.writeSSE({ event: 'result', data: JSON.stringify(result) });
    } catch (e) {
      await writes;
      await stream.writeSSE({ event: 'error', data: JSON.stringify({ message: String(e) }) });
    }
  });
});

app.get('/api/runs/:id', c => {
  try { return c.json(getRun(c.req.param('id'))); }
  catch (e) { return c.json({ error: String(e) }, 404); }
});

app.post('/api/runs/:id/replies', async c => {
  try {
    const b = await c.req.json();
    return c.json(await reply(c.req.param('id'), b.question_id, b.text, b.event_id || crypto.randomUUID()));
  } catch (e) { return c.json({ error: String(e) }, 409); }
});

app.post('/api/runs/:id/replies/stream', async c => {
  const b = await c.req.json();
  return streamSSE(c, async stream => {
    let writes = Promise.resolve();
    try {
      await stream.writeSSE({ event: 'stage', data: JSON.stringify({ stage: 'assessing_reply' }) });
      const result = await reply(c.req.param('id'), b.question_id, b.text, b.event_id || crypto.randomUUID(), delta => {
        writes = writes.then(() => sendToken(stream, delta));
      });
      await writes;
      await stream.writeSSE({ event: 'result', data: JSON.stringify(result) });
    } catch (e) {
      await writes;
      await stream.writeSSE({ event: 'error', data: JSON.stringify({ message: String(e) }) });
      try { await stream.writeSSE({ event: 'result', data: JSON.stringify(getRun(c.req.param('id'))) }); }
      catch { /* The run may not exist. */ }
    }
  });
});

app.post('/api/runs/:id/retry/stream', async c => {
  const b = await c.req.json();
  return streamSSE(c, async stream => {
    let writes = Promise.resolve();
    try {
      await stream.writeSSE({ event: 'stage', data: JSON.stringify({ stage: 'manual_retry' }) });
      const result = await retry(c.req.param('id'), b.attempt_id || crypto.randomUUID(), delta => { writes = writes.then(() => sendToken(stream, delta)); });
      await writes; await stream.writeSSE({ event: 'result', data: JSON.stringify(result) });
    } catch (e) {
      await writes; await stream.writeSSE({ event: 'error', data: JSON.stringify({ message: String(e) }) });
      try { await stream.writeSSE({ event: 'result', data: JSON.stringify(getRun(c.req.param('id'))) }); } catch { /* Unknown run. */ }
    }
  });
});

app.post('/api/runs/:id/no-reply', async c => {
  try {
    const b = await c.req.json();
    return c.json(noReply(c.req.param('id'), b.question_id, b.event_id || crypto.randomUUID()));
  } catch (e) { return c.json({ error: String(e) }, 409); }
});

app.get('*', c => c.html(fs.readFileSync(new URL('../public/index.html', import.meta.url), 'utf8')));
const port = Number(process.env.PORT || 3000);
const hostname = process.env.HOST || '127.0.0.1';
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const server = serve({ fetch: app.fetch, port, hostname }, () => console.log(`Order Rescue UI listening on http://${hostname}:${port}`));
  let stopping = false;
  const shutdown = async () => { if (stopping) return; stopping = true; server.close(); await shutdownAgentTelemetry(); closeHarnessDatabase(); };
  process.once('SIGINT', () => { void shutdown(); });
  process.once('SIGTERM', () => { void shutdown(); });
}
