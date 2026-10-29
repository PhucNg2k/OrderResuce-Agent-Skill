"""Order Rescue pitch deck generator (Sea x OpenAI Codex Hackathon briefing theme).

Run: python build_deck.py  ->  Order_Rescue_Pitch_Deck.pptx (next to this file).
Visual design only; content and speaker notes are unchanged.
"""
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
FONT = 'Open Sans'

# Theme palette (from the briefing deck)
BLACK = RGBColor(0, 0, 0)
WHITE = RGBColor(255, 255, 255)
ORANGE = RGBColor(0xFF, 0x55, 0x20)
TEAL = RGBColor(0x00, 0xD4, 0xA0)
SKY = RGBColor(0x3A, 0xB5, 0xF0)
BLUE = RGBColor(0x00, 0x77, 0xDD)
MUTED = RGBColor(0x8A, 0xAA, 0xCC)
FINE = RGBColor(0x7A, 0x8F, 0xA8)
CARD = RGBColor(0x0B, 0x12, 0x20)
BORDER = RGBColor(0x1E, 0x3A, 0x5F)
HILITE = RGBColor(0x08, 0x2A, 0x40)   # tinted fill for "agent" nodes

W, H = 9144000, 5143500
IN = 914400
prs = Presentation()
prs.slide_width = W
prs.slide_height = H
blank = prs.slide_layouts[6]
PAGENUMS = []

