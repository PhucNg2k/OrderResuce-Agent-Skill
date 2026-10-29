from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
import os

NAVY=RGBColor(0x0B,0x15,0x26); CYAN=RGBColor(0x00,0xC2,0xE0); ORANGE=RGBColor(0xFF,0x60,0x30)
GREEN=RGBColor(0x00,0xD4,0xA0); WHITE=RGBColor(255,255,255); GREY=RGBColor(0x9A,0xA7,0xB8)
PANEL=RGBColor(0x16,0x25,0x3D); INK=RGBColor(0xE8,0xEE,0xF6)
W,H=9144000,5143500
prs=Presentation(); prs.slide_width=W; prs.slide_height=H
blank=prs.slide_layouts[6]
IN=914400
PAGENUMS=[]

def bg(s):
    f=s.background.fill; f.solid(); f.fore_color.rgb=NAVY

def tb(s,x,y,w,h,text,size=16,color=INK,bold=False,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP):
    t=s.shapes.add_textbox(Emu(int(x*IN)),Emu(int(y*IN)),Emu(int(w*IN)),Emu(int(h*IN)))
    tf=t.text_frame; tf.word_wrap=True; tf.vertical_anchor=anchor
    tf.margin_left=tf.margin_right=Emu(40000); tf.margin_top=tf.margin_bottom=Emu(20000)
    lines=text if isinstance(text,list) else [text]
    for i,l in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align; p.space_after=Pt(6)
        r=p.add_run(); r.text=l; r.font.size=Pt(size); r.font.color.rgb=color; r.font.bold=bold; r.font.name='Calibri'
    return t

def box(s,x,y,w,h,text,fill=PANEL,line=CYAN,size=14,color=WHITE,bold=False,shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    b=s.shapes.add_shape(shape,Emu(int(x*IN)),Emu(int(y*IN)),Emu(int(w*IN)),Emu(int(h*IN)))
    b.fill.solid(); b.fill.fore_color.rgb=fill
    if line is None: b.line.fill.background()
    else: b.line.color.rgb=line; b.line.width=Pt(1.5)
    b.shadow.inherit=False
    tf=b.text_frame; tf.word_wrap=True; tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    tf.margin_left=tf.margin_right=Emu(50000); tf.margin_top=tf.margin_bottom=Emu(25000)
    lines=text if isinstance(text,list) else [text]
    for i,l in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=PP_ALIGN.CENTER
        r=p.add_run(); r.text=l; r.font.size=Pt(size); r.font.color.rgb=color; r.font.bold=bold if i==0 else False; r.font.name='Calibri'
    return b

def arrow(s,x1,y1,x2,y2,color=CYAN,head=True):
    c=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Emu(int(x1*IN)),Emu(int(y1*IN)),Emu(int(x2*IN)),Emu(int(y2*IN)))
    c.line.color.rgb=color; c.line.width=Pt(2)
    ln=c.line._get_or_add_ln()
    if head:
        tail=etree.SubElement(ln,qn('a:tailEnd')); tail.set('type','triangle')
    return c

def slide(title,notes,tag=None):
    s=prs.slides.add_slide(blank); bg(s)
    bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,Emu(110000),Emu(H)); bar.fill.solid(); bar.fill.fore_color.rgb=CYAN; bar.line.fill.background()
    if tag: tb(s,0.35,0.08,6,0.36,tag.upper(),14,ORANGE,True)
    tb(s,0.35,0.5,9.25,0.7,title,24,WHITE,True)
    pn=tb(s,8.4,5.17,1.2,0.36,str(len(prs.slides)),14,GREY,align=PP_ALIGN.RIGHT); PAGENUMS.append(pn)
    tb(s,0.35,5.17,6,0.36,"Order Rescue | synthetic data only | local MVP",14,GREY)
    s.notes_slide.notes_text_frame.text=notes
    return s

