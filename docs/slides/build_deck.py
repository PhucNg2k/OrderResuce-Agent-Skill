# Order Rescue pitch deck generator ("parcel / tracking" editorial look, light theme).
# Run: python build_deck.py   -> docs/slides/Order_Rescue_Pitch_Deck.pptx
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.dml import MSO_LINE
from pptx.oxml.ns import qn
from lxml import etree
import os, shutil

def rgb(h): return RGBColor.from_string(h)
PAPER=rgb('FAF6EF'); INK=rgb('1F2A37'); KRAFT=rgb('C58B4B'); SAND=rgb('E9DFCF')
TEAL=rgb('0E5E6F'); RED=rgb('D64933'); REDT=rgb('B83A26'); GREY=rgb('5B6270')
BAND=rgb('F1E9DA'); WHITE=rgb('FFFDF8'); KRAFT_L=rgb('D9AA6E'); KRAFT_D=rgb('A9733A'); TAPE=rgb('EBDDB8')
GEO='Georgia'; CAL='Calibri'
IN=914400; CX=1.5; CR=9.4; TOTAL=15

def E(v): return Emu(int(round(v*IN)))

prs=Presentation(); prs.slide_width=Emu(9144000); prs.slide_height=Emu(5143500)
BLANK=prs.slide_layouts[6]

FW={GEO:(0.55,0.60),CAL:(0.50,0.52)}
def est_lines(text,width_pt,size,font,bold):
    f=FW[font][1 if bold else 0]*size*(1.15 if text.isupper() else 1.0)
    cur=0; lines=1
    for w in text.split(' '):
        wl=len(w)*f
        if cur==0: cur=wl
        elif cur+f+wl<=width_pt: cur+=f+wl
        else: lines+=1; cur=wl
        if wl>width_pt: lines+=int(wl//width_pt)
    return lines

def P(t,size=14,color=INK,bold=False,font=CAL,italic=False,align=PP_ALIGN.LEFT,after=0,ls=None):
    return dict(t=t,size=size,color=color,bold=bold,font=font,italic=italic,align=align,after=after,ls=ls)

def settext(shp,paras,anchor=MSO_ANCHOR.TOP,ml=0.05,mt=0.03):
    tf=shp.text_frame; tf.word_wrap=True; tf.vertical_anchor=anchor; tf.auto_size=MSO_AUTO_SIZE.NONE
    tf.margin_left=tf.margin_right=E(ml); tf.margin_top=tf.margin_bottom=E(mt)
    for i,p in enumerate(paras):
        para=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        para.alignment=p['align']; para.space_after=Pt(p['after']); para.space_before=Pt(0)
        if p['ls']: para.line_spacing=p['ls']
        r=para.add_run(); r.text=p['t']; f=r.font
        f.size=Pt(p['size']); f.bold=p['bold']; f.italic=p['italic']; f.name=p['font']; f.color.rgb=p['color']

def T(s,x,y,w,h,paras,anchor=MSO_ANCHOR.TOP,ml=0.05,mt=0.03):
    t=s.shapes.add_textbox(E(x),E(y),E(w),E(h)); settext(t,paras,anchor,ml,mt); return t

def R(s,x,y,w,h,fill=None,line=None,lw=1.0,shape=MSO_SHAPE.RECTANGLE,dash=None,paras=None,anchor=MSO_ANCHOR.MIDDLE,ml=0.06,mt=0.03,adj=None):
    b=s.shapes.add_shape(shape,E(x),E(y),E(w),E(h))
    if adj is not None: b.adjustments[0]=adj
    if fill is None: b.fill.background()
    else: b.fill.solid(); b.fill.fore_color.rgb=fill
    if line is None: b.line.fill.background()
    else:
        b.line.color.rgb=line; b.line.width=Pt(lw)
        if dash: b.line.dash_style=dash
    b.shadow.inherit=False
    if paras: settext(b,paras,anchor,ml,mt)
    return b

def poly(s,pts,fill,line=None):
    fb=s.shapes.build_freeform(E(pts[0][0]),E(pts[0][1]),scale=1.0)
    fb.add_line_segments([(E(x),E(y)) for x,y in pts[1:]],close=True)
    b=fb.convert_to_shape()
    b.fill.solid(); b.fill.fore_color.rgb=fill
    if line is None: b.line.fill.background()
    else: b.line.color.rgb=line; b.line.width=Pt(0.75)
    b.shadow.inherit=False
    return b

def ln(s,x1,y1,x2,y2,color=INK,w=1.75,head=False,dash=None,a=None,ai=None,b=None,bi=None):
    c=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,E(x1),E(y1),E(x2),E(y2))
    c.line.color.rgb=color; c.line.width=Pt(w)
    if dash: c.line.dash_style=dash
    if a is not None: c.begin_connect(a,ai)
    if b is not None: c.end_connect(b,bi)
    if head:
        l=c.line._get_or_add_ln(); t=etree.SubElement(l,qn('a:tailEnd'))
        t.set('type','triangle'); t.set('w','med'); t.set('len','med')
    return c