NOTES = {
    'Order Rescue':
        '[0:00-0:15] Good afternoon. We are Lucas, Phuc, Hai and Kha. Order Rescue is a policy-gated decision layer for failed last-mile deliveries, designed to host an LLM agent. It recommends to Ops; it never acts on its own. Everything runs on synthetic data and is labelled as such. Be upfront: today a deterministic assessor stands in for the LLM agent.',
    'Why this fits the build directions':
        '[0:15-0:25] (10 seconds) We align with Autonomous and Adaptive AI: an agent that reasons, asks, then reassesses within limits. It also reflects Deep Domain AI: the rules come from how delivery Ops actually reasons, such as silence is not refusal.',
    'Problem: a failed attempt is a status, not a cause':
        '[0:25-0:50] When a first delivery attempt fails, Ops sees a code like recipient unavailable or refused. Public Shopee guidance itself says delivery status can be incorrect or incomplete. Re-attempting blindly wastes a courier trip; closing too early loses a sale. Four parties feel it: buyers, couriers, Ops, sellers (detail on backup slide).',
    'Why rescue is hard, and who is hurt':
        '[BACKUP, not in the timed pitch] Four parties feel this. Buyers wait for parcels; couriers burn attempts; Ops triage case by case without evidence; sellers risk returns. The hard part is that one status maps to many causes, and the buyer is the only person who can resolve some of them.',
    'Priorities: what we built, what we left out':
        '[0:50-1:05] We prioritised a trustworthy decision, not a flashy integration. In scope: evidence-based assessment, one buyer question, a deterministic policy gate and an audit trail. Out of scope: anything that touches the real world.',
    'Solution: the two-assessment flow':
        '[1:05-1:45] Walk the diagram. Raw data goes through a pre-check; malformed or closed cases never reach the AI. Agent assessment 1 produces evidence and a hypothesis. If information is missing, the backend contact gate allows exactly one buyer question. A reply triggers assessment 2; a manual no-reply keeps assessment 1. Then the policy engine decides what is permitted, and Ops receives the recommendation. Say plainly: the deterministic assessor plays the agent role today; the LLM agent is next. The novelty is the bounded design: one buyer question, fixed vocabularies, policy decides.',
    "The agent's output: six fields, fixed vocabularies":
        '[1:45-1:55] The agent (today the deterministic assessor) returns exactly six fields, and values must come from approved lists: 7 hypotheses, 8 missing-info codes, 5 candidate actions. Confidence measures support for the hypothesis, not delivery success.',
    'Policy gate: the LLM never grants itself permission':
        '[1:55-2:15] This is the trust story. High confidence does not override policy. Retry needs direct buyer intent, availability and sufficient delivery info. Anything outside the MVP, such as changing an address, is blocked and escalated. These checks are plain deterministic code that we test.',
    'MVP architecture':
        '[2:15-2:30] Today it is a local Vite, React and TypeScript app. Fixtures stand in for the data stores; a deterministic assessor stands in for the LLM agent; the policy gate and audit trail are real local code. The target design has the same three layers, backed by the 9-table data model.',
    'How it scales':
        '[BACKUP, not in the timed pitch] Scaling is a path, not a claim. The evaluation harness does not exist yet; only the 30 cases and unit tests do. Real carrier data replaces fixtures, a queue handles volume, each policy version gets its own profile, and an evaluation harness reuses our 30 synthetic cases as a regression suite.',
    'Integration: how it would plug into Ops':
        '[BACKUP, not in the timed pitch] Integration is designed, not built. The agent would read delivery-event and order stores, ask the buyer through a backend-controlled channel, and show recommendations in an Ops console with a human decision. State clearly: the MVP integrates with nothing live.',
    'Where AI could create value in operations':
        '[5:45-6:00] (15 seconds) These are hypotheses to validate with real data, not results. We deliberately show no savings or accuracy numbers because we have none. What we can show is the mechanism: evidence-backed, explainable decisions.',
    'How we used Codex':
        '[2:30-3:15] (45 seconds) TEAM MUST CONFIRM before presenting which files Codex generated versus Claude Code; the repo also contains .claude/ and CLAUDE.md, so do not imply Codex did everything. Verifiable facts: 15 Codex agent configs in .codex/agents, 34 skills in .agents/skills, a Vitest suite (23 tests in 6 files passed on 29 Oct; re-run npm run test:unit immediately before presenting and quote the fresh number) and a Playwright spec in e2e/. Show the repo view on screen. Do not state accuracy or correctness.',
    'Demo flow: verified vs simulated':
        '[3:15-5:45] (2.5 minutes, live) Show one case end to end: evidence, assessment, policy result, audit. Then the blocked request. Use the truth legend: real local code versus simulated data versus future.',
    'Roadmap and Q&A backup':
        '[BACKUP, after the end; Q&A] Likely questions: How is the LLM kept honest? Policy gate and fixed vocabularies. What about real data? Not accessed; next step needs permission. Where is the AI? The v2.2 contract, six fixed-vocabulary fields and the recommendation prompt branch define the LLM part; a deterministic assessor stands in today. Where do numbers come from? We claim none.',
}

def E(v):
    return Emu(int(v * IN))


def P(runs, after=4, align=None):
    """Paragraph spec. runs: one (text,size,color,bold) tuple or a list of them."""
    if isinstance(runs, tuple):
        runs = [runs]
    return {'runs': runs, 'after': after, 'align': align}


def fill_tf(tf, paras, align=PP_ALIGN.LEFT):
    if isinstance(paras, dict):
        paras = [paras]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = p['align'] or align
        para.space_after = Pt(p['after'])
        para.space_before = Pt(0)
        for (t, sz, col, b) in p['runs']:
            r = para.add_run()
            r.text = t
            r.font.size = Pt(sz)
            r.font.color.rgb = col
            r.font.bold = b
            r.font.name = FONT


