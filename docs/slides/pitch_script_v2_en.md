# Order Rescue: pitch script for deck v2

Presenter: Lucas. Language: English. Date: 31 October 2026.

## How to use this script

- There are two versions. The **6-minute version** matches the event format (6 minutes of pitch and demo, then 2 minutes of Q&A). The **9 to 10 minute version** is for when you are given more time: it adds three backup slides, a longer demo, and the simulated prompt results.
- Text after `Say:` is spoken. Text after `Do:` is an action on screen. Times are cumulative.
- Every slide ends with one **key line**. If you are running late, say only the key line and move on.
- Speaking pace is about 140 words per minute. The spoken text of the 6-minute version is about 650 words (roughly 4.5 to 5 minutes), which leaves time for clicks, the live demo and transitions. Time yourself once and adjust.
- The app interface is in Vietnamese. Where the demo names a screen element, the English meaning is in brackets so you can say it to an international judge.

## Before you go on stage

- Run `npm run test:unit` right before presenting and read the fresh number. The deck note says 23 tests in 6 files (run on 29 October).
- Run `npm run dev`, keep the app open in its own tab, with scenario OR-SYN-001 selected. Check that the button "Áp dụng phản hồi người mua đã chuẩn bị" (apply the prepared buyer reply) works.
- **The whole team must confirm beforehand** that slide 9 is accurate: Codex was used for the demo app, its tests (Vitest and Playwright), and the data model, business rules and 30 test cases. Say only that. Do not extend the claim to anything else (for example the prompt, the architecture documents, the diagrams or the deck) unless the team did that work with Codex.
- **The whole team must agree on the wording for the hackathon rule:** the product must be built on site in a new public repository, and pre-existing work must be declared. The answer to "what did you build today, and what existed before" must match the declaration submitted at 5:00 PM.
- Open the deck in PowerPoint once. Check slide 5 (rotated lane labels) and slide 6 for text overflow. The presenting machine needs the Georgia and Calibri fonts.
- Prepare screenshots of the four demo steps in case the app fails.
- **Two things in the current deck are out of date:** slide 13 says "Evaluation harness (not built yet)", and slide 15 does not mention the prompt that has been written. There is now prompt v2 and a simulated evaluation run by an LLM. Update these two slides, or say the accurate version aloud as in the 10-minute script.

## 6-minute version

| Time | Slide | Topic |
|---|---|---|
| 0:00 | 1 | Opening |
| 0:20 | 2 | Build directions |
| 0:35 | 3 | Problem |
| 1:05 | 4 | Priorities |
| 1:20 | 5 | Solution: the two-assessment flow |
| 2:00 | 6 | The six output fields |
| 2:10 | 7 | Policy gate |
| 2:30 | 8 | MVP architecture |
| 2:45 | 9 | How we used Codex |
| 3:15 | 10 | Live demo |
| 5:30 | 11 | Value and close |
| 6:00 | | Pitch ends, Q&A for 2 minutes |

### Slide 1: Order Rescue (0:00 to 0:20)

Say:
> Good afternoon. We are Lucas, Phuc, Hai and Kha. Order Rescue is a decision layer for parcels whose first delivery attempt fails. It never acts on its own: it recommends to Operations, with evidence. Everything runs on synthetic data, and we label it that way. And one honest note up front: today's build uses a rule-based assessor in place of the LLM agent. The LLM is our next step, and we have already written its data contract and prompt.

Key line: it never acts, the data is synthetic, the LLM is the next step.

### Slide 2: Why this fits the build directions (0:20 to 0:35)

Say:
> Our primary direction is Autonomous and Adaptive AI: an agent that assesses, asks one question, and reassesses, always inside hard limits. Our second is Deep Domain AI: the rules come from how delivery Operations actually reason. A courier note is unverified, and silence is not refusal.

Key line: Autonomous and Adaptive first, Deep Domain second.

### Slide 3: Problem (0:35 to 1:05)

Say:
> When a first attempt fails, Ops sees a code such as "recipient unavailable" or "refused". Shopee's own public guidance says delivery status can be incorrect or incomplete. The same code can mean the buyer was at work, the address lacked a landmark, the phone had no signal, or the route was disrupted. Retrying blindly wastes a courier trip. Closing the order too early loses a sale. And today there is no structured record of why Ops decided what it did.

Key line: a status code is not a cause.

If you have time (10-minute version): insert slide 12 here.

### Slide 4: Priorities (1:05 to 1:20)

Say:
> We prioritised a trustworthy decision, not a flashy integration. In scope: evidence-based assessment, at most one question to the buyer, a deterministic policy gate, and an audit trail. Out of scope: anything that touches the real world, such as live Shopee or SPX data, real buyer messages, courier dispatch, address changes or refunds.

Key line: trust first, integration later.

### Slide 5: The two-assessment flow (1:20 to 2:00)

Do: follow the diagram with the cursor from left to right, at a steady pace.