def node(s,x,y,w,h,title,sub=None,fill=WHITE,line=INK,tc=INK,lw=1.0,size=14,sc=None,align=PP_ALIGN.CENTER,dash=None):
    paras=[P(title,size,tc,True,CAL,align=align)]
    if sub:
        for t in (sub if isinstance(sub,list) else [sub]): paras.append(P(t,size,sc or tc,False,CAL,align=align))
    return R(s,x,y,w,h,fill,line,lw,paras=paras,ml=0.04,dash=dash)

def hr(s,x1,x2,y,color=KRAFT,w=0.75): return ln(s,x1,y,x2,y,color,w)

def title(s,text,x=CX,y=0.55,w=7.9,size=28,color=INK):
    n=est_lines(text,(w-0.1)*72,size,GEO,True)
    h=n*size*1.2*0.95/72+0.1
    T(s,x,y,w,h,[P(text,size,color,True,GEO,ls=0.95)])
    return y+h

def new(n,notes,numeral=None,label=None,panel=False):
    s=prs.slides.add_slide(BLANK)
    f=s.background.fill; f.solid(); f.fore_color.rgb=PAPER
    s.notes_slide.notes_text_frame.text=notes
    if numeral is not None:
        if not panel:
            T(s,0.56,0.28,0.8,0.8,[P(numeral,44,TEAL,True,GEO)])
            ln(s,0.68,1.15,0.68,4.8,KRAFT,1.0)
            T(s,CX,0.3,7.9,0.24,[P(label.upper(),11,TEAL,True)])
        # footer + tracking route
        T(s,0.6,5.27,6,0.24,[P("Order Rescue | synthetic data only | local MVP",11,GREY)])
        T(s,8.4,5.27,1.0,0.24,[P(f"{n} / {TOTAL}",11,GREY,align=PP_ALIGN.RIGHT)])
        ln(s,0.6,5.08,9.4,5.08,KRAFT,1.0)
        for i in range(TOTAL):
            cx=0.6+i*8.8/(TOTAL-1); cur=(i+1==n); d=0.2 if cur else 0.11
            col=TEAL if i<11 else KRAFT
            R(s,cx-d/2,5.08-d/2,d,d,fill=TEAL if cur else PAPER,line=col,lw=1.25,shape=MSO_SHAPE.OVAL)
    return s