def bullets(s,items,x=0.4,y=1.3,w=9.2,h=3.7,size=18):
    tb(s,x,y,w,h,["•  "+i for i in items],size)

# 1 Title
s=slide("Order Rescue","[0:00-0:15] Good afternoon. We are Lucas, Phuc, Hai and Kha. Order Rescue is a policy-gated decision layer for failed last-mile deliveries, designed to host an LLM agent. It recommends to Ops; it never acts on its own. Everything runs on synthetic data and is labelled as such. Be upfront: today a deterministic assessor stands in for the LLM agent.",tag="Sea x OpenAI Codex Hackathon | 31 Oct 2026")
tb(s,0.4,1.4,9.2,0.8,"Adaptive Delivery Recovery Agent",30,CYAN,True)
tb(s,0.4,2.2,9.2,0.9,"Works out why a delivery failed, asks the buyer one good question, and hands Ops an explainable, policy-checked recommendation.",18,INK)
tb(s,0.4,3.1,9.2,0.6,"Honest status: today a deterministic assessor stands in for the LLM agent; the LLM agent is the next step.",14,ORANGE,True)
box(s,0.4,3.85,2.1,0.55,"Lucas",PANEL,CYAN,16,WHITE,True); box(s,2.65,3.85,2.1,0.55,"Phuc",PANEL,CYAN,16,WHITE,True)
box(s,4.9,3.85,2.1,0.55,"Hai",PANEL,CYAN,16,WHITE,True); box(s,7.15,3.85,2.1,0.55,"Kha",PANEL,CYAN,16,WHITE,True)
tb(s,0.4,4.5,9.2,0.62,"Concept owner: Kha. Lucas: scope and demo flow. Phuc: AI feasibility. Hai: business rules and test cases.",14,GREY)

# 2 Build direction
s=slide("Why this fits the build directions","[0:15-0:25] (10 seconds) We align with Autonomous and Adaptive AI: an agent that reasons, asks, then reassesses within limits. It also reflects Deep Domain AI: the rules come from how delivery Ops actually reasons, such as silence is not refusal.",tag="1  Intro")
box(s,0.4,1.4,2.9,2.4,["Autonomous & Adaptive AI","Reassesses after one buyer reply; stays inside hard limits"],PANEL,CYAN,16,WHITE,True)
box(s,3.55,1.4,2.9,2.4,["Deep Domain AI","Ops logic encoded: courier notes are unverified, silence is not refusal"],PANEL,GREEN,16,WHITE,True)
box(s,6.7,1.4,2.9,2.4,["AI-Native Operations","Recommendation with evidence, not a bare status code"],PANEL,ORANGE,16,WHITE,True)
tb(s,0.4,4.1,9.2,0.8,"Primary: Autonomous & Adaptive AI. Secondary: Deep Domain AI.",18,CYAN,True)

# 3 Problem
s=slide("Problem: a failed attempt is a status, not a cause","[0:25-0:50] When a first delivery attempt fails, Ops sees a code like recipient unavailable or refused. Public Shopee guidance itself says delivery status can be incorrect or incomplete. Re-attempting blindly wastes a courier trip; closing too early loses a sale. Four parties feel it: buyers, couriers, Ops, sellers (detail on backup slide).",tag="2  Problem statement")
bullets(s,["First attempts fail; the raw code is all Ops sees.","Courier notes are unverified and often vague.","Wrong guess: a wasted re-attempt, or a lost order.","No structured record of why a decision was made."],size=20,y=1.4,w=5.7)
box(s,6.2,1.5,3.4,1.2,["recipient unavailable"],PANEL,ORANGE,18,WHITE,True)
tb(s,6.2,2.8,3.4,1.2,"Could mean: at work, wrong landmark, unreachable phone, or a disrupted route.",16,INK)

