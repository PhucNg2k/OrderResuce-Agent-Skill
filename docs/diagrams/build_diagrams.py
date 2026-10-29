"""Generates the three .drawio diagrams used by the Software Architecture Document."""
import json, os
from xml.sax.saxutils import quoteattr
HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, '..', '..', 'src', 'data', 'Database model', 'Order_Rescue_Data_Model_30_Cases_v2.2.json')

C = dict(
    ui=('#DAE8FC', '#6C8EBF'), core=('#D5E8D4', '#82B366'), policy=('#FFE6CC', '#D79B00'),
    data=('#E1D5E7', '#9673A6'), ext=('#F5F5F5', '#666666'), warn=('#F8CECC', '#B85450'), plain=('#FFFFFF', '#666666'))

class Doc:
    def __init__(self): self.cells, self.n = [], 1
    def nid(self): self.n += 1; return f'c{self.n}'
    def box(self, x, y, w, h, text, kind='plain', dashed=False, shape='rounded=1', bold=False, size=12, parent='1', align='center', vertical='middle', extra=''):
        f, s = C[kind]; i = self.nid()
        st = f'{shape};whiteSpace=wrap;html=1;fillColor={f};strokeColor={s};fontSize={size};align={align};verticalAlign={vertical};' + ('dashed=1;dashPattern=6 4;' if dashed else '') + ('fontStyle=1;' if bold else '') + extra
        self.cells.append(f'<mxCell id="{i}" value={quoteattr(text)} style="{st}" vertex="1" parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def container(self, x, y, w, h, title, kind, dashed=False):
        f, s = C[kind]; i = self.nid()
        st = f'rounded=1;whiteSpace=wrap;html=1;fillColor={f};strokeColor={s};opacity=40;verticalAlign=top;align=left;spacingLeft=10;spacingTop=4;fontStyle=1;fontSize=12;' + ('dashed=1;dashPattern=8 4;' if dashed else '') + 'arcSize=4;'
        self.cells.append(f'<mxCell id="{i}" value={quoteattr(title)} style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def label(self, x, y, w, h, text, size=11, align='left', color='#333333', bold=False):
        i = self.nid()
        self.cells.append(f'<mxCell id="{i}" value={quoteattr(text)} style="text;html=1;whiteSpace=wrap;align={align};verticalAlign=middle;fontSize={size};fontColor={color};{"fontStyle=1;" if bold else ""}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def edge(self, a, b, label='', dashed=False, color='#333333', exit=None, entry=None, pts=None, end='classic'):
        i = self.nid()
        st = f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={color};endArrow={end};fontSize=10;labelBackgroundColor=#ffffff;' + ('dashed=1;' if dashed else '')
        if exit: st += f'exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;'
        if entry: st += f'entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;'
        arr = ''.join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in (pts or []))
        arr = f'<Array as="points">{arr}</Array>' if arr else ''
        self.cells.append(f'<mxCell id="{i}" value={quoteattr(label)} style="{st}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')
    def save(self, name, w, h):
        xml = f'<mxfile host="drawio"><diagram name="{name}" id="{name}"><mxGraphModel dx="{w}" dy="{h}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{w}" pageHeight="{h}" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(self.cells) + '</root></mxGraphModel></diagram></mxfile>'
        open(os.path.join(HERE, name + '.drawio'), 'w', encoding='utf-8').write(xml)

# ---------- 1. System architecture ----------
def architecture():
    d = Doc()
    d.label(20, 8, 1000, 24, 'Order Rescue: system architecture (solid = implemented in the local MVP, dashed = target / not yet built)', 13, bold=True)
    ops = d.box(40, 52, 170, 44, 'Ops reviewer (human)', 'plain')
    buyer = d.box(250, 52, 200, 44, 'Buyer reply (scripted / simulated)', 'ext', dashed=True)
    pres = d.container(20, 120, 560, 130, 'Presentation: React + Vite + TypeScript (implemented)', 'ui')
    for i, n in enumerate(['ScenarioList', 'AssessmentPanel', 'EvidencePanel', 'PolicyResultPanel', 'AuditTimeline', 'TruthLegend + flow diagrams']):
        d.box(35 + (i % 3) * 180, 152 + (i // 3) * 48, 165, 38, n, 'ui', size=11)
    app = d.container(20, 270, 560, 90, 'Application state (implemented)', 'ui')
    d.box(35, 300, 250, 44, 'useDemoSession (per-scenario session, re-assessment)', 'ui', size=11)
    d.box(310, 300, 250, 44, 'buildDecisionRecord (audit record)', 'ui', size=11)
    core = d.container(20, 380, 560, 160, 'Decision core', 'core')
    assess = d.box(35, 412, 160, 56, 'assessCase: deterministic assessor (MVP v1 rules)', 'core', size=11)
    valid = d.box(215, 412, 160, 56, 'Schema + source_ref check', 'core', dashed=True, size=11)
    agent = d.box(405, 412, 160, 56, 'LLM Agent runner: prompt v2, six-field assessment', 'core', dashed=True, size=11)
    gate = d.box(35, 480, 530, 48, 'Policy gate (deterministic): eligibility, policy_gate, final_action, reason. The LLM only proposes candidate_action', 'policy', size=11, bold=True)
    data = d.container(640, 250, 380, 130, 'Data (feeds the scenario input)', 'data')
    d.box(655, 280, 350, 38, 'Synthetic fixtures: scenarios.ts, 5 scenarios (implemented)', 'data', size=11)
    d.box(655, 326, 350, 46, 'v2.2 data model: 9 tables, 30 seed cases (JSON). DB engine not selected', 'data', dashed=True, size=11)
    oai = d.box(640, 410, 200, 56, 'OpenAI API (future, called server-side only)', 'ext', dashed=True, size=11)
    shp = d.box(870, 410, 150, 70, 'Shopee / SPX systems: NOT connected', 'warn', dashed=True, size=11)
    ev = d.container(20, 570, 1000, 90, 'Offline evaluation harness (not part of the runtime)', 'plain', dashed=True)
    d.box(35, 600, 300, 46, '30 golden test cases (draft labels), never shown to the Agent', 'plain', size=11)
    d.box(355, 600, 330, 46, 'Simulated runs + graders: exact match on enums, set match on missing_info', 'plain', size=11)
    d.box(705, 600, 300, 46, 'Reports: review report, prompt evaluation report', 'plain', size=11)
    d.edge(ops, pres, '', exit=(0.5, 1), entry=(0.2, 0))
    d.edge(buyer, pres, '', dashed=True, exit=(0.5, 1), entry=(0.6, 0))
    d.edge(pres, app, 'UI actions and state', exit=(0.5, 1), entry=(0.5, 0))
    d.edge(app, core, 'assess request / result', exit=(0.5, 1), entry=(0.5, 0))
    d.edge(data, app, '', exit=(0, 0.5), entry=(1, 0.5))
    d.edge(agent, oai, 'prompt + input', dashed=True, exit=(1, 0.5), entry=(0, 0.5), color='#777777')
    d.edge(agent, valid, '', dashed=True, exit=(0, 0.5), entry=(1, 0.5))
    d.edge(valid, gate, '', dashed=True, exit=(0.5, 1), entry=(0.5, 0))
    d.edge(assess, gate, '', exit=(0.5, 1), entry=(0.2, 0))
    d.edge(ev, core, 'runs the prompt offline', dashed=True, exit=(0.5, 0), entry=(0.5, 1))
    d.save('architecture_overview', 1060, 680)

# ---------- 2. Two-assessment flow ----------
def flow():
    d = Doc()
    d.label(20, 8, 900, 24, 'Order Rescue: two-assessment case flow (v2.2 contract). A case ends in exactly one final assessment', 13, bold=True)
    raw = d.box(30, 60, 150, 56, 'Raw input<br>case, order, failed event,<br>T0 buyer context', 'data', size=11)
    pre = d.box(225, 52, 150, 72, 'Backend pre-check<br>lifecycle, deadline, PII,<br>duplicate trigger', 'policy', shape='rhombus', size=11)
    a1 = d.box(430, 60, 160, 56, 'Agent assessment 1<br>six fields', 'core', size=11, bold=True)
    st1 = d.box(640, 60, 170, 56, 'Store initial assessment<br>+ initial policy output<br>status ASSESSED', 'data', size=11)
    blocked = d.box(225, 170, 150, 50, 'No AI call. Route to Ops<br>(outside the 30-case suite)', 'warn', size=11)
    gate = d.box(640, 160, 170, 72, 'Contact gate<br>question permitted?', 'policy', shape='rhombus', size=11)
    q = d.box(640, 280, 170, 56, 'Emit ONE buyer question<br>WAITING_FOR_BUYER', 'plain', size=11, bold=True)
    nogate = d.box(430, 175, 160, 50, 'Denied: not defined in v2.2<br>(open decision)', 'ext', dashed=True, size=11)
    out = d.box(640, 380, 170, 72, 'Outcome?', 'policy', shape='rhombus', size=11)
    rep = d.box(380, 392, 190, 48, 'BUYER_REPLY (matching question_id)', 'plain', size=11)
    a2 = d.box(380, 480, 190, 56, 'Agent assessment 2<br>raw input + reply, six fields<br>+ policy', 'core', size=11, bold=True)
    f2 = d.box(380, 570, 190, 48, 'Final = copy of assessment 2<br>final_assessment_source = 2', 'data', size=11)
    nr = d.box(880, 392, 200, 48, 'USER_NO_REPLY (manual demo button)', 'plain', size=11)
    f1 = d.box(880, 480, 200, 56, 'No second Agent call.<br>Final = copy of initial<br>final_assessment_source = 1', 'data', size=11)
    done = d.box(640, 600, 170, 56, 'COMPLETED<br>recommendation shown to Ops', 'core', size=11, bold=True)
    nex = d.box(640, 690, 170, 56, 'Nothing is executed: no dispatch,<br>no message, no address or COD edit', 'warn', size=11)
    d.edge(raw, pre); d.edge(pre, a1, 'eligible'); d.edge(a1, st1)
    d.edge(pre, blocked, 'blocked', exit=(0.5, 1), entry=(0.5, 0))
    d.edge(st1, gate, '', exit=(0.5, 1), entry=(0.5, 0))
    d.edge(gate, q, 'permitted', exit=(0.5, 1), entry=(0.5, 0))
    d.edge(gate, nogate, 'denied', dashed=True, exit=(0, 0.5), entry=(1, 0.5))
    d.edge(q, out, '', exit=(0.5, 1), entry=(0.5, 0))
    d.edge(out, rep, 'buyer replies', exit=(0, 0.5), entry=(1, 0.5))
    d.edge(rep, a2, '', exit=(0.5, 1), entry=(0.5, 0)); d.edge(a2, f2, '', exit=(0.5, 1), entry=(0.5, 0))
    d.edge(out, nr, 'no reply (button)', exit=(1, 0.5), entry=(0, 0.5))
    d.edge(nr, f1, '', exit=(0.5, 1), entry=(0.5, 0))
    d.edge(f2, done, '', exit=(1, 0.5), entry=(0, 0.5)); d.edge(f1, done, '', exit=(0.5, 1), entry=(1, 0.5), pts=[(980, 628)])
    d.edge(done, nex, 'scope limit', dashed=True, color='#B85450')
    d.save('case_flow', 1120, 780)

# ---------- 3. ERD ----------
def shorten(ty):
    t = ty.split(',')[0].split(';')[0].split(' (')[0].strip()
    if '|' in t and all(p.replace('_', '').isalnum() and p.upper() == p for p in t.split('|')):
        return 'enum'
    return t if len(t) <= 24 else t[:23] + '.'

def erd():
    m = json.load(open(MODEL, encoding='utf-8'))['schema']
    fks = {}
    for r in m['relationships']:
        t, c = r['to'].split('.'); fks.setdefault(t, set()).add(c)
    d = Doc(); ids = {}
    pos = {'dim_buyer': (30, 50), 'dim_product': (30, 190), 'dim_carrier': (30, 310), 'dim_date': (30, 400),
           'fact_order': (330, 50), 'fact_delivery_event': (330, 270), 'order_rescue': (640, 50),
           'fact_rescue_interaction': (960, 50), 'dim_action': (960, 520)}
    W = {'order_rescue': 300, 'fact_rescue_interaction': 270}
    d.label(20, 8, 1000, 24, 'Order Rescue: data model v2.2 (9 tables, 67 columns, 9 relationships)', 13, bold=True)
    for t, (x, y) in pos.items():
        cols = m['tables'][t]['columns']; pk = set(m['tables'][t]['primary_key'])
        rows = []
        for c, ty in cols.items():
            tag = ' PK' if c in pk else (' FK' if c in fks.get(t, ()) else '')
            short = shorten(ty)
            rows.append(f'{c}: {short}{tag}')
        w = W.get(t, 250); h = 26 + 17 * len(rows)
        kind = 'policy' if t == 'order_rescue' else ('data' if t.startswith('dim') else 'ui')
        f, s = C[kind]; i = d.nid(); ids[t] = i
        d.cells.append(f'<mxCell id="{i}" value="{t}" style="swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=0;marginBottom=0;fillColor={f};strokeColor={s};fontSize=12;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        for k, rtxt in enumerate(rows):
            j = d.nid(); bold = 'fontStyle=1;' if rtxt.endswith(' PK') else ''
            d.cells.append(f'<mxCell id="{j}" value={quoteattr(rtxt)} style="text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=6;fontSize=10;{bold}" vertex="1" parent="{i}"><mxGeometry y="{26 + 17 * k}" width="{w}" height="17" as="geometry"/></mxCell>')
    E = [('dim_buyer', 'fact_order', '1:N', (1, .2), (0, .2)), ('dim_product', 'fact_order', '1:N opt.', (1, .3), (0, .45)),
         ('fact_order', 'fact_delivery_event', '1:N', (.5, 1), (.5, 0)), ('dim_carrier', 'fact_delivery_event', '1:N opt.', (1, .5), (0, .35)),
         ('dim_date', 'fact_delivery_event', '1:N', (1, .5), (0, .8)), ('fact_order', 'order_rescue', '1:N', (1, .2), (0, .12)),
         ('fact_delivery_event', 'order_rescue', '1:0..1 (UK)', (1, .3), (0, .55)), ('order_rescue', 'fact_rescue_interaction', '1:N', (1, .15), (0, .15)),
         ('dim_action', 'order_rescue', '1:N (final_action_id)', (0, .5), (1, .88))]
    for a, b, lab, ex, en in E: d.edge(ids[a], ids[b], lab, exit=ex, entry=en, end='ERmandOne' if False else 'classic')
    d.save('data_model_erd', 1300, 900)

architecture(); flow(); erd()
print('ok')