NOTES = {'Order Rescue': '[0:00-0:15] Good afternoon. We are Lucas, Phuc, Hai and Kha. Order Rescue is a policy-gated decision layer for failed last-mile deliveries, designed to host an LLM agent. It recommends to Ops; it never acts on its own. Everything runs on synthetic data and is labelled as such. Be upfront: today a deterministic assessor stands in for the LLM agent.', 'Why this fits the build directions': '[0:15-0:25] (10 seconds) We align with Autonomous and Adaptive AI: an agent that reasons, asks, then reassesses within limits. It also reflects Deep Domain AI: the rules come from how delivery Ops actually reasons, such as silence is not refusal.', 'Problem: a failed attempt is a status, not a cause': '[0:25-0:50] When a first delivery attempt fails, Ops sees a code like recipient unavailable or refused. Public Shopee guidance itself says delivery status can be incorrect or incomplete. Re-attempting blindly wastes a courier trip; closing too early loses a sale. Four parties feel it: buyers, couriers, Ops, sellers (detail on backup slide).', 'Why rescue is hard, and who is hurt': '[BACKUP, not in the timed pitch] Four parties feel this. Buyers wait for parcels; couriers burn attempts; Ops triage case by case without evidence; sellers risk returns. The hard part is that one status maps to many causes, and the buyer is the only person who can resolve some of them.', 'Priorities: what we built, what we left out': '[0:50-1:05] We prioritised a trustworthy decision, not a flashy integration. In scope: evidence-based assessment, one buyer question, a deterministic policy gate and an audit trail. Out of scope: anything that touches the real world.', 'Solution: the two-assessment flow': '[1:05-1:45] Walk the diagram. Raw data goes through a pre-check; malformed or closed cases never reach the AI. Agent assessment 1 produces evidence and a hypothesis. If information is missing, the backend contact gate allows exactly one buyer question. A reply triggers assessment 2; a manual no-reply keeps assessment 1. Then the policy engine decides what is permitted, and Ops receives the recommendation. Say plainly: the deterministic assessor plays the agent role today; the LLM agent is next. The novelty is the bounded design: one buyer question, fixed vocabularies, policy decides.', "The agent's output: six fields, fixed vocabularies": '[1:45-1:55] The agent (today the deterministic assessor) returns exactly six fields, and values must come from approved lists: 7 hypotheses, 8 missing-info codes, 5 candidate actions. Confidence measures support for the hypothesis, not delivery success.', 'Policy gate: the LLM never grants itself permission': '[1:55-2:15] This is the trust story. High confidence does not override policy. Retry needs direct buyer intent, availability and sufficient delivery info. Anything outside the MVP, such as changing an address, is blocked and escalated. These checks are plain deterministic code that we test.', 'MVP architecture': '[2:15-2:30] Today it is a local Vite, React and TypeScript app. Fixtures stand in for the data stores; a deterministic assessor stands in for the LLM agent; the policy gate and audit trail are real local code. The target design has the same three layers, backed by the 9-table data model.', 'How it scales': '[BACKUP, not in the timed pitch] Scaling is a path, not a claim. The evaluation harness does not exist yet; only the 30 cases and unit tests do. Real carrier data replaces fixtures, a queue handles volume, each policy version gets its own profile, and an evaluation harness reuses our 30 synthetic cases as a regression suite.', 'Integration: how it would plug into Ops': '[BACKUP, not in the timed pitch] Integration is designed, not built. The agent would read delivery-event and order stores, ask the buyer through a backend-controlled channel, and show recommendations in an Ops console with a human decision. State clearly: the MVP integrates with nothing live.', 'Where AI could create value in operations': '[5:45-6:00] (15 seconds) These are hypotheses to validate with real data, not results. We deliberately show no savings or accuracy numbers because we have none. What we can show is the mechanism: evidence-backed, explainable decisions.', 'How we used Codex': '[2:30-3:15] (45 seconds) Say only what the team has confirmed: we used Codex for the demo app, its tests (Vitest and Playwright), and the data model, business rules and 30 test cases. Do not extend the claim beyond those three areas. Re-run npm run test:unit immediately before presenting and quote the fresh number. Show the repo view on screen. Do not state accuracy or correctness.', 'Demo flow: verified vs simulated': '[3:15-5:45] (2.5 minutes, live) Show one case end to end: evidence, assessment, policy result, audit. Then the blocked request. Use the truth legend: real local code versus simulated data versus future.', 'Roadmap and Q&A backup': '[BACKUP, after the end; Q&A] Likely questions: How is the LLM kept honest? Policy gate and fixed vocabularies. What about real data? Not accessed; next step needs permission. Where is the AI? The v2.2 contract, six fixed-vocabulary fields and the recommendation prompt branch define the LLM part; a deterministic assessor stands in today. Where do numbers come from? We claim none.'}
C=PP_ALIGN.CENTER; RT=PP_ALIGN.RIGHT
MID=MSO_ANCHOR.MIDDLE; TOP=MSO_ANCHOR.TOP; BOT=MSO_ANCHOR.BOTTOM

# ---------------------------------------------------------------- 1 Cover
s=prs.slides.add_slide(BLANK); f=s.background.fill; f.solid(); f.fore_color.rgb=PAPER
s.notes_slide.notes_text_frame.text=NOTES["Order Rescue"]
R(s,6.5,0,3.5,5.625,fill=SAND)
fx,fy,fw,fh,dx,dy=6.85,2.65,2.1,1.55,0.45,0.4
R(s,fx-0.1,fy+fh-0.12,fw+dx+0.2,0.26,fill=rgb('D6C6A8'),shape=MSO_SHAPE.OVAL)
R(s,fx,fy,fw,fh,fill=KRAFT)
poly(s,[(fx+fw,fy),(fx+fw+dx,fy-dy),(fx+fw+dx,fy+fh-dy),(fx+fw,fy+fh)],KRAFT_D)
poly(s,[(fx,fy),(fx+fw,fy),(fx+fw+dx,fy-dy),(fx+dx,fy-dy)],KRAFT_L)
tx=fx+fw/2-0.17; tw=0.34
R(s,tx,fy,tw,fh,fill=TAPE)
poly(s,[(tx,fy),(tx+tw,fy),(tx+tw+dx,fy-dy),(tx+dx,fy-dy)],TAPE)
# shipping label (barcode + address lines) right of the tape
lx,ly=fx+1.3,fy+0.8
R(s,lx,ly,0.65,0.58,fill=PAPER,line=INK,lw=0.75)
for k in range(9):
    R(s,lx+0.07+k*0.062,ly+0.07,0.03 if k%2 else 0.045,0.24,fill=INK)
R(s,lx+0.07,ly+0.38,0.5,0.03,fill=GREY); R(s,lx+0.07,ly+0.46,0.34,0.03,fill=GREY)
R(s,fx+0.15,fy+0.15,0.5,0.5,fill=None,line=REDT,lw=1.5,shape=MSO_SHAPE.OVAL)  # rescue stamp ring
R(s,fx+0.3,fy+0.3,0.2,0.2,fill=RED,shape=MSO_SHAPE.OVAL)
# route dots on the panel
for i,(px,py) in enumerate([(7.0,0.7),(7.0,1.15),(7.0,1.6)]): R(s,px-0.04,py-0.04,0.08,0.08,fill=KRAFT,shape=MSO_SHAPE.OVAL)
ln(s,7.0,0.7,7.0,1.6,KRAFT,1.0,dash=MSO_LINE.DASH)