# 4 Why hard / who is hurt
s=slide("Why rescue is hard, and who is hurt","[BACKUP, not in the timed pitch] Four parties feel this. Buyers wait for parcels; couriers burn attempts; Ops triage case by case without evidence; sellers risk returns. The hard part is that one status maps to many causes, and the buyer is the only person who can resolve some of them.",tag="Backup | Who is hurt")
for i,(t,d) in enumerate([("Buyers","Wait, get re-contacted blindly"),("Couriers","Spend limited attempts"),("Ops","Triage case by case"),("Sellers","Risk returns and lost sales")]):
    box(s,0.4+i*2.35,1.5,2.15,1.5,[t,d],PANEL,[CYAN,GREEN,ORANGE,CYAN][i],16,WHITE,True)
bullets(s,["One status maps to many possible causes.","Only the buyer can resolve some unknowns.","Attempts are limited; silence must not be read as refusal."],y=3.3,size=18,h=1.8)

# 5 Priorities
s=slide("Priorities: what we built, what we left out","[0:50-1:05] We prioritised a trustworthy decision, not a flashy integration. In scope: evidence-based assessment, one buyer question, a deterministic policy gate and an audit trail. Out of scope: anything that touches the real world.",tag="3  Priorities")
box(s,0.4,1.4,4.4,0.5,"IN the MVP",GREEN,None,18,NAVY,True)
tb(s,0.4,2.0,4.4,3,["Evidence-backed assessment","One buyer question, max","Deterministic policy gate","Recommendation to Ops only","Audit trail per decision"],16)
box(s,5.2,1.4,4.4,0.5,"Deliberately OUT",ORANGE,None,18,NAVY,True)
tb(s,5.2,2.0,4.4,3,["Live Shopee/SPX data or APIs","Real buyer messaging","Courier dispatch, exact slots","Address or COD changes","Returns and refunds"],16)

# 6 Solution flow diagram
s=slide("Solution: the two-assessment flow","[1:05-1:45] Walk the diagram. Raw data goes through a pre-check; malformed or closed cases never reach the AI. Agent assessment 1 produces evidence and a hypothesis. If information is missing, the backend contact gate allows exactly one buyer question. A reply triggers assessment 2; a manual no-reply keeps assessment 1. Then the policy engine decides what is permitted, and Ops receives the recommendation. Say plainly: the deterministic assessor plays the agent role today; the LLM agent is next. The novelty is the bounded design: one buyer question, fixed vocabularies, policy decides.",tag="4  Solution")
y=1.35; bw=1.5; bh=0.8; RH=1.2
xs=[0.3,2.05,3.8,5.55,7.3]
labels=[["Raw data","status, notes, lifecycle"],["Pre-check","exclude invalid cases"],["Agent assessment 1","6-field output"],["Contact gate","backend allows 1 question"],["One buyer question","from missing_info"]]
cols=[PANEL,PANEL,CYAN,PANEL,PANEL]
for i,(x,l) in enumerate(zip(xs,labels)):
    box(s,x,y,bw,RH,l,cols[i] if cols[i]!=CYAN else RGBColor(0x07,0x4A,0x58),CYAN,14,WHITE,True)
    if i<4: arrow(s,x+bw,y+RH/2,xs[i+1],y+RH/2)
R2=3.0; R2H=1.05
box(s,7.3,R2,1.5,R2H,["Reply","Agent assessment 2"],RGBColor(0x07,0x4A,0x58),GREEN,14,WHITE,True)
box(s,5.3,R2,1.7,R2H,["No reply (manual)","keep assessment 1"],PANEL,ORANGE,14,WHITE,True)
arrow(s,8.05,y+RH,8.05,R2); arrow(s,7.6,y+RH,6.4,R2,ORANGE)
box(s,2.2,R2,2.6,R2H,["Policy engine","deterministic gate"],PANEL,GREEN,16,WHITE,True)
# Reply routes below the No-reply box, then up into the Policy engine; No reply goes straight in
RY=R2+R2H+0.12
arrow(s,8.05,R2+R2H,8.05,RY,GREEN,head=False); arrow(s,8.05,RY,3.5,RY,GREEN,head=False); arrow(s,3.5,RY,3.5,R2+R2H,GREEN)
arrow(s,5.3,R2+R2H/2,4.8,R2+R2H/2,ORANGE)
box(s,0.3,R2,1.6,R2H,["Ops","recommendation"],GREEN,None,16,NAVY,True)
arrow(s,2.2,R2+R2H/2,1.9,R2+R2H/2,GREEN)
tb(s,0.3,4.3,9.3,0.75,["Novelty: one bounded buyer question + fixed vocabularies. LLM proposes; policy decides; Ops executes.","Today a deterministic assessor stands in for the LLM agent (next step). The agent never acts."],14,CYAN,True)

