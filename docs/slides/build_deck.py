# Order Rescue pitch deck generator ("parcel / tracking" editorial look, light theme).
# v3 (30 Oct): shortened per team meeting. Run: python build_deck.py   -> docs/slides/Order_Rescue_Pitch_Deck.pptx
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
IN=914400; CX=1.5; CR=9.4; TOTAL=12

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
            T(s,0.56,0.28,1.2,0.8,[P(numeral,44,TEAL,True,GEO)])
            ln(s,0.68,1.15,0.68,4.8,KRAFT,1.0)
            T(s,CX,0.3,7.9,0.24,[P(label.upper(),11,TEAL,True)])
        # footer + tracking route
        T(s,0.6,5.27,6,0.24,[P("Order Rescue | synthetic data only | local MVP",11,GREY)])
        T(s,8.4,5.27,1.0,0.24,[P(f"{n} / {TOTAL}",11,GREY,align=PP_ALIGN.RIGHT)])
        ln(s,0.6,5.08,9.4,5.08,KRAFT,1.0)
        for i in range(TOTAL):
            cx=0.6+i*8.8/(TOTAL-1); cur=(i+1==n); d=0.2 if cur else 0.11
            col=TEAL if i<9 else KRAFT
            R(s,cx-d/2,5.08-d/2,d,d,fill=TEAL if cur else PAPER,line=col,lw=1.25,shape=MSO_SHAPE.OVAL)
    return s
NOTES = {
'cover': '[0:00-0:15] Good afternoon. We are Lucas, Phuc, Hai and Kha. Order Rescue helps Ops understand why a delivery failed, and recommends what to do next. It recommends; it never acts on its own. Everything uses synthetic data. Be upfront: a rule-based assessor stands in for the LLM agent today.',
'numbers': '[0:15-0:55] Hai supplies these numbers (research due 9:00 on 30 Oct). Order: first Shopee operations numbers, then one outside case study where a similar problem was reduced, then say: that is why we built this. If numbers are not ready, delete this slide; do not invent any.',
'problem': '[0:55-1:25] When a delivery fails, Ops sees a code like recipient unavailable. It could mean the buyer was at work, the landmark was wrong, the phone was off, or the route was disrupted. Guessing wrong wastes a courier trip or loses the order, and nobody records why a decision was made.',
'solution': '[1:25-2:15] Four steps. One: read the case, meaning the status, the courier note and the order history. Two: if something is missing, ask the buyer one question, only one. Three: check the answer against the rules. Four: show Ops a recommendation with the evidence; Ops decides. Say plainly: today a rule-based assessor plays the AI role; the LLM agent is the next step.',
'policy': '[2:15-2:45] This is the trust story. The AI suggests, the rules decide. High confidence never overrides the rules. Silence is not a refusal. A courier note alone is not proof. The AI cannot change an address or refund anything; those are escalated to a person.',
'codex': '[2:45-3:25] Say only what the team confirmed: we used Codex for the demo app, its tests (Vitest and Playwright), and the data model, business rules and 30 test cases. Our process was rules and test cases first, then build, then test against them. Do not extend the claim beyond those areas. Do not state accuracy.',
'declare': '[3:25-3:45] Declaration, matching the 5 PM form. Before 31 Oct: data model, business rules, 30 synthetic cases and a first local prototype. On the day: fill in at 5 PM what was added. Judges may audit, so keep this exact.',
'demo': '[3:45-5:45] (2 minutes, live, real time.) Case 1: pick a failed delivery, show evidence and the assessment. Apply the buyer reply and show the reassessment. Case 2: try an address change and show the policy block. Keep the legend in one sentence: app, rules and tests are real; orders, notes and replies are simulated; nothing connects to Shopee or SPX.',
'impact': '[5:45-6:00] These are hypotheses to validate with real data, not results. We show no savings or accuracy numbers because we have none. Next: connect the LLM agent, run all 30 cases through an evaluator, pilot with permission.',
'flow': '[BACKUP] Detailed flow. Raw data goes through a pre-check; malformed or closed cases never reach the AI. Assessment 1 produces evidence and a hypothesis. The backend allows exactly one buyer question. A reply triggers assessment 2; a manual no-reply keeps assessment 1. The policy engine decides what is permitted; Ops receives the recommendation.',
'arch': '[BACKUP] Today a local Vite, React and TypeScript app. Fixtures stand in for data stores; a rule-based assessor stands in for the LLM; the policy gate and audit trail are real local code. Target design has the same layers backed by the 9-table data model.',
'qa': '[BACKUP, Q&A] Keep answers short and honest. LLM kept honest: fixed vocabularies and a deterministic gate. Real data: not accessed; next step needs permission. Where is the AI: the v2.2 contract, six fixed fields and the recommendation prompt define it; a rule-based assessor stands in today. Numbers: we claim none.'}
C=PP_ALIGN.CENTER; RT=PP_ALIGN.RIGHT
MID=MSO_ANCHOR.MIDDLE; TOP=MSO_ANCHOR.TOP; BOT=MSO_ANCHOR.BOTTOM