T(s,0.6,0.45,5.6,0.25,[P("SEA X OPENAI CODEX HACKATHON | 31 OCT 2026",11,TEAL,True)])
T(s,0.6,0.75,5.6,0.9,[P("Order Rescue",46,INK,True,GEO,ls=0.95)])
R(s,0.65,1.68,0.7,0.06,fill=RED)
T(s,0.6,1.82,5.6,0.45,[P("Adaptive Delivery Recovery Agent",20,TEAL,False,GEO,italic=True)])
T(s,0.6,2.4,5.6,0.85,[P("Works out why a delivery failed, asks the buyer one good question, and hands Ops an explainable, policy-checked recommendation.",16,INK)])
T(s,0.6,3.35,5.6,0.55,[P("Honest status: today a deterministic assessor stands in for the LLM agent; the LLM agent is the next step.",14,REDT,True)])
for i,nm in enumerate(["Lucas","Phuc","Hai","Kha"]):
    R(s,0.65+i*1.3,4.1,1.2,0.38,fill=SAND,shape=MSO_SHAPE.ROUNDED_RECTANGLE,adj=0.3,paras=[P(nm,14,INK,True,align=C)])
T(s,0.6,4.6,5.6,0.55,[P("Concept owner: Kha. Lucas: scope and demo flow. Phuc: AI feasibility. Hai: business rules and test cases.",14,GREY)])

# ---------------------------------------------------------------- 2 Build directions (split screen)
s=new(2,NOTES["Why this fits the build directions"],"1","Intro",panel=True)
R(s,0,0,3.7,4.85,fill=TEAL)
T(s,0.6,0.28,0.8,0.8,[P("1",44,PAPER,True,GEO)])
T(s,0.6,1.1,2.8,0.24,[P("INTRO",11,SAND,True)])
title(s,"Why this fits the build directions",x=0.6,y=1.35,w=2.9,color=PAPER)
T(s,0.6,3.55,2.9,1.05,[P("Primary: Autonomous & Adaptive AI. Secondary: Deep Domain AI.",16,SAND)])
rows=[("Autonomous & Adaptive AI","Reassesses after one buyer reply; stays inside hard limits",TEAL),
      ("Deep Domain AI","Ops logic encoded: courier notes are unverified, silence is not refusal",KRAFT),
      ("AI-Native Operations","Recommendation with evidence, not a bare status code",GREY)]
for i,(a,b,c) in enumerate(rows):
    y=0.55+i*1.4
    R(s,4.1,y,5.3,1.15,fill=SAND,paras=[P(a,18,INK,True,GEO,after=3),P(b,14,INK)],ml=0.3,anchor=MID)
    R(s,4.1,y,0.1,1.15,fill=c)

# ---------------------------------------------------------------- 3 Problem
s=new(3,NOTES["Problem: a failed attempt is a status, not a cause"],"2","Problem statement")
title(s,"Problem: a failed attempt is a status, not a cause")
items=["First attempts fail; the raw code is all Ops sees.","Courier notes are unverified and often vague.","Wrong guess: a wasted re-attempt, or a lost order.","No structured record of why a decision was made."]
for i,t in enumerate(items):
    y=1.7+i*0.78
    hr(s,CX,5.6,y,KRAFT,0.75)
    T(s,CX,y+0.06,4.1,0.66,[P(t,16,INK)],anchor=MID)
R(s,6.1,1.75,3.3,1.05,fill=None,line=REDT,lw=2.25,paras=[P("recipient unavailable",22,REDT,False,GEO,italic=True,align=C)])
T(s,6.1,2.95,3.3,0.95,[P("Could mean: at work, wrong landmark, unreachable phone, or a disrupted route.",16,INK)])
for k in range(22):
    R(s,6.15+k*0.14,4.2,0.045 if k%3 else 0.08,0.5,fill=INK)

# ---------------------------------------------------------------- 4 Priorities (compare)
s=new(4,NOTES["Priorities: what we built, what we left out"],"3","Priorities")
title(s,"Priorities: what we built, what we left out")
ln(s,5.45,1.65,5.45,4.8,KRAFT,0.75,dash=MSO_LINE.DASH)
for (x,head,hc,items,mark) in [(CX,"IN the MVP",TEAL,["Evidence-backed assessment","One buyer question, max","Deterministic policy gate","Recommendation to Ops only","Audit trail per decision"],'in'),
                              (5.75,"Deliberately OUT",REDT,["Live Shopee/SPX data or APIs","Real buyer messaging","Courier dispatch, exact slots","Address or COD changes","Returns and refunds"],'out')]:
    T(s,x,1.6,3.65,0.45,[P(head,20,hc,True,GEO)])
    ln(s,x,2.1,x+3.65,2.1,hc,2.25)
    for j,t in enumerate(items):
        y=2.25+j*0.5
        if mark=='in': R(s,x+0.05,y+0.13,0.18,0.18,fill=TEAL,shape=MSO_SHAPE.OVAL)
        else:
            R(s,x+0.05,y+0.13,0.18,0.18,fill=None,line=REDT,lw=1.5,shape=MSO_SHAPE.OVAL)
            ln(s,x+0.09,y+0.22,x+0.19,y+0.22,REDT,1.5)
        T(s,x+0.32,y,3.33,0.44,[P(t,15,INK)],anchor=MID)