# 7 Six fields
s=slide("The agent's output: six fields, fixed vocabularies","[1:45-1:55] The agent (today the deterministic assessor) returns exactly six fields, and values must come from approved lists: 7 hypotheses, 8 missing-info codes, 5 candidate actions. Confidence measures support for the hypothesis, not delivery success.",tag="4  Solution")
f=["evidence","hypothesis","confidence","missing_info","question_key","candidate_action"]
for i,n in enumerate(f):
    box(s,0.4+(i%3)*3.1,1.3+(i//3)*0.8,2.9,0.65,n,PANEL,CYAN,16,WHITE,True)
box(s,0.4,3.0,2.9,1.5,["7 hypotheses","availability, address, contact, buyer intent, payment, logistics, unknown"],PANEL,GREEN,14,WHITE,True)
box(s,3.5,3.0,2.9,1.5,["8 missing_info","intent, availability, address, contact, COD, access, logistics, cause"],PANEL,GREEN,14,WHITE,True)
box(s,6.6,3.0,3.0,1.5,["5 candidate actions","clarify, standard re-attempt, hold, escalate review, no action"],PANEL,GREEN,14,WHITE,True)

# 8 Policy separation
s=slide("Policy gate: the LLM never grants itself permission","[1:55-2:15] This is the trust story. High confidence does not override policy. Retry needs direct buyer intent, availability and sufficient delivery info. Anything outside the MVP, such as changing an address, is blocked and escalated. These checks are plain deterministic code that we test.",tag="4  Solution")
box(s,0.4,1.4,4.3,0.5,"Agent proposes",CYAN,None,18,NAVY,True)
tb(s,0.4,2.0,4.3,2.3,["Evidence and hypothesis","Missing information","One question","Candidate action","Today: rule-based; LLM is next"],16)
box(s,5.1,1.4,4.5,0.5,"Policy engine decides",GREEN,None,18,NAVY,True)
tb(s,5.1,2.0,4.5,2.3,["Eligibility and attempts left","Silence is not refusal","Courier note is unverified","Blocks address change, dispatch, refund"],16)
tb(s,0.4,4.4,9.2,0.6,"High confidence never overrides policy.",18,ORANGE,True)

# 9 Architecture diagram
s=slide("MVP architecture","[2:15-2:30] Today it is a local Vite, React and TypeScript app. Fixtures stand in for the data stores; a deterministic assessor stands in for the LLM agent; the policy gate and audit trail are real local code. The target design has the same three layers, backed by the 9-table data model.",tag="5  MVP architecture")
box(s,0.3,1.3,2.6,1.2,["Data layer","9-table model: buyers, orders, delivery events, rescue cases, interactions"],PANEL,CYAN,13,WHITE,True)
box(s,3.3,1.3,2.6,1.2,["Backend","state, contact gate, question budget, writes"],PANEL,CYAN,14,WHITE,True)
box(s,6.3,1.3,3.3,1.2,["Agent (LLM: next step)","reads allowed sources; outputs 6 fields"],RGBColor(0x07,0x4A,0x58),CYAN,14,WHITE,True)
arrow(s,2.9,1.9,3.3,1.9); arrow(s,5.9,1.9,6.3,1.9)
box(s,3.3,3.0,2.6,1.0,["Policy engine","versioned, deterministic"],PANEL,GREEN,14,WHITE,True)
box(s,6.3,3.0,3.3,1.0,["Ops console","recommendation, evidence, audit"],GREEN,None,14,NAVY,True)
arrow(s,4.6,2.5,4.6,3.0,GREEN); arrow(s,5.9,3.5,6.3,3.5,GREEN)
box(s,0.3,3.0,2.6,1.0,["Today: local React app","fixtures, rule-based assessor"],PANEL,ORANGE,13,WHITE,True)
tb(s,0.3,4.3,9.3,0.6,"Golden test cases are kept out of the assessor's input.",16,GREY)

# 10 Scale
s=slide("How it scales","[BACKUP, not in the timed pitch] Scaling is a path, not a claim. The evaluation harness does not exist yet; only the 30 cases and unit tests do. Real carrier data replaces fixtures, a queue handles volume, each policy version gets its own profile, and an evaluation harness reuses our 30 synthetic cases as a regression suite.",tag="Backup | Scale")
steps=[("Now","Local MVP, fixtures"),("Next","Real carrier data feeds"),("Then","Case queue, async agent runs"),("Then","Policy profile per version"),("Then","Evaluation harness, 30 cases (not built yet)")]
for i,(a,b) in enumerate(steps):
    box(s,0.3+i*1.85,1.8,1.65,1.6,[a,b],PANEL,[ORANGE,CYAN,CYAN,CYAN,GREEN][i],14,WHITE,True)
    if i<4: arrow(s,1.95+i*1.85,2.6,2.15+i*1.85,2.6)
tb(s,0.4,3.8,9.2,1.0,"The 30 synthetic cases cover 24 with a buyer reply and 6 manual no-reply paths.",16,INK)

# 11 Integration
s=slide("Integration: how it would plug into Ops","[BACKUP, not in the timed pitch] Integration is designed, not built. The agent would read delivery-event and order stores, ask the buyer through a backend-controlled channel, and show recommendations in an Ops console with a human decision. State clearly: the MVP integrates with nothing live.",tag="Backup | Integration")
box(s,0.3,1.4,2.5,1.0,["Order and delivery-event stores","read only"],PANEL,CYAN,14,WHITE,True)
box(s,3.5,1.4,2.5,1.0,["Order Rescue service","agent + policy engine"],RGBColor(0x07,0x4A,0x58),CYAN,14,WHITE,True)
box(s,6.7,1.4,2.9,1.0,["Ops console","human approves or rejects"],GREEN,None,14,NAVY,True)
arrow(s,2.8,1.9,3.5,1.9); arrow(s,6.0,1.9,6.7,1.9,GREEN)
box(s,3.5,3.0,2.5,0.9,["Buyer messaging channel","via backend contact gate"],PANEL,ORANGE,14,WHITE,True)
arrow(s,4.75,2.4,4.75,3.0,ORANGE)
tb(s,0.3,4.2,9.3,0.8,"Today: no Shopee/SPX data, API, messaging or dispatch. All of the above is FUTURE / UNVERIFIED.",16,ORANGE,True)

# 12 Impact
s=slide("Where AI could create value in operations","[5:45-6:00] (15 seconds) These are hypotheses to validate with real data, not results. We deliberately show no savings or accuracy numbers because we have none. What we can show is the mechanism: evidence-backed, explainable decisions.",tag="7  Impact (hypotheses to validate)")
for i,(t,d) in enumerate([("Fewer wasted re-attempts","9 of 30 test cases change hypothesis after the reply, e.g. DEMO-002"),("Faster Ops triage","Evidence pre-assembled for all 30 cases"),("Explainable decisions","Six traceable fields per case"),("Better buyer experience","One question; 6 no-reply paths handled")]):
    box(s,0.4+(i%2)*4.7,1.4+(i//2)*1.45,4.5,1.25,[t,d],PANEL,[CYAN,GREEN,ORANGE,CYAN][i],16,WHITE,True)
tb(s,0.4,4.4,9.2,0.7,"Case counts come from the 30 synthetic test cases. No impact numbers claimed; all four are hypotheses.",16,GREY)

# 13 Codex
s=slide("How we used Codex","[2:30-3:15] (45 seconds) TEAM MUST CONFIRM before presenting which files Codex generated versus Claude Code; the repo also contains .claude/ and CLAUDE.md, so do not imply Codex did everything. Verifiable facts: 15 Codex agent configs in .codex/agents, 34 skills in .agents/skills, a Vitest suite (23 tests in 6 files passed on 29 Oct; re-run npm run test:unit immediately before presenting and quote the fresh number) and a Playwright spec in e2e/. Show the repo view on screen. Do not state accuracy or correctness.",tag="8  Use of Codex")
bullets(s,["Codex harness in the repo: 15 agent configs (.codex/agents), 34 skills (.agents/skills).","Spec-driven loop encoded there: research, plan, validate, execute.","Vitest: 23 tests in 6 files pass (npm run test:unit, run 29 Oct).","Playwright spec for the demo flow in e2e/.","Claude Code was also used here (.claude/ in repo): we show the repo, not sole authorship."],size=16,y=1.4)

# 14 Demo flow
s=slide("Demo flow: verified vs simulated","[3:15-5:45] (2.5 minutes, live) Show one case end to end: evidence, assessment, policy result, audit. Then the blocked request. Use the truth legend: real local code versus simulated data versus future.",tag="9  Demo")
for i,(t,d,c) in enumerate([("REAL - LOCAL","UI, assessor, policy gate, audit, tests",GREEN),("SIMULATED","Orders, events, notes, buyer replies",ORANGE),("FUTURE / UNVERIFIED","Shopee/SPX data, messaging, dispatch",CYAN)]):
    box(s,0.4+i*3.1,1.4,2.9,1.5,[t,d],PANEL,c,16,WHITE,True)
bullets(s,["Pick a case: raw status plus courier note.","See evidence, hypothesis, missing info.","Apply buyer reply; watch reassessment.","Try a blocked request: policy refuses."],y=3.1,size=16,h=2)

# 15 Roadmap
s=slide("Roadmap and Q&A backup","[BACKUP, after the end; Q&A] Likely questions: How is the LLM kept honest? Policy gate and fixed vocabularies. What about real data? Not accessed; next step needs permission. Where is the AI? The v2.2 contract, six fixed-vocabulary fields and the recommendation prompt branch define the LLM part; a deterministic assessor stands in today. Where do numbers come from? We claim none.",tag="Backup | Roadmap")
for i,(a,b) in enumerate([("Next","Connect the LLM agent to the v2.2 contract"),("Then","Run all 30 cases through an evaluator"),("Later","Pilot on real data with permission")]):
    box(s,0.4+i*3.1,1.4,2.9,1.4,[a,b],PANEL,[CYAN,GREEN,ORANGE][i],16,WHITE,True)
tb(s,0.4,3.1,9.2,1.9,["Q&A backup:","How do you prevent hallucinated actions? Fixed vocabularies and a deterministic gate.","Why one question only? Policy profile caps buyer questions at 1.","What is real today? Local app, policy gate and tests."],16)

# reorder: timed pitch first, backup slides after the end
lst=prs.slides._sldIdLst; ids=list(lst)
order=[0,1,2,4,5,6,7,8,12,13,11,3,9,10,14]
for e in ids: lst.remove(e)
for i in order: lst.append(ids[i])
for n,i in enumerate(order,1):
    PAGENUMS[i].text_frame.paragraphs[0].runs[0].text=str(n)
os.makedirs('/home/team3/lucas/sea-hackathon/docs/slides',exist_ok=True)
prs.save('/home/team3/lucas/sea-hackathon/docs/slides/Order_Rescue_Pitch_Deck.pptx')
