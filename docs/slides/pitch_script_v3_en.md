# Order Rescue pitch script v3 (6 minutes + 2 minutes Q&A)

Matches `Order_Rescue_Pitch_Deck.pptx` (12 slides: 9 main, 3 backup). Updated after the 29 Oct team meeting. Audience: managers, not engineers. Say the plain-language lines; keep technical words for Q&A.

## Timing

| Slide | Time | Topic |
|---|---|---|
| 1 | 0:00-0:15 | Cover |
| 2 | 0:15-0:55 | Why this matters (Hai's numbers) |
| 3 | 0:55-1:25 | Problem |
| 4 | 1:25-2:15 | Solution in four steps |
| 5 | 2:15-2:45 | Trust: the AI suggests, the rules decide |
| 6 | 2:45-3:25 | How we used Codex |
| 7 | 3:25-3:45 | Declaration: before vs on the day |
| 8 | 3:45-5:45 | Live demo |
| 9 | 5:45-6:00 | Impact and next |

## Script

**Slide 1 (cover).** "Good afternoon. We are Lucas, Phuc, Hai and Kha. Order Rescue helps delivery Ops understand why a delivery failed and what to do next. It recommends; it never acts on its own. All data is synthetic."

**Slide 2 (why it matters).** Hai's numbers: first the Shopee operations figure, then one outside case where a similar problem was reduced, then: "That is why we built this." If the numbers are not ready, delete the slide. Never invent a number.

**Slide 3 (problem).** "When a delivery fails, Ops sees a code like 'recipient unavailable'. It could mean the buyer was at work, the landmark was wrong, the phone was off, or the route was disrupted. A wrong guess wastes a trip or loses the order, and nobody records why."

**Slide 4 (solution).** "Four steps. Read the case. Ask the buyer one question, only one, and only if something is missing. Check the answer against the rules. Then show Ops a recommendation with the evidence; Ops decides. Today a rule-based assessor plays the AI role; the LLM agent is the next step."

**Slide 5 (trust).** "The AI suggests, the rules decide. High confidence never overrides the rules. Silence is not a refusal. A courier note alone is not proof. The AI cannot change an address or refund; those go to a person."

**Slide 6 (Codex).** "We used Codex for the demo app, its tests, and the data model, business rules and 30 test cases. Our process: rules and test cases first, then build, then test against them." Claim nothing beyond this.

**Slide 7 (declaration).** "Before today we prepared the data model, business rules, 30 synthetic cases and a first prototype. On the day we added: [fill from the 5 PM declaration]." Must match the form exactly.

**Slide 8 (demo, 2 minutes, live).**
1. Open OR-SYN-001. Show the evidence and the assessment.
2. Press "Apply the prepared buyer reply". Show the reassessment and the recommendation.
3. Open OR-SYN-003 (address change). Show that the rules block it and send it to a person.
One sentence on the legend: app, rules and tests are real; orders, notes and replies are simulated; nothing connects to Shopee or SPX.

**Slide 9 (impact).** "These are hypotheses, not results; we claim no savings. Next: connect the LLM agent, run all 30 cases through an evaluator, and pilot with permission. Thank you."

## Q&A (2 minutes)

| Question | Answer |
|---|---|
| Is a real LLM running yet? | Not in the app. A rule-based assessor stands in. The output contract, schema and prompt are written, and we simulated it on the 30 cases. |
| How accurate is it? | We claim no accuracy. The labels are still drafts. |
| How do you stop made-up actions? | Fixed vocabularies, evidence tied to real sources, and a deterministic rules gate that decides. The AI only proposes. |
| Why one question only? | Policy setting: at most one, so we do not pester the buyer. If the reply is not enough, a person reviews. |
| What if the buyer stays silent? | Silence is not refusal. The case holds, and Ops reviews after the wait time set by policy. |
| Real data? | No. Everything is synthetic. Real contact data needs a legal basis and permission. |
| How much does it save? | No number yet. First step is shadow mode on historical data. |
| How did you use Codex? | Demo app, tests, data model, business rules and 30 cases. Nothing beyond that. |
| What was built today vs before? | Answer from the 5 PM declaration. Agree this answer as a team before going on stage. |

## Do not say

- Integrated with or approved by Shopee or SPX; real data read; real messages sent.
- Accuracy on real orders, money saved, or percentage of GMV recovered.
- That the agent knows the true cause from one status code.
- That Codex produced the whole product.

## If you run late

- With 1 minute left before the demo: drop slide 7 and go straight to step 1 and step 3 of the demo.
- If time is out: say only the first line of slide 9 and thank the judges.