# ---------------------------------------------------------------- 1 Cover
s=prs.slides.add_slide(BLANK); f=s.background.fill; f.solid(); f.fore_color.rgb=PAPER
s.notes_slide.notes_text_frame.text=NOTES["cover"]
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

# ---------------------------------------------------------------- 2 Numbers (Hai to fill)
s=new(2,NOTES["numbers"],"1","Why it matters")
title(s,"Why this problem is worth solving")
tiles=[("[ __ ]","Shopee delivery operations","[Hai: failed-attempt figure from research]"),
       ("[ __ ]","Outside case study","[Hai: similar problem, what improved]"),
       ("[ __ ]","What it means for Ops","[Hai: estimate, labelled as an estimate]")]
for i,(n_,a,b) in enumerate(tiles):
    x=CX+i*2.7
    ln(s,x,1.75,x+2.5,1.75,KRAFT,2.25)
    T(s,x,1.8,2.5,0.9,[P(n_,40,TEAL,True,GEO)],anchor=MID)
    T(s,x,2.75,2.5,0.4,[P(a,16,INK,True,GEO)])
    T(s,x,3.2,2.5,0.9,[P(b,14,GREY)])
R(s,CX,4.3,7.9,0.5,fill=None,line=REDT,lw=1.5,dash=MSO_LINE.DASH,paras=[P("TO FILL by 9:00 on 30 Oct (Hai's research). Delete this slide if the numbers are not ready.",13,REDT,True,align=C)])

# ---------------------------------------------------------------- 3 Problem
s=new(3,NOTES["problem"],"2","Problem")
title(s,"A failed delivery shows what happened, not why")
items=["Ops sees a status code, not the reason.","Courier notes are vague and unverified.","A wrong guess wastes a trip or loses the order.","No record of why a decision was made."]
for i,t in enumerate(items):
    y=1.7+i*0.78
    hr(s,CX,5.6,y,KRAFT,0.75)
    T(s,CX,y+0.06,4.1,0.66,[P(t,16,INK)],anchor=MID)
R(s,6.1,1.75,3.3,1.05,fill=None,line=REDT,lw=2.25,paras=[P("recipient unavailable",22,REDT,False,GEO,italic=True,align=C)])
T(s,6.1,2.95,3.3,0.95,[P("Could mean: at work, wrong landmark, phone off, or a disrupted route.",16,INK)])
for k in range(22):
    R(s,6.15+k*0.14,4.2,0.045 if k%3 else 0.08,0.5,fill=INK)

# ---------------------------------------------------------------- 4 Solution (4 steps)
s=new(4,NOTES["solution"],"3","Solution")
title(s,"Order Rescue in four steps")
steps4=[("1","Read the case","Status, courier note, order history"),("2","Ask once","One question to the buyer, only if something is missing"),
        ("3","Check the rules","A policy check decides what is allowed"),("4","Recommend","Ops sees the suggestion and the evidence, then decides")]
cs4=[]
for i,(n_,a,b) in enumerate(steps4):
    x=CX+i*2.02
    cs4.append(R(s,x,1.55,1.85,2.1,fill=SAND,anchor=TOP,ml=0.14,mt=0.14,paras=[P(n_,28,TEAL,True,GEO,after=2),P(a,16,INK,True,GEO,after=4),P(b,14,INK)]))
    R(s,x,1.55,1.85,0.07,fill=TEAL if i<3 else RED)