Say:
> Here is the flow. Raw data goes through a pre-check: malformed or closed cases never reach the AI. Assessment 1 produces evidence and a hypothesis about the cause. If information is missing, the backend allows exactly one question to the buyer. If the buyer replies, we run assessment 2. If they do not, we keep assessment 1, and we never treat silence as refusal. Finally the policy engine decides what is permitted, and Ops receives the recommendation. The novelty is the bounded design: one question, fixed vocabularies, the LLM proposes, the policy decides, and Ops executes.

Key line: the LLM proposes, the policy decides, Ops executes.

### Slide 6: The six output fields (2:00 to 2:10)

Say:
> The agent returns exactly six fields, and every value must come from an approved list: 7 hypotheses, 8 missing-information codes, and 5 candidate actions. Confidence measures how well the evidence supports the hypothesis, not whether delivery will succeed.

Key line: six fields, fixed vocabularies.

### Slide 7: Policy gate (2:10 to 2:30)

Say:
> This is the trust story. High confidence never overrides policy. A retry is recommended only with direct buyer intent, a time the buyer can receive, and enough delivery information. Anything outside the MVP, such as changing an address, is blocked and escalated to a person. These checks are plain deterministic code, and we have tests for them.

Key line: the LLM never grants itself permission.

### Slide 8: MVP architecture (2:30 to 2:45)

Say:
> Today this is a local React, Vite and TypeScript app. Fixtures stand in for the data stores and a rule-based assessor stands in for the LLM agent. The policy gate and the audit trail are real local code. The target design has the same three layers, backed by a nine-table data model.

Key line: what is real is the policy gate, the audit trail and the tests.

If you have time (10-minute version): insert slides 13 and 14 here.

### Slide 9: How we used Codex (2:45 to 3:15)

Do: briefly show the repo tree (`src/`, `e2e/`, the data model and test case files). Say only what the team has confirmed.

Say:
> On Codex: we used it to build the local demo app, with its interface, assessor, policy gate and audit trail. We used it for the tests too: a Vitest suite with [read the fresh number] tests, and a Playwright spec for the demo flow. And we used it to prepare the data model, the business rules and the 30 synthetic test cases. The LLM agent itself is the next step.

Key line: three areas, stated plainly, and the repo on screen. Say nothing about accuracy.

### Slide 10: Demo (3:15 to 5:30, live, 2 minutes 15 seconds)

Do and say, in order. The app is in Vietnamese, so add one English sentence for international judges where needed.

1. **Transparency labels (15 seconds).** Point at the panel "Nhãn minh bạch" (transparency labels).
   > First, three labels. "Chạy thật cục bộ", real and local, is the interface, the assessor, the policy gate, the audit trail and the tests. "Mô phỏng", simulated, is the orders, events, courier notes and buyer replies. "Tương lai, chưa xác minh", future and unverified, is Shopee or SPX data, messaging and dispatch.
2. **Case OR-SYN-001, "Người mua đang đi làm" (the buyer is at work) (40 seconds).** The case is already selected. Point at the status "recipient unavailable" and the courier note saying the attempt happened during working hours.
   > The code only says the recipient was unavailable. The system suspects a timing conflict but cannot prove it, so the recommendation is only "Hỏi xác nhận từ người mua", ask the buyer to confirm: exactly one question. It does not retry, and it does not blame the buyer.
3. **Apply the buyer reply (40 seconds).** Click "Áp dụng phản hồi người mua đã chuẩn bị" (apply the prepared buyer reply). Point at the new result and at the audit trail, which now has two entries.
   > The simulated buyer confirms the timing conflict and agrees to receive the parcel again. The recommendation changes to "Đề xuất giao lại theo quy trình thường", propose a standard re-attempt, and confidence goes up. Same status code, two different recommendations, because the evidence is different. Every step is in the audit trail.
4. **Blocked request (40 seconds).** Select OR-SYN-003 (landmark unclear). Point at the block "Đã chặn cục bộ: Đổi địa chỉ nhận" (blocked locally: change delivery address).
   > In this case the buyer needs to clarify a landmark. The system only allows a clarification. If someone requests an address change, the policy gate blocks it and records why. Nothing is executed.

Key line: the same code leads to different recommendations as the evidence changes, and out-of-scope requests are blocked.

If the app fails: switch to the four screenshots and say "This is a capture from an earlier run."

### Slide 11: Where AI could create value (5:30 to 6:00)

Say:
> On value, we deliberately show no savings or accuracy numbers, because we do not have any. These four points are hypotheses to validate with real data: fewer wasted re-attempts, faster Ops triage, explainable decisions, and a better buyer experience with a single question. The numbers on the slide are only counts from our 30 synthetic cases: in 9 of them the hypothesis changes after the buyer replies. What we can show today is the mechanism: decisions that are evidence-based, explainable and bounded. Thank you.

Key line: the mechanism works, the value is a hypothesis.