def tb(s, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    t = s.shapes.add_textbox(E(x), E(y), E(w), E(h))
    tf = t.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Emu(40000)
    tf.margin_top = tf.margin_bottom = Emu(20000)
    fill_tf(tf, paras, align)
    return t


def card(s, x, y, w, h, paras=None, accent=None, fill=CARD, line=BORDER, rule=None,
         anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT, mx=0.14, my=0.1, lw=1.0):
    """Dark rounded card with thin border; optional accent rule on the top edge."""
    b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, E(x), E(y), E(w), E(h))
    b.adjustments[0] = min(0.12, 0.09 / min(w, h) * 1.0)
    b.fill.solid()
    b.fill.fore_color.rgb = fill
    if line is None:
        b.line.fill.background()
    else:
        b.line.color.rgb = line
        b.line.width = Pt(lw)
    b.shadow.inherit = False
    tf = b.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = E(mx)
    tf.margin_top = tf.margin_bottom = E(my)
    if paras:
        fill_tf(tf, paras, align)
    if rule is not None:
        r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, E(x + 0.18), E(y), E(0.55), E(0.04))
        r.fill.solid()
        r.fill.fore_color.rgb = rule
        r.line.fill.background()
        r.shadow.inherit = False
    return b


def numcard(s, x, y, w, h, num, title, body, accent, tsize=16):
    paras = [P((num, 22, accent, True), 2), P((title, tsize, WHITE, True), 4)]
    if body:
        paras.append(P((body, 14, MUTED, False), 0))
    return card(s, x, y, w, h, paras, rule=accent, my=0.14)


def node(s, x, y, w, h, title, sub, accent, hi=False, solid=False, tsize=14, ssize=12):
    """Diagram node. solid=True -> accent-filled with black text."""
    if solid:
        paras = [P((title, tsize, BLACK, True), 2)]
        if sub:
            paras.append(P((sub, ssize, BLACK, False), 0))
        return card(s, x, y, w, h, paras, fill=accent, line=None, anchor=MSO_ANCHOR.MIDDLE,
                    align=PP_ALIGN.CENTER, mx=0.08, my=0.05)
    paras = [P((title, tsize, WHITE, True), 2)]
    if sub:
        paras.append(P((sub, ssize, MUTED, False), 0))
    return card(s, x, y, w, h, paras, fill=HILITE if hi else CARD, line=accent,
                anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER, mx=0.08, my=0.05, lw=1.5)


def arrow(s, x1, y1, x2, y2, color=SKY, head=True, wpt=2.25):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    c.line.color.rgb = color
    c.line.width = Pt(wpt)
    if head:
        ln = c.line._get_or_add_ln()
        t = etree.SubElement(ln, qn('a:tailEnd'))
        t.set('type', 'triangle')
        t.set('w', 'med')
        t.set('len', 'med')
    return c


def bullets(s, x, y, w, h, items, size=16, color=WHITE, dot=ORANGE, after=8):
    paras = [P([('•  ', size, dot, True), (i, size, color, False)], after) for i in items]
    return tb(s, x, y, w, h, paras)