for i in range(3): ln(s,0,0,1,1,INK,1.75,True,a=cs4[i],ai=3,b=cs4[i+1],bi=1)
T(s,CX,3.9,7.9,1.04,[P("The AI recommends. It never acts on its own.",18,TEAL,True,GEO,after=4),
                      P("Today a rule-based assessor plays the AI role; the LLM agent is the next step.",14,REDT,True)])

# ---------------------------------------------------------------- 5 Policy
s=new(5,NOTES["policy"],"4","Trust")
title(s,"The AI suggests. The rules decide.")
lp=R(s,CX,1.7,3.0,2.35,fill=SAND,anchor=TOP,ml=0.2,mt=0.15,paras=[P("AI suggests",18,TEAL,True,GEO,after=6)]+[P("•  "+t,14,INK,after=3) for t in ["Why delivery likely failed","What is still unknown","One question for the buyer","What to do next"]])
gate=R(s,4.95,1.5,0.16,2.75,fill=RED)
rp=R(s,5.7,1.7,3.7,2.35,fill=TEAL,anchor=TOP,ml=0.2,mt=0.15,paras=[P("Rules decide",18,PAPER,True,GEO,after=6)]+[P("•  "+t,14,PAPER,after=3) for t in ["Is the order still eligible?","Silence is not a refusal","A courier note alone is not proof","No address change or refund by the AI"]])
gy=1.7+2.35/2
ln(s,4.5,gy,4.95,gy,INK,1.75,True,b=gate,bi=1)
ln(s,5.11,gy,5.7,gy,INK,1.75,True,b=rp,bi=1)
T(s,CX,4.28,7.9,0.55,[P("High confidence never overrides the rules.",20,REDT,False,GEO,italic=True)])

# ---------------------------------------------------------------- 6 Codex
s=new(6,NOTES["codex"],"5","Use of Codex")
title(s,"How we used Codex")
rowsx=[("App","Local demo app: React, Vite, TypeScript. Assessor, policy gate and audit trail.",TEAL),
       ("Tests","Unit tests (Vitest) and a browser test of the demo flow (Playwright).",TEAL),
       ("Data and rules","Data model, business rules and 30 synthetic test cases.",TEAL),
       ("Process","Rules and test cases first, then build, then test against them.",TEAL),
       ("Next","Connect the LLM agent. Today a rule-based assessor stands in.",REDT)]
for i,(a,b,c) in enumerate(rowsx):
    y=1.2+i*0.72
    hr(s,CX,CR,y,KRAFT,0.75)
    T(s,CX,y+0.04,1.9,0.64,[P(a,20,c,True,GEO)],anchor=MID)
    T(s,3.5,y+0.04,5.9,0.64,[P(b,16,INK)],anchor=MID)

# ---------------------------------------------------------------- 7 Declaration
s=new(7,NOTES["declare"],"6","Declaration")
title(s,"What was built before, and what on the day")
R(s,CX,1.55,3.8,2.8,fill=SAND,anchor=TOP,ml=0.2,mt=0.15,paras=[P("Before 31 Oct (declared)",18,INK,True,GEO,after=6)]+[P("•  "+t,14,INK,after=3) for t in ["Data model v2.2","Business rules","30 synthetic test cases","First local prototype"]])
R(s,CX,1.55,3.8,0.07,fill=KRAFT_D)
R(s,5.6,1.55,3.8,2.8,fill=None,line=TEAL,lw=2.0,dash=MSO_LINE.DASH,anchor=TOP,ml=0.2,mt=0.15,paras=[P("On 31 Oct (at Shopee)",18,TEAL,True,GEO,after=6),P("[Fill at 5 PM: what was added or changed on the day]",14,REDT,True)])
T(s,CX,4.5,7.9,0.4,[P("Must match the declaration form submitted at 5 PM.",14,GREY)])

