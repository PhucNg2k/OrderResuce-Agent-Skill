// Generates Product_Vision and Software_Architecture_Document .docx files for Order Rescue.
// Run: DOCX_BASE=<folder where the docx package is installed> node build_docs.js
const fs = require('fs'); const path = require('path');
const D = require(require.resolve('docx', { paths: [process.env.DOCX_BASE || __dirname] }));
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Header, Footer, AlignmentType,
  LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageOrientation, PageBreak } = D;

const DIAG = path.join(__dirname, '..', 'diagrams');
const OUT = __dirname;
const INK = '1F2A37', ACC = '0E5E6F', GREY = '5B6270', HEAD_FILL = 'DCE9EC', ALT = 'F4F7F8';
const A4 = { width: 11906, height: 16838 };
const MARGIN = 1134;
const CW = A4.width - 2 * MARGIN;          // 9638 portrait content width

// ---------- helpers ----------
const run = (t, o = {}) => new TextRun({ text: t, font: 'Calibri', size: 22, color: INK, ...o });
function rich(text, o = {}) {              // **bold** and `code` inline markup
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/).filter(Boolean).map(s => {
    if (s.startsWith('**')) return run(s.slice(2, -2), { ...o, bold: true });
    if (s.startsWith('`')) return run(s.slice(1, -1), { ...o, font: 'Consolas', size: Math.max(16, (o.size || 22) - 2) });
    return run(s, o);
  });
}
const p = (text, o = {}) => new Paragraph({ spacing: { after: 120, line: 276 }, alignment: o.align, children: rich(text, o.run || {}), keepNext: o.keepNext });
const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 140 }, keepNext: true, children: [new TextRun({ text: t, font: 'Calibri', size: 32, bold: true, color: ACC })] });
const h2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 100 }, keepNext: true, children: [new TextRun({ text: t, font: 'Calibri', size: 26, bold: true, color: INK })] });
const h3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 160, after: 80 }, keepNext: true, children: [new TextRun({ text: t, font: 'Calibri', size: 23, bold: true, color: GREY })] });
const bullets = (items) => items.map(t => new Paragraph({ numbering: { reference: 'bul', level: 0 }, spacing: { after: 60, line: 264 }, children: rich(t) }));
let numRef = 0;                            // each numbered list restarts at 1
const numbered = (items) => { const ref = 'num' + (numRef++); NUM_REFS.push(ref); return items.map(t => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60, line: 264 }, children: rich(t) })); };
const NUM_REFS = [];
const spacer = () => new Paragraph({ spacing: { after: 80 }, children: [] });

const border = { style: BorderStyle.SINGLE, size: 4, color: 'C9D3D6' };
const borders = { top: border, bottom: border, left: border, right: border };
function cell(text, w, o = {}) {
  const lines = Array.isArray(text) ? text : [text];
  return new TableCell({
    width: { size: w, type: WidthType.DXA }, borders, margins: { top: 70, bottom: 70, left: 110, right: 110 },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined, verticalAlign: 'top',
    children: lines.map(l => new Paragraph({ spacing: { after: 30, line: 252 }, children: rich(String(l), { size: o.size || 20, bold: o.bold }) })),
  });
}
function table(headers, rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: headers.map((h, i) => cell(h, widths[i], { fill: HEAD_FILL, bold: true, size: o.size })) }),
      ...rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], { fill: ri % 2 ? ALT : undefined, size: o.size })) })),
    ],
  });
}
function kv(rows, widths = [2400, CW - 2400]) {
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map(([k, v]) => new TableRow({ cantSplit: true, children: [cell(k, widths[0], { fill: HEAD_FILL, bold: true }), cell(v, widths[1])] })),
  });
}
function code(text) {
  return text.split('\n').map(l => new Paragraph({
    spacing: { after: 0, line: 240 }, shading: { fill: 'F2F4F5', type: ShadingType.CLEAR, color: 'auto' }, indent: { left: 120, right: 120 },
    children: [new TextRun({ text: l === '' ? ' ' : l, font: 'Consolas', size: 17, color: '1F2937' })],
  })).concat([spacer()]);
}
function figure(file, maxW, maxH, caption) {
  const buf = fs.readFileSync(path.join(DIAG, file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const s = Math.min(maxW / w, maxH / h);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, keepNext: true, children: [new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(w * s), height: Math.round(h * s) }, altText: { title: caption, description: caption, name: file } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [run(caption, { size: 18, italics: true, color: GREY })] }),
  ];
}
function titleBlock(kicker, title, subtitle) {
  return [
    new Paragraph({ spacing: { after: 60 }, children: [run(kicker, { size: 20, bold: true, color: ACC, characterSpacing: 40 })] }),
    new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: title, font: 'Calibri', size: 52, bold: true, color: INK })] }),
    new Paragraph({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACC, space: 6 } }, children: [run(subtitle, { size: 24, color: GREY })] }),
  ];
}
const numberingFor = () => ({ config: [
  { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 520, hanging: 260 } } } }] },
  ...NUM_REFS.map(ref => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 520, hanging: 320 } } } }] })),
] });
const styles = { default: { document: { run: { font: 'Calibri', size: 22 } } },
  paragraphStyles: [
    { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 32, bold: true, font: 'Calibri' }, paragraph: { spacing: { before: 360, after: 140 }, outlineLevel: 0 } },
    { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 26, bold: true, font: 'Calibri' }, paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 1 } },
    { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 23, bold: true, font: 'Calibri' }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } },
  ] };