# ---------------------------------------------------------------- 5 Flow (swimlane)
s=new(5,NOTES["Solution: the two-assessment flow"],"4","Solution")
title(s,"Solution: the two-assessment flow")
X0=1.8; PITCH=1.56; NW=1.32; NH=1.04
def cx_(i): return X0+PITCH*i
R(s,1.4,1.1,8.0,1.12,fill=BAND); R(s,1.4,1.1,0.28,1.12,fill=TEAL,paras=[P("ASSESS",11,PAPER,True,align=C)],ml=0,mt=0)
R(s,1.4,2.45,8.0,1.37,fill=BAND); R(s,1.4,2.45,0.28,1.37,fill=TEAL,paras=[P("DECIDE",11,PAPER,True,align=C)],ml=0,mt=0)
for sh in s.shapes:
    if sh.has_text_frame and sh.text_frame.text in ("ASSESS","DECIDE"):
        sh.text_frame._txBody.find(qn('a:bodyPr')).set('vert','vert270')
L1=[("Raw data","status, notes, lifecycle",WHITE,INK,KRAFT),("Pre-check","exclude invalid cases",WHITE,INK,KRAFT),
    ("Agent assessment 1","6-field output",TEAL,PAPER,TEAL),("Contact gate","backend allows 1 question",WHITE,INK,KRAFT),
    ("One buyer question","from missing_info",WHITE,INK,KRAFT)]
n1=[]
for i,(a,b,f_,tc,lc) in enumerate(L1):
    n1.append(node(s,cx_(i),1.14,NW,NH,a,b,fill=f_,line=lc,tc=tc))
for i in range(4): ln(s,0,0,1,1,INK,1.75,True,a=n1[i],ai=3,b=n1[i+1],bi=1)
LY=2.5; LH=1.04
ops=node(s,X0,LY,1.62,LH,"Ops","recommendation",fill=INK,line=INK,tc=PAPER)
pol=node(s,3.7,LY,2.4,LH,"Policy engine","deterministic gate",fill=KRAFT,line=INK,tc=INK)
nor=node(s,cx_(3),LY,NW,LH,"No reply (manual)","keep assessment 1",fill=WHITE,line=KRAFT,tc=INK,lw=1.5)
rep=node(s,cx_(4),LY,NW,LH,"Reply","Agent assessment 2",fill=TEAL,line=TEAL,tc=PAPER)
ln(s,0,0,1,1,TEAL,1.75,True,a=n1[4],ai=2,b=rep,bi=0)                       # Q -> Reply
qx=cx_(4)+NW/2; nx=cx_(3)+NW/2; mid=(1.14+NH+LY)/2
ln(s,qx,mid,nx,mid,KRAFT_D,1.75)                                           # branch to No reply
ln(s,nx,mid,nx,LY,KRAFT_D,1.75,True)
ln(s,0,0,1,1,KRAFT_D,1.75,True,a=nor,ai=1,b=pol,bi=3)                      # No reply -> Policy
by=LY+LH+0.16; px_=3.7+2.4/2
ln(s,qx,LY+LH,qx,by,TEAL,1.75); ln(s,qx,by,px_,by,TEAL,1.75); ln(s,px_,by,px_,LY+LH,TEAL,1.75,True)  # Reply -> Policy (bypass)
ln(s,0,0,1,1,INK,1.75,True,a=pol,ai=1,b=ops,bi=3)                          # Policy -> Ops
T(s,CX,3.9,7.9,1.04,[P("Novelty: one bounded buyer question + fixed vocabularies. LLM proposes; policy decides; Ops executes.",14,TEAL,True,after=2),
                      P("Today a deterministic assessor stands in for the LLM agent (next step). The agent never acts.",14,REDT,True)])