## Additions for the 9 to 10 minute version

Total time is about 9 minutes 30 seconds.

| Insert after | Content | Adds |
|---|---|---|
| Slide 3 | Slide 12: who is hurt | 30 seconds |
| Slide 8 | Slides 13 (scale) and 14 (integration) | 60 seconds |
| Inside the demo | Add cases OR-SYN-004 and OR-SYN-005 | 60 seconds |
| Slide 11 | Slide 15 (roadmap) with the simulated prompt results | 60 seconds |

### Slide 12: Who is hurt (+30 seconds)

Say:
> Four parties feel this. Buyers wait and then get contacted blindly. Couriers burn their limited attempts. Ops triage case by case. Sellers risk returns and lost sales. The hard part is that one status maps to many causes, and only the buyer can resolve some of the unknowns.

### Slide 13: How it scales (+30 seconds)

Say:
> Scaling is a path, not a claim. Today it is a local build with fixtures. Next, real carrier data. Then a case queue with asynchronous agent runs, then a policy profile for each version. Our 30 synthetic cases become the regression suite.

Note: the slide says "Evaluation harness (not built yet)". There has since been a simulated evaluation run by an LLM, but it is not a harness inside the repo. Say it that way if the slide has not been updated.

### Slide 14: Integration (+30 seconds)

Say:
> Integration is designed, not built. The agent would only read the order and delivery-event stores, ask the buyer through a channel the backend controls, and show recommendations in an Ops console where a human decides. To be clear: today the MVP integrates with nothing live.

### Extended demo (+60 seconds)

Do: after step 4 of the demo, select OR-SYN-004, then OR-SYN-005.

Say:
> Case 004 has a service disruption. The system recommends "Tạm giữ do gián đoạn dịch vụ", hold for the disruption, instead of blaming the buyer. Case 005 has only a "refused" code with no evidence that anyone made contact. The system escalates it to a human reviewer. A refusal code alone is not enough to assign fault or to recommend a return.

### Slide 15: Roadmap (+60 seconds)

Say:
> Next we connect the LLM agent to the version 2.2 data contract. We have already written the agent's prompt and run a simulated test on the 30 cases. Honestly: the recommended action matched the label in 30 of 30 cases at the first stage and 24 of 24 after the buyer's reply. But all six fields matched together in only 14 of 30 and 21 of 24. Confidence and missing information are the weak spots. These results come from an LLM simulation compared with draft labels that nobody has reviewed yet, so we treat them as guidance, not accuracy. After that we run all 30 cases through an evaluator, and we only test on real data once we have permission.

## Q&A (2 minutes)

Answer briefly and directly. Never go beyond what has been verified.

| Question | Answer |
|---|---|
| Is a real LLM running yet? | Not in the app. A rule-based assessor stands in for it. The six-field contract, the JSON schema and the prompt are written, and we have run a simulation on the 30 cases. |
| How accurate is it? | We do not claim accuracy. In simulation the actions matched the labels, but confidence and missing information are not good enough yet, and the labels are still drafts. |
| How do you stop the LLM inventing actions? | Three layers. Fixed vocabularies and a schema check on the output. Every piece of evidence must point to a real source. The policy gate is deterministic code and decides the action; the LLM only proposes. Courier notes and buyer replies are treated as data, never as instructions. |
| Why only one question? | It is the demo policy setting: at most one question, so we do not pester the buyer and Ops gets a result quickly. If the answer is not enough, the case goes to a human reviewer. We never open a second round. |
| What if the buyer stays silent? | Silence is not refusal. We keep assessment 1. The demo has a "no reply" button pressed by the operator. We set no wait time because we do not know Shopee's real policy. |
| Do you use real data? | No. Everything is synthetic. Contact and location data are personal data, so we need a legal basis and permission before using them. |
| How much does it save? | We have no number. It is a hypothesis. The first step is shadow mode on historical data, with a baseline agreed with Operations. |
| How is this different from a chatbot? | Three separate layers: raw data, agent assessment, policy decision. The agent never acts. Every decision has evidence and an audit trail. |
| How did you use Codex? | We used it for the demo app, its tests (Vitest and Playwright), and the data model, business rules and 30 test cases. The LLM agent is not built yet. Do not add claims beyond that. |
| What did you build today, and what existed before? | Answer according to the declaration submitted at 5:00 PM. The team must agree this answer before going on stage. |

## Do not say

- Do not say we are integrated with, or approved by, Shopee or SPX. Do not say we read real data or send real messages.
- Do not state accuracy on real orders, money saved, or a percentage of GMV recovered.
- Do not say the agent knows the true cause from a single status code.
- Do not say Codex produced the whole product.
- Do not call the simulated numbers accuracy.

## If you run late

- With 1 minute left and still on slide 8: skip to demo steps 1 and 3, and drop step 4.
- If time is out: say only the key line of slide 11 and thank the judges.