def slide(title, tag=None):
    s = prs.slides.add_slide(blank)
    s.shapes.add_picture(os.path.join(ASSETS, 'bg_content.png'), 0, 0, W, H)
    if tag:
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, E(0.6), E(0.35), E(0.3), E(0.04))
        bar.fill.solid(); bar.fill.fore_color.rgb = ORANGE; bar.line.fill.background()
        bar.shadow.inherit = False
        tb(s, 0.98, 0.2, 6.5, 0.3, P((tag.upper(), 12, ORANGE, True), 0))
    tb(s, 0.6, 0.5, 8.4, 0.98, P((title, 26, WHITE, True), 0))
    pn = tb(s, 8.7, 5.2, 0.7, 0.28, P((str(len(prs.slides)), 10, FINE, False), 0), align=PP_ALIGN.RIGHT)
    PAGENUMS.append(pn)
    tb(s, 4.2, 5.2, 4.5, 0.28,
       P(("Order Rescue | synthetic data only | local MVP", 10, FINE, False), 0), align=PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text = NOTES[title]
    return s


def est_lines(text, size, width_in, bold=False):
    cpl = max(1, int(width_in * 72 / (size * (0.6 if bold else 0.55))))
    return max(1, math.ceil(len(text) / cpl))


# ---------------------------------------------------------------- 1 Cover
s = prs.slides.add_slide(blank)
s.shapes.add_picture(os.path.join(ASSETS, 'bg_cover.png'), 0, 0, W, H)
s.notes_slide.notes_text_frame.text = NOTES["Order Rescue"]
PAGENUMS.append(None)
C = PP_ALIGN.CENTER
tb(s, 2.2, 1.05, 5.6, 0.3, P(("Sea x OpenAI Codex Hackathon | 31 Oct 2026".upper(), 12, ORANGE, True), 0), C)
tb(s, 2.0, 1.32, 6.0, 0.8, P(("Order Rescue", 40, WHITE, True), 0), C)
tb(s, 1.9, 2.1, 6.2, 0.45, P(("Adaptive Delivery Recovery Agent", 20, TEAL, True), 0), C)
tb(s, 2.2, 2.6, 5.6, 0.75,
   P(("Works out why a delivery failed, asks the buyer one good question, and hands Ops an explainable, policy-checked recommendation.", 14, WHITE, False), 0), C)
tb(s, 2.2, 3.35, 5.6, 0.75,
   P(("Honest status: today a deterministic assessor stands in for the LLM agent; the LLM agent is the next step.", 14, ORANGE, True), 0), C)
team = [("Lucas", "Scope and demo flow", SKY), ("Phuc", "AI feasibility", TEAL),
        ("Hai", "Business rules and test cases", ORANGE), ("Kha", "Concept owner", SKY)]
for i, (n, r, c) in enumerate(team):
    card(s, 2.3 + i * 1.4, 4.0, 1.3, 1.08,
         [P((n, 14, WHITE, True), 1), P((r, 12, MUTED, False), 0)], rule=c,
         align=C, mx=0.06, my=0.1)
tb(s, 2.8, 5.2, 4.4, 0.28, P(("Order Rescue | synthetic data only | local MVP", 10, FINE, False), 0), C)

# ---------------------------------------------------------------- 2 Build direction
s = slide("Why this fits the build directions", "1  Intro")
cards2 = [("01", "Autonomous & Adaptive AI", "Reassesses after one buyer reply; stays inside hard limits", SKY),
          ("02", "Deep Domain AI", "Ops logic encoded: courier notes are unverified, silence is not refusal", TEAL),
          ("03", "AI-Native Operations", "Recommendation with evidence, not a bare status code", ORANGE)]
for i, (n, t, b, c) in enumerate(cards2):
    numcard(s, 0.6 + i * 3.0, 1.6, 2.8, 2.3, n, t, b, c)
card(s, 0.6, 4.15, 8.8, 0.6,
     [P([("Primary: ", 16, TEAL, True), ("Autonomous & Adaptive AI.  ", 16, WHITE, True),
         ("Secondary: ", 16, SKY, True), ("Deep Domain AI.", 16, WHITE, True)], 0)],
     anchor=MSO_ANCHOR.MIDDLE, mx=0.25)

# ---------------------------------------------------------------- 3 Problem
s = slide("Problem: a failed attempt is a status, not a cause", "2  Problem statement")
bullets(s, 0.6, 1.65, 5.3, 3.2, ["First attempts fail; the raw code is all Ops sees.",
                                "Courier notes are unverified and often vague.",
                                "Wrong guess: a wasted re-attempt, or a lost order.",
                                "No structured record of why a decision was made."], size=16, after=10)
card(s, 6.3, 1.65, 3.1, 1.1, [P(("recipient unavailable", 18, WHITE, True), 0)],
     line=ORANGE, lw=1.5, anchor=MSO_ANCHOR.MIDDLE, align=C, rule=ORANGE)
tb(s, 6.3, 2.95, 3.1, 1.4,
   P(("Could mean: at work, wrong landmark, unreachable phone, or a disrupted route.", 14, MUTED, False), 0))

# ---------------------------------------------------------------- 4 Who is hurt (backup)
s = slide("Why rescue is hard, and who is hurt", "Backup | Who is hurt")
cols4 = [SKY, TEAL, ORANGE, SKY]
for i, (t, d) in enumerate([("Buyers", "Wait, get re-contacted blindly"), ("Couriers", "Spend limited attempts"),
                            ("Ops", "Triage case by case"), ("Sellers", "Risk returns and lost sales")]):
    numcard(s, 0.6 + i * 2.25, 1.6, 2.05, 1.75, "%02d" % (i + 1), t, d, cols4[i])
bullets(s, 0.6, 3.65, 8.8, 1.3, ["One status maps to many possible causes.",
                                "Only the buyer can resolve some unknowns.",
                                "Attempts are limited; silence must not be read as refusal."], size=16, after=8)

# ---------------------------------------------------------------- 5 Priorities
s = slide("Priorities: what we built, what we left out", "3  Priorities")
for x, head, col, items in [
        (0.6, "IN the MVP", TEAL, ["Evidence-backed assessment", "One buyer question, max", "Deterministic policy gate",
                                    "Recommendation to Ops only", "Audit trail per decision"]),
        (5.1, "Deliberately OUT", ORANGE, ["Live Shopee/SPX data or APIs", "Real buyer messaging",
                                           "Courier dispatch, exact slots", "Address or COD changes",
                                           "Returns and refunds"])]:
    paras = [P((head, 20, col, True), 10)] + \
            [P([('•  ', 16, col, True), (i, 16, WHITE, False)], 6) for i in items]
    card(s, x, 1.6, 4.3, 3.25, paras, rule=col, mx=0.25, my=0.22)

# ---------------------------------------------------------------- 6 Flow diagram
s = slide("Solution: the two-assessment flow", "4  Solution")
RW, RY, RH = 1.44, 1.5, 1.05
xs = [0.6, 2.44, 4.28, 6.12, 7.96]
labels = [("Raw data", "status, notes, lifecycle"), ("Pre-check", "exclude invalid cases"),
          ("Agent assessment 1", "6-field output"), ("Contact gate", "backend allows 1 question"),
          ("One buyer question", "from missing_info")]
his = [False, False, True, False, False]
for i, (x, (a, b)) in enumerate(zip(xs, labels)):
    node(s, x, RY, RW, RH, a, b, SKY, hi=his[i])
R2, R2H = 2.85, 0.9
node(s, 7.96, R2, RW, R2H, "Reply", "Agent assessment 2", TEAL, hi=True)
node(s, 5.8, R2, 1.9, R2H, "No reply (manual)", "keep assessment 1", ORANGE)
node(s, 2.9, R2, 2.4, R2H, "Policy engine", "deterministic gate", TEAL, tsize=16, ssize=14)
node(s, 0.6, R2, 1.7, R2H, "Ops", "recommendation", TEAL, solid=True, tsize=16, ssize=14)
for i in range(4):
    arrow(s, xs[i] + RW, RY + RH / 2, xs[i + 1], RY + RH / 2)
arrow(s, 8.68, RY + RH, 8.68, R2, TEAL)
arrow(s, 8.2, RY + RH, 6.75, R2, ORANGE)
RT = R2 + R2H + 0.12
arrow(s, 8.68, R2 + R2H, 8.68, RT, TEAL, head=False)
arrow(s, 8.68, RT, 4.1, RT, TEAL, head=False)
arrow(s, 4.1, RT, 4.1, R2 + R2H, TEAL)
arrow(s, 5.8, R2 + R2H / 2, 5.3, R2 + R2H / 2, ORANGE)
arrow(s, 2.9, R2 + R2H / 2, 2.3, R2 + R2H / 2, TEAL)
tb(s, 0.8, 4.0, 8.6, 1.05, [
    P(("Novelty: one bounded buyer question + fixed vocabularies. LLM proposes; policy decides; Ops executes.", 14, TEAL, True), 3),
    P(("Today a deterministic assessor stands in for the LLM agent (next step). The agent never acts.", 14, MUTED, False), 0)])

# ---------------------------------------------------------------- 7 Six fields
s = slide("The agent's output: six fields, fixed vocabularies", "4  Solution")
fields = ["evidence", "hypothesis", "confidence", "missing_info", "question_key", "candidate_action"]
fcol = [SKY, SKY, SKY, TEAL, TEAL, ORANGE]
for i, n in enumerate(fields):
    card(s, 0.6 + (i % 3) * 3.0, 1.6 + (i // 3) * 0.75, 2.8, 0.62,
         [P([("%02d  " % (i + 1), 14, fcol[i], True), (n, 14, WHITE, True)], 0)],
         anchor=MSO_ANCHOR.MIDDLE, mx=0.18, my=0.05)
for i, (t, d, c) in enumerate([("7 hypotheses", "availability, address, contact, buyer intent, payment, logistics, unknown", TEAL),
                               ("8 missing_info", "intent, availability, address, contact, COD, access, logistics, cause", SKY),
                               ("5 candidate actions", "clarify, standard re-attempt, hold, escalate review, no action", ORANGE)]):
    card(s, 0.6 + i * 3.0, 3.25, 2.8, 1.65,
         [P((t, 16, c, True), 4), P((d, 14, MUTED, False), 0)], rule=c, my=0.15)

# ---------------------------------------------------------------- 8 Policy gate
s = slide("Policy gate: the LLM never grants itself permission", "4  Solution")
for x, head, col, items in [
        (0.6, "Agent proposes", SKY, ["Evidence and hypothesis", "Missing information", "One question",
                                      "Candidate action", "Today: rule-based; LLM is next"]),
        (5.1, "Policy engine decides", TEAL, ["Eligibility and attempts left", "Silence is not refusal",
                                              "Courier note is unverified",
                                              "Blocks address change, dispatch, refund"])]:
    paras = [P((head, 18, col, True), 8)] + \
            [P([('•  ', 16, col, True), (i, 16, WHITE, False)], 4) for i in items]
    card(s, x, 1.6, 4.3, 2.75, paras, rule=col, mx=0.25, my=0.2)
card(s, 0.6, 4.5, 8.8, 0.5, [P(("High confidence never overrides policy.", 18, ORANGE, True), 0)],
     line=ORANGE, lw=1.5, anchor=MSO_ANCHOR.MIDDLE, align=C)

# ---------------------------------------------------------------- 9 Architecture
s = slide("MVP architecture", "5  MVP architecture")
CW = 2.7
cx = [0.6, 3.65, 6.7]
r1y, r1h = 1.5, 1.6
node(s, cx[0], r1y, CW, r1h, "Data layer", "9-table model: buyers, orders, delivery events, rescue cases, interactions", SKY, ssize=14)
node(s, cx[1], r1y, CW, r1h, "Backend", "state, contact gate, question budget, writes", SKY, ssize=14)
node(s, cx[2], r1y, CW, r1h, "Agent (LLM: next step)", "reads allowed sources; outputs 6 fields", SKY, hi=True, ssize=14)
r2y, r2h = 3.4, 1.15
node(s, cx[0], r2y, CW, r2h, "Today: local React app", "fixtures, rule-based assessor", ORANGE, ssize=14)
node(s, cx[1], r2y, CW, r2h, "Policy engine", "versioned, deterministic", TEAL, ssize=14)
node(s, cx[2], r2y, CW, r2h, "Ops console", "recommendation, evidence, audit", TEAL, solid=True, ssize=14)
arrow(s, cx[0] + CW, r1y + r1h / 2, cx[1], r1y + r1h / 2)
arrow(s, cx[1] + CW, r1y + r1h / 2, cx[2], r1y + r1h / 2)
arrow(s, cx[1] + CW / 2, r1y + r1h, cx[1] + CW / 2, r2y, TEAL)
arrow(s, cx[1] + CW, r2y + r2h / 2, cx[2], r2y + r2h / 2, TEAL)
tb(s, 0.6, 4.65, 8.8, 0.35, P(("Golden test cases are kept out of the assessor's input.", 14, MUTED, False), 0))

# ---------------------------------------------------------------- 10 Scale (backup)
s = slide("How it scales", "Backup | Scale")
steps = [("Now", "Local MVP, fixtures", ORANGE), ("Next", "Real carrier data feeds", SKY),
         ("Then", "Case queue, async agent runs", SKY), ("Then", "Policy profile per version", SKY),
         ("Then", "Evaluation harness, 30 cases (not built yet)", TEAL)]
SW, SG = 1.52, 0.3
for i, (a, b, c) in enumerate(steps):
    x = 0.6 + i * (SW + SG)
    numcard(s, x, 1.6, SW, 2.05, "%02d" % (i + 1), a, b, c)
    if i < 4:
        arrow(s, x + SW, 2.6, x + SW + SG, 2.6, SKY)
card(s, 0.6, 3.95, 8.8, 0.8,
     [P(("The 30 synthetic cases cover 24 with a buyer reply and 6 manual no-reply paths.", 16, WHITE, False), 0)],
     anchor=MSO_ANCHOR.MIDDLE, mx=0.25, rule=TEAL)

# ---------------------------------------------------------------- 11 Integration (backup)
s = slide("Integration: how it would plug into Ops", "Backup | Integration")
node(s, 0.6, 1.6, 2.6, 1.15, "Order and delivery-event stores", "read only", SKY, tsize=15, ssize=14)
node(s, 3.7, 1.6, 2.6, 1.15, "Order Rescue service", "agent + policy engine", SKY, hi=True, tsize=15, ssize=14)
node(s, 6.8, 1.6, 2.6, 1.15, "Ops console", "human approves or rejects", TEAL, solid=True, tsize=15, ssize=14)
arrow(s, 3.2, 2.175, 3.7, 2.175)
arrow(s, 6.3, 2.175, 6.8, 2.175, TEAL)
node(s, 3.7, 3.15, 2.6, 1.15, "Buyer messaging channel", "via backend contact gate", ORANGE, tsize=15, ssize=14)
arrow(s, 5.0, 2.75, 5.0, 3.15, ORANGE)
tb(s, 0.6, 4.3, 8.8, 0.65, P(("Today: no Shopee/SPX data, API, messaging or dispatch. All of the above is FUTURE / UNVERIFIED.", 16, ORANGE, True), 0))

# ---------------------------------------------------------------- 12 Impact
s = slide("Where AI could create value in operations", "7  Impact (hypotheses to validate)")
imp = [("Fewer wasted re-attempts", "9 of 30 test cases change hypothesis after the reply, e.g. DEMO-002", SKY),
       ("Faster Ops triage", "Evidence pre-assembled for all 30 cases", TEAL),
       ("Explainable decisions", "Six traceable fields per case", ORANGE),
       ("Better buyer experience", "One question; 6 no-reply paths handled", SKY)]
for i, (t, d, c) in enumerate(imp):
    card(s, 0.6 + (i % 2) * 4.5, 1.6 + (i // 2) * 1.45, 4.3, 1.3,
         [P([("%02d  " % (i + 1), 18, c, True), (t, 16, WHITE, True)], 4), P((d, 14, MUTED, False), 0)],
         rule=c, my=0.16, mx=0.2)
tb(s, 0.6, 4.55, 8.8, 0.5,
   P(("Case counts come from the 30 synthetic test cases. No impact numbers claimed; all four are hypotheses.", 14, MUTED, False), 0))

# ---------------------------------------------------------------- 13 Codex
s = slide("How we used Codex", "8  Use of Codex")
rows = ["Codex harness in the repo: 15 agent configs (.codex/agents), 34 skills (.agents/skills).",
        "Spec-driven loop encoded there: research, plan, validate, execute.",
        "Vitest: 23 tests in 6 files pass (npm run test:unit, run 29 Oct).",
        "Playwright spec for the demo flow in e2e/.",
        "Claude Code was also used here (.claude/ in repo): we show the repo, not sole authorship."]
ry = 1.6
for i, t in enumerate(rows):
    h = max(0.5, est_lines(t, 15, 7.7) * 15 * 1.25 / 72 + 0.24)
    c = [SKY, SKY, TEAL, TEAL, ORANGE][i]
    card(s, 0.6, ry, 8.8, h, None)
    tb(s, 0.75, ry, 0.7, h, P(("%02d" % (i + 1), 20, c, True), 0), anchor=MSO_ANCHOR.MIDDLE)
    tb(s, 1.5, ry, 7.8, h, P((t, 15, WHITE, False), 0), anchor=MSO_ANCHOR.MIDDLE)
    ry += h + 0.1

# ---------------------------------------------------------------- 14 Demo
s = slide("Demo flow: verified vs simulated", "9  Demo")
for i, (t, d, c) in enumerate([("REAL - LOCAL", "UI, assessor, policy gate, audit, tests", TEAL),
                               ("SIMULATED", "Orders, events, notes, buyer replies", ORANGE),
                               ("FUTURE / UNVERIFIED", "Shopee/SPX data, messaging, dispatch", SKY)]):
    card(s, 0.6 + i * 3.0, 1.6, 2.8, 1.3, [P((t, 15, c, True), 4), P((d, 14, MUTED, False), 0)], rule=c, my=0.16)
for i, t in enumerate(["Pick a case: raw status plus courier note.", "See evidence, hypothesis, missing info.",
                       "Apply buyer reply; watch reassessment.", "Try a blocked request: policy refuses."]):
    numcard(s, 0.6 + i * 2.25, 3.2, 2.05, 1.6, "%02d" % (i + 1), t, None, [SKY, SKY, TEAL, ORANGE][i], tsize=14)

# ---------------------------------------------------------------- 15 Roadmap
s = slide("Roadmap and Q&A backup", "Backup | Roadmap")
for i, (a, b, c) in enumerate([("Next", "Connect the LLM agent to the v2.2 contract", SKY),
                               ("Then", "Run all 30 cases through an evaluator", TEAL),
                               ("Later", "Pilot on real data with permission", ORANGE)]):
    card(s, 0.6 + i * 3.0, 1.6, 2.8, 1.3,
         [P([("%02d  " % (i + 1), 18, c, True), (a, 16, WHITE, True)], 3), P((b, 14, MUTED, False), 0)],
         rule=c, my=0.16, mx=0.2)
qa = [("How do you prevent hallucinated actions? ", "Fixed vocabularies and a deterministic gate."),
      ("Why one question only? ", "Policy profile caps buyer questions at 1."),
      ("What is real today? ", "Local app, policy gate and tests.")]
paras = [P(("Q&A backup:", 16, ORANGE, True), 6)] + \
        [P([(q, 14, WHITE, True), (a, 14, MUTED, False)], 6) for q, a in qa]
card(s, 0.6, 3.1, 8.8, 1.88, paras, mx=0.25, my=0.16, rule=ORANGE)

# ---------------------------------------------------------------- reorder: timed pitch first, backup after
lst = prs.slides._sldIdLst
ids = list(lst)
order = [0, 1, 2, 4, 5, 6, 7, 8, 12, 13, 11, 3, 9, 10, 14]
for e in ids:
    lst.remove(e)
for i in order:
    lst.append(ids[i])
for n, i in enumerate(order, 1):
    if PAGENUMS[i] is not None:
        PAGENUMS[i].text_frame.paragraphs[0].runs[0].text = str(n)
prs.save(os.path.join(HERE, 'Order_Rescue_Pitch_Deck.pptx'))