# ---------------------------------------------------------------- 6 Six fields (big numbers)
s=new(6,NOTES["The agent's output: six fields, fixed vocabularies"],"4","Solution")
title(s,"The agent's output: six fields, fixed vocabularies")
fl=["evidence","hypothesis","confidence","missing_info","question_key","candidate_action"]
for i,nm in enumerate(fl):
    R(s,CX+(i%3)*2.7,1.6+(i//3)*0.52,2.5,0.42,fill=None,line=TEAL,lw=1.25,paras=[P(nm,15,TEAL,True,align=C)])
stats=[("7","hypotheses","availability, address, contact, buyer intent, payment, logistics, unknown"),
       ("8","missing_info","intent, availability, address, contact, COD, access, logistics, cause"),
       ("5","candidate actions","clarify, standard re-attempt, hold, escalate review, no action")]
for i,(n_,lab,lst) in enumerate(stats):
    x=CX+i*2.7
    ln(s,x,2.68,x+2.5,2.68,KRAFT,2.25)
    T(s,x,2.7,2.5,0.85,[P(n_,46,TEAL,True,GEO)],anchor=MID)
    T(s,x,3.55,2.5,0.34,[P(lab,16,INK,True,GEO)])
    T(s,x,3.9,2.5,1.02,[P(lst,14,INK)])

# ---------------------------------------------------------------- 7 Policy gate
s=new(7,NOTES["Policy gate: the LLM never grants itself permission"],"4","Solution")
title(s,"Policy gate: the LLM never grants itself permission")
lp=R(s,CX,1.7,3.0,2.35,fill=SAND,anchor=TOP,ml=0.2,mt=0.15,paras=[P("Agent proposes",18,TEAL,True,GEO,after=6)]+[P("•  "+t,14,INK,after=3) for t in ["Evidence and hypothesis","Missing information","One question","Candidate action","Today: rule-based; LLM is next"]])
gate=R(s,4.95,1.5,0.16,2.75,fill=RED)
rp=R(s,5.7,1.7,3.7,2.35,fill=TEAL,anchor=TOP,ml=0.2,mt=0.15,paras=[P("Policy engine decides",18,PAPER,True,GEO,after=6)]+[P("•  "+t,14,PAPER,after=3) for t in ["Eligibility and attempts left","Silence is not refusal","Courier note is unverified","Blocks address change, dispatch, refund"]])
gy=1.7+2.35/2
ln(s,4.5,gy,4.95,gy,INK,1.75,True,b=gate,bi=1)
ln(s,5.11,gy,5.7,gy,INK,1.75,True,b=rp,bi=1)
T(s,CX,4.28,7.9,0.55,[P("High confidence never overrides policy.",20,REDT,False,GEO,italic=True)])

# ---------------------------------------------------------------- 8 Architecture (layers)
s=new(8,NOTES["MVP architecture"],"5","MVP architecture")
title(s,"MVP architecture")
SX=CX; SWD=5.0; RH=0.76; GAP=0.22; y0=1.12
ys=[y0+i*(RH+GAP) for i in range(4)]
ops=node(s,SX,ys[0],SWD,RH,"Ops console","recommendation, evidence, audit",fill=INK,line=INK,tc=PAPER)
pol=node(s,SX,ys[1],2.4,RH,"Policy engine","versioned, deterministic",fill=KRAFT,line=INK,tc=INK)
agt=node(s,SX+2.6,ys[1],2.4,RH,"Agent (LLM: next step)","reads allowed sources; outputs 6 fields",fill=TEAL,line=TEAL,tc=PAPER)
bck=node(s,SX,ys[2],SWD,RH,"Backend","state, contact gate, question budget, writes",fill=WHITE,line=INK)
dat=node(s,SX,ys[3],SWD,RH,"Data layer","9-table model: buyers, orders, delivery events, rescue cases, interactions",fill=WHITE,line=INK)
ln(s,0,0,1,1,TEAL,1.75,True,a=dat,ai=0,b=bck,bi=2)
pcx=SX+1.2; acx=SX+2.6+1.2
ln(s,pcx,ys[2],pcx,ys[1]+RH,INK,1.75,True,b=pol,bi=2)
ln(s,acx,ys[2],acx,ys[1]+RH,INK,1.75,True,b=agt,bi=2)
ln(s,pcx,ys[1],pcx,ys[0]+RH,INK,1.75,True)
R(s,6.85,1.12,2.55,3.6,fill=SAND,anchor=TOP,ml=0.2,mt=0.2,paras=[P("Today: local React app",18,INK,True,GEO,after=4),P("fixtures, rule-based assessor",14,INK,after=14),P("Golden test cases are kept out of the assessor's input.",14,INK)])
R(s,6.85,1.12,2.55,0.08,fill=TEAL)

# ---------------------------------------------------------------- 9 Codex (ledger)
s=new(9,NOTES["How we used Codex"],"8","Use of Codex")
title(s,"How we used Codex")
rowsx=[("App","We used Codex to build the local demo app: React + Vite + TypeScript UI, assessor, policy gate and audit trail.",TEAL),
       ("23 tests","Vitest: 23 tests in 6 files pass (npm run test:unit, run 29 Oct).",TEAL),
       ("1 spec","Playwright spec for the demo flow in e2e/.",TEAL),
       ("30 cases","Data model v2.2, business rules and the 30 synthetic test cases were prepared with Codex.",TEAL),
       ("Next","The LLM agent is the next step; today a rule-based assessor stands in.",REDT)]
for i,(a,b,c) in enumerate(rowsx):
    y=1.2+i*0.72
    hr(s,CX,CR,y,KRAFT,0.75)
    T(s,CX,y+0.04,1.7,0.64,[P(a,20,c,True,GEO)],anchor=MID)
    T(s,3.3,y+0.04,6.1,0.64,[P(b,16,INK)],anchor=MID)

# ---------------------------------------------------------------- 10 Demo (legend + route)
s=new(10,NOTES["Demo flow: verified vs simulated"],"9","Demo")
title(s,"Demo flow: verified vs simulated")
leg=[("REAL - LOCAL","UI, assessor, policy gate, audit, tests",TEAL,None,PAPER,None),
     ("SIMULATED","Orders, events, notes, buyer replies",SAND,KRAFT_D,INK,MSO_LINE.DASH),
     ("FUTURE / UNVERIFIED","Shopee/SPX data, messaging, dispatch",None,GREY,INK,MSO_LINE.SQUARE_DOT)]
for i,(a,b,f_,l_,tc,d) in enumerate(leg):
    R(s,CX+i*2.7,1.25,2.5,1.5,fill=f_,line=l_,lw=2.0,dash=d,anchor=TOP,ml=0.18,mt=0.16,paras=[P(a,14,tc,True,after=6),P(b,16,tc)])
steps=["Pick a case: raw status plus courier note.","See evidence, hypothesis, missing info.","Apply buyer reply; watch reassessment.","Try a blocked request: policy refuses."]
sy=3.3; sc=[]
for i,t in enumerate(steps):
    cx=CX+0.2+i*2.0+0.0
    sc.append(R(s,cx,sy,0.4,0.4,fill=TEAL,shape=MSO_SHAPE.OVAL,paras=[P(str(i+1),14,PAPER,True,GEO,align=C)],ml=0,mt=0))
    T(s,cx-0.2,sy+0.5,1.8,1.0,[P(t,14,INK)])
for i in range(3):
    x1=CX+0.2+i*2.0+0.4; x2=CX+0.2+(i+1)*2.0
    ln(s,x1,sy+0.2,x2,sy+0.2,TEAL,1.75,True)

# ---------------------------------------------------------------- 11 Impact (big numbers)
s=new(11,NOTES["Where AI could create value in operations"],"7","Impact (hypotheses to validate)")
title(s,"Where AI could create value in operations")
imp=[("9/30","Fewer wasted re-attempts","9 of 30 test cases change hypothesis after the reply, e.g. DEMO-002"),
     ("30","Faster Ops triage","Evidence pre-assembled for all 30 cases"),
     ("6","Explainable decisions","Six traceable fields per case"),
     ("1","Better buyer experience","One question; 6 no-reply paths handled")]
y=1.58
for i,(n_,a,b) in enumerate(imp):
    rh=0.84 if i==0 else 0.64
    hr(s,CX,CR,y,KRAFT,0.75)
    T(s,CX,y+0.03,1.3,rh-0.06,[P(n_,28,TEAL,True,GEO)],anchor=MID)
    T(s,2.85,y+0.03,6.55,rh-0.06,[P(a,16,INK,True,GEO),P(b,14,INK)],anchor=MID)
    y+=rh
T(s,CX,4.42,7.9,0.52,[P("Case counts come from the 30 synthetic test cases. No impact numbers claimed; all four are hypotheses.",14,GREY)])

# ---------------------------------------------------------------- 12 Why hard (backup)
s=new(12,NOTES["Why rescue is hard, and who is hurt"],"B","Backup | Who is hurt")
title(s,"Why rescue is hard, and who is hurt")
for i,(a,b) in enumerate([("Buyers","Wait, get re-contacted blindly"),("Couriers","Spend limited attempts"),("Ops","Triage case by case"),("Sellers","Risk returns and lost sales")]):
    x=CX+i*2.02
    R(s,x+0.05,1.6,0.55,0.55,fill=[TEAL,REDT,INK,GREY][i],shape=MSO_SHAPE.OVAL,paras=[P(a[0],20,PAPER,True,GEO,align=C)],ml=0,mt=0)
    T(s,x,2.2,1.85,1.1,[P(a,16,INK,True,GEO,after=2),P(b,14,INK)])
for i,t in enumerate(["One status maps to many possible causes.","Only the buyer can resolve some unknowns.","Attempts are limited; silence must not be read as refusal."]):
    y=3.5+i*0.46
    hr(s,CX,CR,y,KRAFT,0.75)
    T(s,CX,y+0.04,7.9,0.38,[P(t,16,INK)],anchor=MID)

# ---------------------------------------------------------------- 13 Scale (route with stops)
s=new(13,NOTES["How it scales"],"B","Backup | Scale")
title(s,"How it scales")
stp=[("Now","Local MVP, fixtures"),("Next","Real carrier data feeds"),("Then","Case queue, async agent runs"),("Then","Policy profile per version"),("Then","Evaluation harness, 30 cases (not built yet)")]
cs=[]
for i,(a,b) in enumerate(stp):
    x=CX+i*1.6
    T(s,x,1.35,1.5,0.4,[P(a,20,REDT if i==0 else TEAL,True,GEO)])
    cs.append(R(s,x+0.05,1.9,0.34,0.34,fill=RED if i==0 else PAPER,line=RED if i==0 else TEAL,lw=2.0,shape=MSO_SHAPE.OVAL))
    T(s,x,2.4,1.5,1.3,[P(b,14,INK)])
for i in range(4): ln(s,CX+i*1.6+0.39,2.07,CX+(i+1)*1.6+0.05,2.07,TEAL,1.75,True)
for k in range(30):
    R(s,CX+k*0.2633,3.95,0.2,0.2,fill=TEAL if k<24 else None,line=TEAL if k<24 else KRAFT_D,lw=1.25)
T(s,CX,4.25,7.9,0.4,[P("The 30 synthetic cases cover 24 with a buyer reply and 6 manual no-reply paths.",14,INK)])

# ---------------------------------------------------------------- 14 Integration
s=new(14,NOTES["Integration: how it would plug into Ops"],"B","Backup | Integration")
title(s,"Integration: how it would plug into Ops")
R(s,CX-0.05,1.62,7.95,2.5,fill=None,line=GREY,lw=1.25,dash=MSO_LINE.DASH)
T(s,CX+0.1,1.66,3.0,0.24,[P("FUTURE / UNVERIFIED",11,GREY,True)])
st=node(s,1.7,2.0,2.2,1.0,"Order and delivery-event stores","read only",fill=WHITE,line=INK)
sv=node(s,4.2,2.0,2.4,1.0,"Order Rescue service","agent + policy engine",fill=TEAL,line=TEAL,tc=PAPER)
oc=node(s,6.9,2.0,2.3,1.0,"Ops console","human approves or rejects",fill=INK,line=INK,tc=PAPER)
by_=node(s,3.95,3.25,2.9,0.7,"Buyer messaging channel","via backend contact gate",fill=WHITE,line=KRAFT_D,lw=1.5)
ln(s,0,0,1,1,INK,1.75,True,a=st,ai=3,b=sv,bi=1)
ln(s,0,0,1,1,INK,1.75,True,a=sv,ai=3,b=oc,bi=1)
ln(s,0,0,1,1,KRAFT_D,1.75,True,a=sv,ai=2,b=by_,bi=0)
T(s,CX,4.25,7.9,0.6,[P("Today: no Shopee/SPX data, API, messaging or dispatch. All of the above is FUTURE / UNVERIFIED.",16,REDT,True)])

# ---------------------------------------------------------------- 15 Roadmap + Q&A
s=new(15,NOTES["Roadmap and Q&A backup"],"B","Backup | Roadmap")
title(s,"Roadmap and Q&A backup")
rm=[("Next","Connect the LLM agent to the v2.2 contract"),("Then","Run all 30 cases through an evaluator"),("Later","Pilot on real data with permission")]
rc=[]
for i,(a,b) in enumerate(rm):
    x=CX+i*2.7
    T(s,x,1.1,2.5,0.4,[P(a,20,[REDT,TEAL,TEAL][i],True,GEO)])
    rc.append(R(s,x+0.05,1.55,0.34,0.34,fill=RED if i==0 else PAPER,line=RED if i==0 else TEAL,lw=2.0,shape=MSO_SHAPE.OVAL))
    T(s,x,1.98,2.5,0.62,[P(b,14,INK)])
for i in range(2): ln(s,CX+i*2.7+0.39,1.72,CX+(i+1)*2.7+0.05,1.72,TEAL,1.75,True)
T(s,CX,2.65,7.9,0.34,[P("Q&A backup:",16,TEAL,True,GEO)])
qa=[("How do you prevent hallucinated actions?","Fixed vocabularies and a deterministic gate."),
    ("Why one question only?","Policy profile caps buyer questions at 1."),
    ("What is real today?","Local app, policy gate and tests.")]
for i,(q,a) in enumerate(qa):
    y=3.05+i*0.62
    hr(s,CX,CR,y,KRAFT,0.75)
    T(s,CX,y+0.03,4.3,0.56,[P(q,15,INK,False,GEO,italic=True)],anchor=MID)
    T(s,5.9,y+0.03,3.5,0.56,[P(a,14,INK)],anchor=MID)

# ---------------------------------------------------------------- save
OUT='/home/team3/lucas/sea-hackathon/docs/slides/Order_Rescue_Pitch_Deck.pptx'
os.makedirs(os.path.dirname(OUT),exist_ok=True)
prs.save(OUT)
print('saved',OUT,len(prs.slides._sldIdLst),'slides')