const hdrFtr = (label) => ({
  headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [run('Order Rescue  |  ' + label, { size: 16, color: GREY })] })] }) },
  footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [run('Draft, synthetic data only  |  Page ', { size: 16, color: GREY }), new TextRun({ children: [PageNumber.CURRENT], font: 'Calibri', size: 16, color: GREY })] })] }) },
});
const portrait = { page: { size: A4, margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } } };
const landscape = { page: { size: { width: A4.width, height: A4.height, orientation: PageOrientation.LANDSCAPE }, margin: { top: 900, right: MARGIN, bottom: 900, left: MARGIN } } };

// =====================================================================
// PRODUCT VISION
// =====================================================================
function productVision() {
  const W4 = [2300, 1900, 2900, 2538];
  const c = [
    ...titleBlock('PRODUCT VISION', 'Order Rescue', 'Adaptive Delivery Recovery Agent: from a failure code to the right recovery decision'),
    kv([
      ['Document Definition', 'The Product Vision is a broad, high-level statement of what the product aspires to achieve, its purpose, long-term objectives, and how it creates value for users and the business.'],
      ['Purpose', 'Explain why Order Rescue exists and what problem it solves, so that stakeholders and the whole team share one direction.'],
      ['Who to Share', 'Stakeholders, executives, hackathon judges, and the whole team (Lucas, Phúc, Hải, Kha).'],
      ['Document Scope', 'Inspirational and strategic. Focuses on "why" and "for whom". It does not specify implementation details; those live in the Software Architecture Document.'],
    ]),
    spacer(),
    p('**Product:** "Order Rescue" - an explainable, policy-bounded AI decision layer that helps Operations teams recover failed first-attempt deliveries before another delivery attempt is wasted.'),

    h1('1. Problem Statement'),
    p('When a delivery attempt fails, the system records a status such as RECIPIENT_UNAVAILABLE, CONTACT_FAILED or REFUSED. That status is an **observation, not a cause**. Behind one code can sit very different realities: the buyer was at work, the address lacked a landmark, the phone had no signal, the buyer did not recognise a gift order, cash for COD was not ready, or the route was paused by flooding.'),
    p('Treating every failure the same way wastes scarce courier capacity, can end in avoidable return logistics, and risks blaming the buyer on the strength of a single code. Public Shopee guidance itself notes that delivery status can be incorrect or incomplete, and research on last-mile delivery documents that false "customer unavailable" remarks are a known operational risk.'),

    h1('2. Vision'),
    p('We recognise a gap between **what the delivery system recorded** and **what Operations must decide next**. Order Rescue closes that gap with an evidence-first loop: read the raw data, state the most likely cause with sourced evidence and an honest confidence level, name what is still missing, ask the buyer at most one useful question, and then recommend the next action to a human Operations reviewer.'),
    p('Order Rescue creates a **trustworthy decision layer** between raw delivery data and Ops action. The language model proposes; a deterministic policy gate decides what is permitted; a human stays in control. Every recommendation can be traced back to the source records and the buyer\'s own words, and nothing is executed on the buyer\'s or courier\'s behalf.'),
    p('From a single failure code, Order Rescue can reach different recommendations when the evidence differs: ask a clarifying question, recommend a standard re-attempt, hold for a verified service disruption, or escalate to Ops review. It will never claim a cause that the evidence does not support, and it treats buyer silence as silence, not as refusal.'),
    p('Our goal for the hackathon is to prove this loop end to end on **30 synthetic scenarios**. Our long-term aspiration is to run it in shadow mode beside real Operations teams, with authorised data access, so that its recommendations can be compared with real outcomes before anything is automated.'),

    h1('3. The Pain We\'re Solving'),
    h3('For Who'),
    ...bullets([
      '**Primary:** last-mile Operations teams (for example Shopee / SPX style failed-delivery recovery, retry and return desks) who triage failed deliveries every day.',
      '**Affected:** buyers and recipients, who may need to clarify availability or intent and who should not be blamed for a code they did not choose.',
      '**Indirect:** sellers, through fewer lost orders and less inventory tied up in reverse logistics.',
    ]),
    h3('For What'),
    p('They lack a way to turn a generic failure code into a **diagnosis with evidence**. Today the next step is often the same for every case (try again, or return), because the cause is unknown and asking the buyer costs time. Ops needs to know which cases are worth a re-attempt, which need one clarifying question, which are blocked by a disruption, and which need a human decision, and needs to see why.'),
    h3('Impact'),
    p('By separating raw data, AI assessment and policy decision, Order Rescue aims to enable:'),
    ...bullets([
      'Fewer wasted re-attempts, because re-attempts are recommended only when intent, availability and delivery information are supported by evidence.',
      'Faster, more consistent Ops triage, because each case arrives with sourced evidence, a confidence level and the missing information.',
      'Fairer treatment of buyers, because a status code alone never decides fault and silence is not refusal.',
      'Safer automation, because the policy gate blocks unsupported actions and the system never executes dispatch, messaging, address or COD changes.',
      'A foundation for learning, because every decision is recorded as an auditable two-step assessment.',
    ]),
    p('These impacts are **hypotheses to validate** with real Operations data. They are not measured results.', { run: { italics: true, color: GREY } }),

    h1('4. Success Metrics'),
    p('The hackathon phase can only be measured on synthetic data. Metrics that need real operations data are listed as future and have no baseline yet.'),
    table(['Metric', 'Target', 'Current', 'Why It Matters'], [
      ['Synthetic scenario suite', '30 cases covering 7 hypotheses and 6 manual no-reply branches', '30 cases defined (draft labels); 5 scenarios runnable in the local app', 'Repeatable proof of behaviour'],
      ['Candidate action agreement with golden labels', 'Target set after the labels are reviewed with Hải', 'Prompt v2 simulation: 30/30 at the initial stage, 24/24 after reply (draft labels, LLM-simulated)', 'The recommendation is the core value'],
      ['All six assessment fields agree', 'Target set after label review', 'Prompt v2 simulation: 14/30 initial, 21/24 after reply. Confidence and missing_info are the weakest fields', 'Evidence quality and trust'],
      ['Schema-valid assessments', '100%', 'Not yet measured with a live model', 'Reliability of the contract'],
      ['Unsupported operational actions executed', '0', '0 by design (policy gate, no live integrations)', 'Safety'],
      ['Claims beyond verified capability', '0', 'Claim ledger and truth labels (real-local, simulated, future) kept in the demo', 'Credibility with judges and Ops'],
      ['First-attempt rescue rate, wasted re-attempts avoided, Ops triage time', 'Baseline and targets to be agreed with Operations', 'Not measurable: no live data access', 'Real-world value (future, unverified)'],
    ], W4, { size: 19 }),
    spacer(),
    p('Simulation figures come from the prompt evaluation report (30 synthetic cases, two independent simulated stages, graded against draft golden labels). They are not evidence of accuracy on real shipments.', { run: { italics: true, color: GREY, size: 20 } }),

    h1('5. Strategy'),
    p('Phase durations beyond the hackathon depend on partner access and are deliberately not fixed here.'),
    h3('Phase 1: Hackathon MVP (build day: 31 October 2026)'),
    ...bullets([
      '**Done:** concept selection (25 September 2026), data model v2.2 (9 tables), business rules, 30 synthetic test cases, local Vite + React + TypeScript demo with deterministic assessor and policy gate, assessment prompt v2 and its evaluation harness.',
      '**Next:** review of the draft golden labels with Hải, live Agent integration behind the schema validator, narrated team rehearsal.',
      '**Hackathon deliverables:** public repository, project write-up (PDF), demo link, declaration of pre-existing work.',
    ]),
    h3('Phase 2: Validation with authorised access'),
    ...bullets([
      'Obtain documented permission and data access. Until then every figure stays synthetic.',
      'Run in shadow mode on historical failed deliveries; replace draft labels with Operations-reviewed labels.',
      'Agree baselines and targets with Operations for rescue rate, wasted re-attempts and triage time.',
    ]),
    h3('Phase 3: Human-in-the-loop pilot'),
    ...bullets([
      'Recommendations shown in an Ops console; humans execute every action.',
      'A real buyer contact channel, used only through a backend contact gate and policy.',
    ]),
    h3('Phase 4: Scale and learn'),
    ...bullets([
      'Carrier- and policy-version-specific profiles, extended vocabularies, outcome feedback into evaluation.',
      'Move from recommendation to partially automated actions only where policy and Operations explicitly allow it.',
    ]),

    h1('6. Key Features'),
    h3('Must Have (MVP)'),
    ...bullets([
      'Case intake from the 9-table data model (case, order, failed event, T0 buyer context, interactions).',
      'Deterministic backend pre-check before any AI call (lifecycle, deadline, malformed input).',
      'Agent assessment 1: evidence with sources, one of 7 hypotheses, confidence, missing information, question key, candidate action.',
      'One buyer question, then either buyer reply (assessment 2) or the manual "no reply" control that keeps assessment 1.',
      'Deterministic policy gate: eligibility, gate decision, final action, reason. The LLM never grants itself permission.',
      'Audit trail of decision records and visible truth labels (real-local, simulated, future / unverified).',
      'Evaluation harness over 30 synthetic cases.',
    ]),
    h3('Should Have (Phase 2)'),
    ...bullets([
      'Live Agent call with strict schema and source-reference validation, server-side only.',
      'Contact gate rules and defined behaviour for blocked or denied paths.',
      'Ops-reviewed golden labels and a regression suite built from them.',
      'Decision dashboard for Ops (queue, evidence, missing information).',
    ]),
    h3('Could Have (Future)'),
    ...bullets([
      'Production timeout and late-reply policy.',
      'Carrier- and region-specific policy profiles.',
      'Additional hypotheses where real data shows gaps (for example separating wrong recipient from changed mind).',
      'Outcome tracking and learning from resolved cases.',
    ]),
    h3('Out of scope (will not claim)'),
    ...bullets([
      'Any live integration with Shopee, SPX or a courier; any real buyer message, dispatch, exact delivery slot, address or COD change, return or refund.',
      'Any claim of money saved, GMV recovered, or accuracy on real shipments.',
    ]),

    h1('7. What Success Looks Like'),
    h3('Phase 1: Hackathon'),
    ...bullets([
      'The demo runs end to end on synthetic cases: failure, assessment, one question, reply or no reply, final recommendation.',
      'The same broad failure signal visibly leads to different recommendations when the evidence differs.',
      'Every recommendation can be traced to a source record and the buyer\'s own words.',
      'Typecheck, unit tests and the browser journey pass; the team can explain what is real, simulated and future.',
      'No claim goes beyond what is verified.',
    ]),
    h3('Later phases'),
    ...bullets([
      'Operations reviewers agree that recommendations are explainable and useful on historical cases, measured against reviewed labels.',
      'A pilot shows, against an agreed baseline, fewer wasted re-attempts and faster triage. Targets are set with Operations, not assumed here.',
    ]),

    h1('Document Info'),
    kv([
      ['Author', 'Core Team (Lucas, Phúc, Hải, Kha)'],
      ['Last Updated', 'October 29, 2026'],
      ['Version', '0.1'],
      ['Status', 'Draft for team review'],
      ['Review Date', 'To be set; before the 31 October 2026 hackathon rehearsal'],
    ]),
  ];
  return new Document({ creator: 'Order Rescue team', title: 'Order Rescue - Product Vision', styles, numbering: numberingFor(),
    sections: [{ properties: portrait, ...hdrFtr('Product Vision'), children: c }] });
}