# ---------------------------------------------------------------- 8 Demo
s=new(8,NOTES["demo"],"7","Demo")
title(s,"Live demo: 2 minutes")
dsteps=[("1","Pick a failed delivery","See the evidence and the assessment"),("2","Apply the buyer reply","Watch the AI reassess"),("3","Try an address change","The rules block it")]
dc=[]
for i,(n_,a,b) in enumerate(dsteps):
    x=CX+i*2.7
    dc.append(R(s,x,1.5,0.5,0.5,fill=TEAL,shape=MSO_SHAPE.OVAL,paras=[P(n_,18,PAPER,True,GEO,align=C)],ml=0,mt=0))
    T(s,x,2.1,2.5,0.4,[P(a,16,INK,True,GEO)])
    T(s,x,2.55,2.5,0.7,[P(b,14,INK)])
for i in range(2): ln(s,CX+i*2.7+0.5,1.75,CX+(i+1)*2.7,1.75,TEAL,1.75,True)
leg=[("REAL","App, rules, tests",TEAL,None,PAPER,None),("SIMULATED","Orders, notes, buyer replies",SAND,KRAFT_D,INK,MSO_LINE.DASH),("NOT CONNECTED","Live Shopee/SPX data, messaging, dispatch",None,GREY,INK,MSO_LINE.SQUARE_DOT)]
for i,(a,b,f_,l_,tc,d) in enumerate(leg):
    R(s,CX+i*2.7,3.5,2.5,1.2,fill=f_,line=l_,lw=2.0,dash=d,anchor=TOP,ml=0.18,mt=0.14,paras=[P(a,14,tc,True,after=4),P(b,14,tc)])

# ---------------------------------------------------------------- 9 Impact + next
s=new(9,NOTES["impact"],"8","Impact and next")
title(s,"What it could change, and what comes next")
imp=[("9/30","Fewer wasted re-attempts","9 of 30 test cases change after the buyer reply"),
     ("30","Faster triage","Evidence ready for every case"),
     ("6","Clear reasons","Six traceable fields per decision")]
y=1.5
for i,(n_,a,b) in enumerate(imp):
    hr(s,CX,CR,y,KRAFT,0.75)
    T(s,CX,y+0.03,1.3,0.74,[P(n_,28,TEAL,True,GEO)],anchor=MID)
    T(s,2.85,y+0.03,6.55,0.74,[P(a,16,INK,True,GEO),P(b,14,INK)],anchor=MID)
    y+=0.8
T(s,CX,3.95,7.9,0.34,[P("Next: connect the LLM agent, run all 30 cases through an evaluator, pilot with permission.",14,INK,True)])
T(s,CX,4.4,7.9,0.5,[P("Case counts come from the 30 synthetic test cases. These are hypotheses, not measured results.",13,GREY)])

# ---------------------------------------------------------------- 5 Flow (swimlane)
s=new(10,NOTES["flow"],"B","Backup | Detailed flow")
title(s,"Detailed flow: two assessments, one question")
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

# ---------------------------------------------------------------- 8 Architecture (layers)
s=new(11,NOTES["arch"],"B","Backup | Architecture")
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

# ---------------------------------------------------------------- 12 Q&A backup
s=new(12,NOTES["qa"],"B","Backup | Q&A")
title(s,"Q&A backup")
qa=[("How do you stop made-up actions?","Fixed vocabularies and a rules gate."),
    ("Why only one buyer question?","Policy caps it at one."),
    ("What is real today?","Local app, rules and tests."),
    ("Where is the LLM?","Next step; a rule-based assessor stands in."),
    ("Where do numbers come from?","We claim none from the demo.")]
for i,(q,a) in enumerate(qa):
    y=1.3+i*0.68
    hr(s,CX,CR,y,KRAFT,0.75)
    T(s,CX,y+0.03,4.3,0.62,[P(q,15,INK,False,GEO,italic=True)],anchor=MID)
    T(s,5.9,y+0.03,3.5,0.62,[P(a,14,INK)],anchor=MID)

# ---------------------------------------------------------------- save
OUT='/home/team3/lucas/sea-hackathon/docs/slides/Order_Rescue_Pitch_Deck.pptx'
os.makedirs(os.path.dirname(OUT),exist_ok=True)
prs.save(OUT)
print('saved',OUT,len(prs.slides._sldIdLst),'slides')
