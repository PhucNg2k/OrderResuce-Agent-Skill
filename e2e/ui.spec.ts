import { test, expect } from '@playwright/test';

const sse = (...events: Array<[string, unknown]>) => events.map(([event, data]) => `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`).join('');

test('case assessment streams a draft then renders the validated result and accepts a reply', async ({ page }) => {
  const initial = {
    id: 'run-1', state: 'WAITING_FOR_BUYER', case_id: 'SYN-01',
    question: JSON.stringify({ question_id: 'q-1', question_key: 'CONFIRM_INTENT', question_text: 'Bạn có thể nhận hàng vào ngày mai không?' }),
    input: { failed_event: { status: 'FAILED', courier_note: 'Reported issue' }, attempts_used: 1, deadline: '2026-10-31' },
    initial: { hypothesis: 'AVAILABILITY_ISSUE', confidence: 'MEDIUM', candidate_action: 'CLARIFY', missing_info: ['RECEIVING_AVAILABILITY'], evidence: [{ source_ref: 'SYN-01-NOTE', verification: 'UNVERIFIED_REPORT', fact: 'Buyer was away.' }] },
    initial_policy: { final_action: 'CLARIFY', policy_gate: 'PERMITTED', reason: 'One clarification may be simulated.' },
    meta: { explanation: 'Only an unverified courier note is available.', phase: 'initial' }, events: [],
  };
  const completed = {
    ...initial, state: 'COMPLETED', question: null, source: 2,
    events: [{ event_type: 'BUYER_REPLY', created: '2026-10-30T11:00:00.000Z' }],
    after_reply: { ...initial.initial, hypothesis: 'UNKNOWN_CAUSE' },
    after_policy: { final_action: 'ESCALATE_REVIEW', policy_gate: 'ESCALATED', reason: 'Required facts remain unknown.' },
    final: { ...initial.initial, hypothesis: 'UNKNOWN_CAUSE', evidence: '<script>alert(1)</script>' },
    final_policy: { final_action: 'ESCALATE_REVIEW', policy_gate: 'ESCALATED', reason: 'Required facts remain unknown.' },
    meta: { ...initial.meta, phase2: { explanation: 'The buyer reply did not confirm availability.' } },
  };

  await page.route('**/api/cases', route => route.fulfill({ json: [{ case_id: 'SYN-01', title: 'Synthetic availability case' }] }));
  await page.route('**/api/runs/stream', route => route.fulfill({
    status: 200,
    contentType: 'text/event-stream',
    body: sse(['stage', { stage: 'assessing' }], ['token', { delta: '{"assessment":' }], ['result', initial]),
  }));
  await page.route('**/api/runs/run-1/replies/stream', route => route.fulfill({
    status: 200,
    contentType: 'text/event-stream',
    body: sse(['token', { delta: '{"assessment":"after reply"}' }], ['result', completed]),
  }));

  await page.goto('/');
  await expect(page.locator('#cases')).toHaveValue('SYN-01');
  await page.getByRole('button', { name: /New demo run/ }).click();
  await expect(page.getByText('Độ tin cậy: Trung bình')).toBeVisible();
  await expect(page.locator('#replyBox')).toBeVisible();
  await expect(page.locator('#evidence')).toContainText('SYN-01-NOTE');
  await expect(page.locator('#explanation')).toContainText('unverified courier note');

  await page.locator('#replyText').fill('Có, tôi có thể nhận ngày mai.');
  await page.getByRole('button', { name: /Gửi phản hồi/ }).click();
  await expect(page.locator('#replyBox')).toBeHidden();
  await expect(page.locator('#result')).toContainText('Chuyển nhân viên xem xét');
  await expect(page.locator('#result script')).toHaveCount(0);
  await expect(page.locator('#explanation')).toContainText('did not confirm availability');
  await expect(page.locator('#history')).toContainText('BUYER_REPLY');
});

test('real browser to Hono API to harness and SQLite supports two rounds and refresh', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /New demo run/ }).click();
  await expect(page.locator('#replyBox')).toBeVisible();
  await expect(page.locator('#questionHeading')).toContainText('1/2');
  await page.locator('#replyText').fill('I still want the parcel, but I am unsure who can receive it.');
  await page.getByRole('button', { name: /Gửi phản hồi/ }).click();
  await expect(page.locator('#replyBox')).toBeVisible();
  await expect(page.locator('#questionHeading')).toContainText('2/2');
  await expect(page.locator('#history')).toContainText('I still want the parcel');
  await page.reload();
  await expect(page.locator('#questionHeading')).toContainText('2/2');
  await expect(page.locator('#history')).toContainText('I still want the parcel');
  await page.locator('#replyText').fill('I still want it, but still do not know who can receive it.');
  await page.getByRole('button', { name: /Gửi phản hồi/ }).click();
  await expect(page.locator('#replyBox')).toBeHidden();
  await expect(page.locator('#result')).toContainText('Chuyển nhân viên xem xét');
  await expect(page.locator('#history')).toContainText('Assessment lượt 0');
  await expect(page.locator('#history')).toContainText('Assessment lượt 2');
});

test('explicit retry is visible after a persisted model failure and preserves run history', async ({ page }) => {
  await page.goto('/');
  await page.locator('#cases').selectOption('SYN-02');
  await page.getByRole('button', { name: /New demo run/ }).click();
  await expect(page.locator('#status')).toContainText('Cần nhân viên xem xét');
  await expect(page.locator('#retry')).toBeVisible();
  await page.getByRole('button', { name: /Retry assessment/ }).click();
  await expect(page.locator('#replyBox')).toBeVisible();
  await expect(page.locator('#retry')).toBeHidden();
  await expect(page.locator('#history')).toContainText('Retry thủ công');
});