// =====================================================================
// SOFTWARE ARCHITECTURE DOCUMENT
// =====================================================================
function sad() {
  const s1 = [
    ...titleBlock('SOFTWARE ARCHITECTURE DOCUMENT', 'Order Rescue', 'How the Adaptive Delivery Recovery Agent is built'),
    kv([
      ['Document Definition', 'This technical document lays out "how" the product is built: system architecture, technology stack, component structure, data flow and key technical decisions.'],
      ['Who to Share', 'Development team, system architects, evaluators and reviewers.'],
      ['Document Scope', 'Deeply technical. Covers system structure, data contract, security, code organisation, integration and engineering details. Product "why" lives in the Product Vision.'],
    ]),
    spacer(),
    p('**Reading note.** This document separates what is **implemented today** (local MVP) from the **target architecture** (v2.2 contract with a live LLM Agent). Items marked "Target" or "Proposed" are not built yet. Section 12 lists the known gaps.', { run: { color: GREY } }),

    h1('1. Executive Summary'),
    kv([
      ['Product', 'Order Rescue: Adaptive Delivery Recovery Agent'],
      ['Version', '0.1 (hackathon MVP)'],
      ['Architecture Style', 'Deterministic decision pipeline with an LLM assessment step behind a validated contract. Single-page local app today; stateless backend service as target'],
      ['Core Principle', 'Three separated layers: raw data, Agent assessment (LLM proposes), policy output (deterministic code decides)'],
      ['Target Scale', 'Demo scale: 30 synthetic cases. No production scale or load target has been set or measured'],
      ['Infrastructure', 'Local development machine (Vite dev server). No deployment, no carrier integration'],
      ['Data', 'Synthetic only. No Shopee / SPX data, API, buyer messaging, dispatch or operational action'],
      ['Document Status', 'Draft'],
      ['Last Updated', 'October 29, 2026'],
    ]),

    h1('2. High-Level Architecture Overview'),
    h2('2.1 Architecture Philosophy'),
    p('**Evidence-first, policy-bounded, human-in-the-loop.** The design rests on four rules taken from the v2.2 business rules:'),
    ...numbered([
      '**Three layers never mix.** Raw data (status, courier note, lifecycle, buyer context, replies), Agent assessment (evidence, hypothesis, confidence, missing_info, question_key, candidate_action) and policy output (eligibility, policy_gate, final_action, reason).',
      '**The LLM proposes, code decides.** Anything that must be correct (eligibility, attempt limits, allowed actions) is computed by deterministic code. The Agent only proposes a candidate action.',
      '**Two assessment slots, one final.** A case stores at most an initial and an after-reply assessment. The final assessment is a copy of one of them, never a third inference.',
      '**Nothing is executed.** The system recommends to Operations. It never calls carrier APIs, messages real buyers, changes addresses or COD, dispatches, returns or refunds.',
    ]),
    h2('2.2 System Components'),
    p('Figure 1 (next page) shows the components. Solid boxes exist in the repository today; dashed boxes are target components.'),
    ...bullets([
      '**Presentation (implemented):** React components render the scenario list, assessment, evidence, policy result and audit timeline, plus truth labels that mark what is real-local, simulated or future.',
      '**Application state (implemented):** `useDemoSession` keeps one session per scenario and triggers re-assessment; `buildDecisionRecord` writes an immutable audit record for each assessment.',
      '**Decision core:** `assessCase` is the deterministic assessor used by the MVP (v1 rules). The LLM Agent runner and the schema validator are the target replacement for the v2.2 contract. `evaluatePolicy` is the deterministic policy gate and already blocks unsupported requests such as address change, courier dispatch or refund.',
      '**Data:** five synthetic fixtures today; the v2.2 data model (9 tables, 30 seed cases in JSON) is the target store. The database engine is not selected.',
      '**Offline evaluation harness:** 30 golden cases that are never given to the Agent, simulated runs and graders (exact match on enums, set match on missing_info).',
    ]),
  ];
  const figArch = figure('architecture_overview.png', 970, 590, 'Figure 1. System architecture (solid = implemented, dashed = target)');
  const s3 = [
    h2('2.3 Data Flow Architecture'),
    p('Figure 2 (next page) shows the case flow defined by the v2.2 contract. In words:'),
    ...numbered([
      'A trigger creates or loads a case in status **NEW** with raw input only. No expected answers are stored.',
      'The **backend pre-check** rejects malformed input, started or completed returns, unknown or expired deadlines, no attempts remaining, and duplicate or stale triggers. A blocked case does not call the AI and is routed to Ops (outside the 30-case suite).',
      '**Agent assessment 1** receives `core_input` (case id, failed event, attempts used, return state, deadline, buyer history, operational context including T0 buyer messages) and returns the six-field assessment. The backend validates it, computes the policy output and stores both (status **ASSESSED**).',
      'The **contact gate** decides whether one buyer question is permitted. If so, one question is emitted and the case moves to **WAITING_FOR_BUYER**.',
      'If the buyer replies, the backend rebuilds the raw input plus the reply as `runtime_context`, runs **Agent assessment 2** and the policy, and the final assessment is a copy of it (`final_assessment_source = 2`).',
      'If the demo operator presses **USER_NO_REPLY**, no second Agent call is made; the final assessment is a copy of the initial one (`final_assessment_source = 1`). The system never turns silence into refusal.',
      'The case becomes **COMPLETED**. This means a recommendation was fixed, not that Ops acted or the parcel was delivered.',
    ]),
  ];
  const figFlow = figure('case_flow.png', 960, 600, 'Figure 2. Two-assessment case flow (v2.2 contract)');

  const s5 = [
    h1('3. Technology Stack'),
    table(['Layer', 'Choice', 'Status'], [
      ['Language', 'TypeScript (project references: tsconfig.app.json, tsconfig.node.json)', 'Implemented'],
      ['UI framework', 'React with react-dom', 'Implemented'],
      ['Build / dev server', 'Vite with @vitejs/plugin-react', 'Implemented'],
      ['Package manager', 'npm (package-lock.json)', 'Implemented'],
      ['Unit / component tests', 'Vitest, Testing Library (react, jest-dom), jsdom', 'Implemented'],
      ['Browser tests', 'Playwright (e2e/order-rescue-demo.spec.ts)', 'Implemented'],
      ['Decision engine (MVP)', 'Pure TypeScript functions: assessCase, evaluatePolicy, buildDecisionRecord', 'Implemented'],
      ['LLM Agent', 'OpenAI model called server-side with structured JSON output; system prompt and JSON Schema in src/agent/prompts/. Model id not fixed', 'Target (prompt written and evaluated by simulation)'],
      ['Data store', 'Logical 9-table model in JSON seed; relational engine not chosen. Reference SQL was run on SQLite in memory only', 'Target'],
      ['Backend runtime', 'Not chosen. Must be stateless per request, with transactions around state changes', 'Target'],
      ['CI/CD', 'None yet. GitHub Actions proposed (see section 9)', 'Proposed'],
      ['Hosting', 'Local only. No deployment', 'n/a'],
    ], [2200, 5238, 2200], { size: 19 }),
    spacer(),
    p('Note: `package.json` pins dependencies to `latest`; reproducibility today relies on the lockfile. Pinning exact versions is recommended (section 12).'),

    h1('4. Modular Architecture Design'),
    h2('4.1 Module Structure'),
    ...code(`src/
  app/            useDemoSession.ts        session state, re-assessment
  components/     ScenarioList, AssessmentPanel, EvidencePanel,
                  PolicyResultPanel, AuditTimeline, TruthLegend,
                  DecisionFlowDiagram, ScopeDiagram, SyntheticDataCard
  data/           scenarios.ts             5 synthetic fixtures + validateScenario
                  Database model/          v2.2 data model + seed (JSON)
                  Test case/               30 golden cases (JSON, never Agent input)
  domain/         types.ts                 vocabularies, actions, labels
  engine/         assessCase.ts            deterministic assessor (MVP v1)
                  policyGate.ts            deterministic policy gate
                  buildDecisionRecord.ts   audit record builder
  agent/prompts/  recommendation_system_prompt.md
                  assessment.schema.json   six-field output schema
                  README.md
  test/           setup.ts
e2e/              order-rescue-demo.spec.ts`),
    p('**Rules of the structure:** components never compute decisions; the engine is pure (no I/O, no globals) so it is unit-testable; the Agent can only reach the engine through the validator; the golden test file is read only by the evaluator.'),
    h3('Target backend modules'),
    table(['Module', 'Responsibility'], [
      ['case-store', 'Reads cases with the four query recipes; writes initial and final assessments with guarded updates (affected rows = 1)'],
      ['precheck', 'Deterministic lifecycle, deadline, attempts, PII and duplicate checks before any AI call'],
      ['contact-gate', 'Decides whether one buyer question is permitted; writes the question and wait state'],
      ['agent-runner', 'Builds the envelope, calls the LLM with the system prompt, returns raw JSON'],
      ['validator', 'Validates six-field schema, enums, source_ref existence and availability, verification values'],
      ['policy-engine', 'Computes eligibility, policy_gate, final_action and reason from a versioned policy profile'],
      ['evaluator', 'Offline: runs cases, compares with golden labels, produces reports'],
    ], [2200, 7438], { size: 19 }),
    h2('4.2 State and Event Catalog'),
    p('Case status follows a fixed state machine (from the v2.2 runtime contract). Each transition writes specific fields and only from the expected prior state.'),
    ...code(`{
  "states": ["NEW", "ASSESSED", "WAITING_FOR_BUYER", "COMPLETED"],
  "transitions": [
    { "from": "NEW", "event": "VALID_INITIAL_ASSESSMENT", "to": "ASSESSED",
      "writes": ["initial_assessment", "initial_policy_output"] },
    { "from": "ASSESSED", "event": "PERMITTED_FIRST_QUESTION", "to": "WAITING_FOR_BUYER",
      "writes": ["AI_QUESTION interaction", "question_wait_state=PENDING"] },
    { "from": "WAITING_FOR_BUYER", "event": "MATCHING_BUYER_REPLY", "to": "COMPLETED",
      "writes": ["BUYER_REPLY interaction", "after_reply_*", "final_assessment_source=2",
                 "final fields", "question status=ANSWERED"] },
    { "from": "WAITING_FOR_BUYER", "event": "MANUAL_USER_NO_REPLY", "to": "COMPLETED",
      "writes": ["final_assessment_source=1", "final fields = initial",
                 "question status=NO_REPLY", "after_reply_* stay null"] }
  ]
}`),
    p('Interaction types stored in `fact_rescue_interaction`: **BUYER_CONTEXT** (raw context known before T0, never a reply), **AI_QUESTION**, **BUYER_REPLY**, and the **USER_NO_REPLY** control (never evidence of buyer intent).'),
    p('Pre-reply guards before calling Agent 2: case is WAITING_FOR_BUYER and not COMPLETED; exactly one allowed question is PENDING; the event is a BUYER_REPLY for the same case and matching `question_id`; no other outcome exists for that question.'),

    h1('5. Data Architecture'),
    h2('5.1 Core Database Schema'),
    p('The v2.2 model has **9 tables, 67 columns and 9 relationships**. Figure 3 (next page) is the ERD. Column types are logical; nullability is not yet enforced as DDL.'),
    table(['Table', 'Role', 'Key columns'], [
      ['order_rescue', 'Case, lifecycle, two assessment slots, final result', 'case_id (PK), order_id, failed_event_id (FK, unique), current_status, attempts_used, return_state, deadline_at, policy_version, initial_* / after_reply_* / final_*'],
      ['fact_order', 'Current order, payment type, operational context', 'order_id (PK), buyer_id, payment_type, operational_context (JSON)'],
      ['fact_delivery_event', 'Failed event that triggers the case plus history', 'event_id (PK), order_id, event_status, courier_note, reported_reason'],
      ['fact_rescue_interaction', 'Buyer context, question, reply, no-reply control', 'interaction_id (PK), case_id, interaction_type, available_phase, question_id'],
      ['dim_buyer', 'Buyer reference (history is derived, never stored here)', 'buyer_id (PK)'],
      ['dim_action', 'Valid action codes', 'action_id (PK): CLARIFY, STANDARD_REATTEMPT, HOLD_DISRUPTION, ESCALATE_REVIEW, NO_ACTION'],
      ['dim_product, dim_carrier, dim_date', 'Optional dimensions; product and carrier are empty in the seed', 'product_id, carrier_id, date_id'],
    ], [2300, 3000, 4338], { size: 19 }),
    h3('Assessment object (stored three times as JSON columns)'),
    p('`initial_assessment`, `after_reply_assessment` and `final_assessment` share one schema. They are not three tables, and the Agent returns exactly these six keys:'),
    ...code(`{
  "evidence": [ { "source_ref": "DEMO-001-NOTE",
                  "fact": "...short, sourced, states who reported what...",
                  "verification": "UNVERIFIED_REPORT" } ],
  "hypothesis": "AVAILABILITY_ISSUE",
  "confidence": "MEDIUM",
  "missing_info": ["CURRENT_BUYER_INTENT", "RECEIVING_AVAILABILITY"],
  "question_key": "CONFIRM_INTENT",
  "candidate_action": "CLARIFY"
}
// policy output (backend only): eligibility, policy_gate, final_action, reason`),
    h3('Approved vocabularies'),
    table(['Field', 'Values'], [
      ['hypothesis (7)', 'AVAILABILITY_ISSUE, ADDRESS_ISSUE, CONTACT_ISSUE, BUYER_INTENT_ISSUE, PAYMENT_ISSUE, LOGISTICS_ISSUE, UNKNOWN_CAUSE'],
      ['confidence (3)', 'LOW, MEDIUM, HIGH (support for the cause, not likelihood of delivery success)'],
      ['verification (4)', 'SOURCE_RECORD, UNVERIFIED_REPORT, DIRECT_BUYER_STATEMENT, VERIFIED_OPS_SIGNAL'],
      ['missing_info (8)', 'CURRENT_BUYER_INTENT, RECEIVING_AVAILABILITY, ADDRESS_CLARIFICATION, CONTACT_CLARIFICATION, COD_READINESS, DELIVERY_ACCESS, LOGISTICS_VERIFICATION, CAUSE_CLARIFICATION'],
      ['question_key (2 + null)', 'CONFIRM_INTENT, CLARIFY_LANDMARK, null'],
      ['candidate_action (5)', 'CLARIFY, STANDARD_REATTEMPT, HOLD_DISRUPTION, ESCALATE_REVIEW, NO_ACTION'],
      ['policy_gate / eligibility', 'PERMITTED, BLOCKED, ESCALATED / ELIGIBLE, INELIGIBLE, UNKNOWN'],
    ], [2600, 7038], { size: 19 }),
    h3('Read and write rules'),
    ...bullets([
      '**Read path for the Agent:** case, order and failed event joined once and validated (one row, same `order_id`, `event_time <= as_of`); buyer history from other orders of the same buyer (empty in the 30 seed cases); T0 buyer context from `BUYER_CONTEXT` rows; runtime interactions only after they were actually released. Never `SELECT *` rows that contain earlier assessments.',
      '**Write path:** validate against the schema first, then guarded `UPDATE` statements (status and empty slot checked in the WHERE clause); require affected rows = 1; bind JSON with a library, never by string concatenation.',
      '**Final fields are written once.** Late events never reopen a COMPLETED case.',
    ]),
    h2('5.2 State and Persistence Strategy'),
    p('The architecture needs no cache. The consistency strategy replaces it:'),
    table(['Concern', 'Strategy'], [
      ['Idempotency', 'Unique failed_event_id per case; guarded UPDATEs with state in the WHERE clause; affected rows = 1 or abort'],
      ['Atomicity', 'After-reply assessment, policy output, final selection and question status are written in one transaction'],
      ['Re-runnable tests', 'Reset or clone the seed before every evaluation run'],
      ['Isolation', 'Golden labels live in a separate file that retrieval and the Agent can never read'],
      ['Time', 'Compare parsed timestamps, not strings; the `as_of` of the assessment moment bounds what is visible'],
    ], [2400, 7238], { size: 19 }),
  ];
  const figErd = figure('data_model_erd.png', 970, 600, 'Figure 3. Data model v2.2 (9 tables, 67 columns, 9 relationships)');

  const s7 = [
    h1('6. Interface Architecture'),
    p('The MVP has no network API: the UI calls engine functions in the same process. This section defines the **Agent contract** (target) and a **proposed** service interface. Nothing in 6.2 and 6.3 is implemented.', { run: { color: GREY } }),
    h2('6.1 Agent Contract'),
    p('Input envelope (seven core fields plus runtime context):'),
    ...code(`{
  "core_input": {
    "case_id": "DEMO-001",
    "failed_event": { "status": "...", "time": "...", "courier_note": "...",
                      "reported_reason": "...", "as_of": "..." },
    "attempts_used": 1,
    "return_state": "NOT_STARTED",
    "deadline": "2026-10-28T15:00:00+07:00",
    "buyer_history": [],
    "operational_context": { "route": "...", "payment": "PREPAID",
                             "policy_version": "...", "source_refs": ["..."],
                             "buyer_messages_t0": [ { "source_ref": "...", "text": "..." } ] }
  },
  "runtime_context": [ { "source_ref": "...-REPLY", "interaction_type": "BUYER_REPLY", "text": "..." } ]
}`),
    p('Output: the six-field assessment above, JSON only. `assessment.schema.json` enforces keys and enums. Policy fields are never produced by the Agent.'),
    h2('6.2 Proposed Service Endpoints'),
    ...code(`POST /v1/cases/{caseId}/assess      # run precheck + Agent assessment 1, store initial
POST /v1/cases/{caseId}/question    # contact gate; emit the single question
POST /v1/cases/{caseId}/reply       # body: { questionId, text } -> assessment 2 + final
POST /v1/cases/{caseId}/no-reply    # manual demo control -> final = initial
GET  /v1/cases/{caseId}             # initial, after_reply, final, policy, question state`),
    h2('6.3 Proposed Error Handling'),
    ...code(`{ "error": { "code": "SCHEMA_INVALID", "message": "evidence[0].verification is not allowed",
             "field": "evidence[0].verification", "caseId": "DEMO-001", "requestId": "uuid" } }`),
    table(['Code', 'HTTP', 'Meaning'], [
      ['VALIDATION_ERROR', '400', 'Malformed request or case input'],
      ['SCHEMA_INVALID', '422', 'Agent output failed the six-field schema or enum check'],
      ['SOURCE_REF_UNKNOWN', '422', 'An evidence source_ref does not resolve for this case and stage'],
      ['STATE_CONFLICT', '409', 'Transition not allowed from the current status, or a guard matched 0 rows'],
      ['POLICY_BLOCKED', '200', 'Not an error: policy_gate = BLOCKED with the reason'],
      ['NOT_FOUND', '404', 'Unknown case'],
      ['AGENT_UNAVAILABLE', '502', 'LLM call failed after bounded retries; case stays in its state'],
      ['INTERNAL_ERROR', '500', 'Unexpected failure'],
    ], [2800, 900, 5938], { size: 19 }),

    h1('7. Security Architecture'),
    h2('7.1 Trust Boundaries'),
    ...bullets([
      '**Untrusted inputs:** courier notes, buyer replies and any text field. They are data, never instructions. The prompt tells the Agent to ignore commands found there, and the schema limits what output can contain.',
      '**Untrusted output:** the LLM response is validated by code before it is stored or shown.',
      '**Authority:** only the policy engine grants eligibility and final action. A HIGH confidence never overrides policy.',
    ]),
    h2('7.2 Security Measures'),
    table(['Area', 'Measure', 'Status'], [
      ['Data', 'Synthetic data only; fictional IDs; no real phone, address, GPS or business names. Contact and location data are personal data (Vietnam Decree 13)', 'In place'],
      ['Actions', 'Policy gate blocks address change, dispatch, delivery change, exact slot, real buyer message, return authorisation, refund', 'In place (gate); labels in UI'],
      ['Prompt injection', 'Notes and replies treated as data; schema-constrained output; source_ref must resolve', 'Prompt written; validator is Target'],
      ['Evaluation integrity', 'Golden file never given to the Agent; examples in the prompt are invented', 'In place'],
      ['Secrets', 'LLM API key only on the server. Vite exposes only VITE_ variables to the browser bundle, so the key must never be a VITE_ variable', 'Rule for Target'],
      ['SQL injection', 'Bind parameters only; never build SQL from notes or replies', 'Rule for Target'],
      ['Input validation', 'validateScenario in the MVP; schema and enum validation for Agent output', 'Partial'],
      ['Audit', 'Every assessment and policy result stored with source references', 'In place (decision records)'],
    ], [1900, 5638, 2100], { size: 19 }),

    h1('8. Performance and Scaling'),
    p('No latency, throughput or concurrency target has been set or measured. The MVP is a local demo. The following are **design constraints** that keep the cost per case bounded:'),
    ...bullets([
      'At most **two Agent calls per case** (initial and after reply); a no-reply case uses one. No loops, no third inference.',
      'At most one buyer question and a demo policy profile with a maximum of 3 attempts.',
      'Engine functions are pure and synchronous, so they scale with the UI or service that hosts them.',
      'The Agent runner is stateless; cases are independent, so it can run behind a queue.',
    ]),
    h3('Scaling path'),
    ...bullets([
      'Measure first: record latency and token usage of the live Agent on the 30 cases; then set targets.',
      'Run Agent calls from a worker queue; keep state changes in short transactions.',
      'Version policy profiles per carrier or region through `policy_version`.',
      'Run evaluations in parallel (the simulation already ran 30 cases concurrently).',
    ]),
    p('The system prompt is about 28 KB. Trimming it and measuring the effect on the evaluation is a cost and latency lever.'),

    h1('9. Deployment Pipeline'),
    h2('9.1 Environments'),
    table(['Environment', 'How', 'Status'], [
      ['Development', '`npm run dev` (Vite dev server)', 'In use'],
      ['Verification', '`npm run typecheck`, `npm run test:unit`, `npm run build`, Playwright browser journey', 'In use'],
      ['Demo', 'Local run on the presenter machine; no hosting', 'In use'],
      ['Staging / Production', 'Not defined', 'None'],
    ], [2300, 5538, 1800], { size: 19 }),
    h2('9.2 CI/CD Flow (Proposed)'),
    ...numbered([
      'Push or pull request to the repository.',
      'GitHub Actions: install with the lockfile, then `npm run typecheck`.',
      '`npm run test:unit`.',
      '`npx playwright test e2e/order-rescue-demo.spec.ts --output=<isolated dir>` (the shared `test-results/` output has a known trace-close ENOENT issue).',
      '`npm run build`; publish the static bundle only when a hosting target exists.',
      'Optional: run the evaluation harness on the 30 cases and attach the report.',
    ]),
    h2('9.3 Commands'),
    ...code(`npm ci
npm run typecheck
npm run test:unit
npm run build
npx playwright test e2e/order-rescue-demo.spec.ts --output=/tmp/order-rescue-results`),

    h1('10. Monitoring and Observability'),
    h2('10.1 Today'),
    ...bullets([
      'Decision records and the audit timeline show input summary, assessment, policy result and labels for each step.',
      'The evaluation harness reports exact-match rates per field and stage, and classifies mismatches as prompt gap, questionable label or model variance.',
    ]),
    h2('10.2 Proposed for the live Agent'),
    ...bullets([
      'Log per call: case id, stage, prompt version, model id, latency, token counts, schema-validation result, retry count (no PII).',
      'Track: schema-invalid rate, unknown source_ref rate, candidate_action distribution, share of ESCALATE_REVIEW.',
      'Alert when the schema-invalid rate rises, when Agent calls fail repeatedly, or when the distribution of actions shifts sharply.',
    ]),

    h1('11. Future Migration Path'),
    ...numbered([
      '**Align the MVP with the v2.2 contract:** replace the v1 vocabularies in `src/domain/types.ts` and `assessCase` with the approved hypotheses and actions.',
      '**Add the validator** and run the Agent on the 30 cases through a server-side proxy.',
      '**Choose the database engine,** write DDL with NOT NULL and unique constraints, and re-run the query recipes and guards on that engine.',
      '**Add the backend service** (modules in 4.1) with transactions and the proposed endpoints.',
      '**Shadow mode** on authorised historical data; replace draft labels with Ops-reviewed labels.',
      '**Pilot** with a human-controlled Ops console and a real contact channel behind the contact gate.',
    ]),

    h1('12. Open Decisions and Known Gaps'),
    table(['#', 'Gap', 'Impact / next step'], [
      ['1', 'Two vocabularies coexist: the MVP engine uses v1 causes and 6 actions; the v2.2 contract uses 7 hypotheses and 5 actions', 'The UI demo and the Agent contract disagree. Migrate the engine (section 11, step 1)'],
      ['2', 'Golden labels are drafts (DRAFT_NEEDS_USER_REVIEW). Flagged: DEMO-024 vs 027, HOLD vs CLARIFY in 023 and 026, emoji reply in 030', 'Evaluation scores are only as good as the labels. The review report lists 12 questions for Hải'],
      ['3', 'Prompt v2 simulation: all six fields agree in 14/30 initial and 21/24 after reply; confidence and missing_info are weakest', 'Do not tune further until labels are reviewed, to avoid fitting wrong labels'],
      ['4', 'Pre-check blocked path and contact-gate denial have no defined state or tests', 'Define the target status and add a few cases outside the 30'],
      ['5', 'Database engine, DDL and constraints not chosen', 'Decide, then validate on that engine'],
      ['6', '`package.json` uses `latest` for all dependencies', 'Pin versions'],
      ['7', 'No CI', 'Add the proposed pipeline'],
      ['8', 'Live Agent integration and its measurements do not exist yet', 'No latency, cost or live accuracy claim until measured'],
      ['9', 'Hackathon rules: work must be built on-site in a new public repository; any pre-existing work must be declared', 'Prepare README and declaration stating what was built during the event'],
    ], [500, 5000, 4138], { size: 19 }),
    spacer(),
    h1('Document Info'),
    kv([
      ['Author', 'Engineering Team (Lucas, Phúc, Hải, Kha)'],
      ['Version', '0.1'],
      ['Last Updated', 'October 29, 2026'],
      ['Review Date', 'To be set; before the 31 October 2026 hackathon rehearsal'],
      ['Companion documents', 'Product Vision; Business Rules v2.2; review report; prompt evaluation report; src/agent/prompts/README.md'],
    ]),
  ];

  const f = hdrFtr('Software Architecture Document');
  return new Document({ creator: 'Order Rescue team', title: 'Order Rescue - Software Architecture Document', styles, numbering: numberingFor(),
    sections: [
      { properties: portrait, ...f, children: s1 },
      { properties: landscape, ...f, children: figArch },
      { properties: portrait, ...f, children: s3 },
      { properties: landscape, ...f, children: figFlow },
      { properties: portrait, ...f, children: s5 },
      { properties: landscape, ...f, children: figErd },
      { properties: portrait, ...f, children: s7 },
    ] });
}

(async () => {
  const pv = productVision();     // build documents first so numbering refs are collected
  const sa = sad();
  const pv2 = productVision(), sa2 = sad();   // rebuild with the full list of numbered-list references
  fs.writeFileSync(path.join(OUT, 'Order_Rescue_Product_Vision.docx'), await Packer.toBuffer(pv2));
  fs.writeFileSync(path.join(OUT, 'Order_Rescue_Software_Architecture_Document.docx'), await Packer.toBuffer(sa2));
  console.log('written');
})();
