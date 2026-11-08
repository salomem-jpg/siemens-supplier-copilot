"""Siemens Energy supplier capability studio — independent synthetic Streamlit demo.

Eight-stage guided engagement + evidence-matched solutions + two-sided economics.
For student project demonstration, not official Siemens tools or approvals.
"""
from __future__ import annotations

import copy
import hashlib
import html
import hmac
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

import engine as E

st.set_page_config(page_title="Supplier Capability Studio | Demo", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# Streamlit Community Cloud session state is NOT a permanent shared database.
if 'cases' not in st.session_state:
    st.session_state.cases=E.new_cases()
if 'selected_case' not in st.session_state:
    st.session_state.selected_case=next(iter(st.session_state.cases))
if 'conversation' not in st.session_state:
    st.session_state.conversation={}

st.markdown('''<style>
:root { --navy:#082e5c; --blue:#145da0; --yellow:#f8c50a; --light:#f3f6f9; --ink:#17314e; }
html,body,[class*="css"]{font-family:Arial,Helvetica,sans-serif}
.stApp{background:#f8f9fc;color:#152a41}
[data-testid="stSidebar"]{background:#0b2f59}
[data-testid="stSidebar"] * {color:#eaf2fb}
[data-testid="stSidebar"] input,[data-testid="stSidebar"] select{color:#152a41!important}
[data-testid="stSidebar"] [data-baseweb="select"] *{color:inherit}
[data-testid="stSidebar"] .stButton>button{background:#174f85;border-color:#3d6f9e;color:white}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:2px}
h1,h2,h3{color:#092f58;letter-spacing:-.025em}
h1{font-size:1.9rem!important}h2{font-size:1.36rem!important}
[data-testid="stMetric"]{padding:14px 16px;background:white;border:1px solid #e0e7ef;border-radius:8px}
[data-testid="stMetricLabel"]{font-size:.8rem}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:8px}
.stButton>button[kind="primary"]{background:#0e5b9f;border-color:#0e5b9f;color:white}
.stButton>button:hover{border-color:#f8c50a}
.block-container{max-width:1460px;padding-top:1.65rem;padding-bottom:3rem}
.headline{background:#082f5e;color:white;padding:20px 26px 21px;border-radius:8px;margin-bottom:18px;border-left:8px solid #f8c50a}
.headline h1{color:white;font-size:1.85rem!important;margin:0 0 4px}
.headline p{color:#d9e6f3;margin:0;font-size:.9rem}
.kicker{text-transform:uppercase;letter-spacing:.11em;font-weight:700;color:#276aa7;font-size:.72rem}
.stepnote{background:#f1f6fb;border-left:4px solid #1460a2;padding:12px 15px;margin:9px 0 19px;color:#28516e}
.sec{font-size:1.1rem;font-weight:700;margin:1.1rem 0 .5rem;color:#0b3765}
.compact{font-size:.84rem;color:#60748b}
.warn{font-size:.8rem;color:#74560a;padding:8px;background:#fff9e4;border-radius:5px}
</style>''',unsafe_allow_html=True)


def secret_value(key:str, default=''):
    try: return st.secrets.get(key,os.getenv(key,default))
    except (FileNotFoundError,KeyError):return os.getenv(key,default)


def access_gate():
    token=str(secret_value('APP_PASSWORD','')).strip()
    if not token: return True
    if st.session_state.get('logged_in'):return True
    st.markdown('<div class="headline"><h1>Supplier Capability Studio</h1><p>Restricted student demonstration</p></div>',unsafe_allow_html=True)
    entered=st.text_input('Demo password',type='password')
    if st.button('Open prototype',type='primary'):
        if hmac.compare_digest(entered,token):
            st.session_state.logged_in=True;st.rerun()
        st.error('Incorrect password')
    st.caption('Do not enter Siemens credentials here. This basic demo password is not enterprise authentication.')
    return False

if not access_gate(): st.stop()


def eur(v, currency='EUR'):
    symbol={'EUR':'€','USD':'$','GBP':'£'}.get(currency,currency+' ')
    v=float(v)
    return f'{symbol}{v/1e6:,.2f}m' if abs(v)>=100000 else f'{symbol}{v:,.0f}'


def case_obj():
    return st.session_state.cases[st.session_state.selected_case]


def update(fields:dict):
    E.revise_case(case_obj(),fields)
    st.rerun()


def status_tag(ok):return '✓ PASS' if ok else '● REVIEW'


def allow_completion(n:int):
    case=case_obj();allowed,reason=E.stage_check(case,n)
    if case.get('completed_stage',0)>=n:
        st.success(f'Stage {n} is recorded as completed in this synthetic scenario.')
        return
    if n>case.get('completed_stage',0)+1:
        st.info(f'Complete Stage {case.get("completed_stage",0)+1} first. Steps must be recorded in order.')
        return
    if not allowed:st.warning(f'Stage {n} cannot proceed yet: {reason}')
    if st.button(f'Record Stage {n} complete',disabled=not allowed,type='primary',key=f'complete-{n}'):
        try:E.complete_stage_local(case,n);st.rerun()
        except ValueError as exc:st.error(str(exc))


def heading(title,subtitle,stage=None):
    st.markdown('<div class="kicker">'+('Stage '+str(stage)+' · ' if stage else '')+'Supplier capability-building</div>',unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


# left sidebar
with st.sidebar:
    st.markdown('## ⚡ Capability Studio')
    st.caption('SIEMENS ENERGY · STUDENT DEMO')
    st.divider()
    ids=list(st.session_state.cases.keys())
    chosen=st.selectbox('Supplier case',ids,format_func=lambda x:st.session_state.cases[x]['name'],index=ids.index(st.session_state.selected_case))
    if chosen!=st.session_state.selected_case:
        st.session_state.selected_case=chosen
        st.rerun()
    c=case_obj()
    st.caption(f'{c["type"]} supplier  ·  {c["id"]}')
    st.progress(min(int(c.get('completed_stage',0))/8,1.0),text=f'{int(c.get("completed_stage",0))}/8 stages recorded')
    pages=['Portfolio','1 · Business need','2 · Diagnosis','3 · Interventions','4 · Feasibility','5 · Commitment','6 · Implementation','7 · Verification','8 · Handover','Specialist agents','Official questionnaire','Benchmark research','Snowflake data','Ask the copilot','Export / import']
    page=st.radio('Workspace',pages,label_visibility='collapsed')
    st.divider()
    st.caption('**Demo only** · Fictional suppliers and financials. Session edits are not permanent cloud storage.')
    if st.button('Reset selected demo case',use_container_width=True):
        seed=next((x for x in E.CASES if x['id']==c['id']),None)
        if seed: st.session_state.cases[c['id']]=copy.deepcopy(seed);st.rerun()
        else: st.warning('Imported case has no built-in seed.')

c=case_obj(); f=c.get('finance',{}); calculations=E.calc(c)
st.markdown('<div class="headline"><h1>Supplier Capability Studio</h1><p>Eight-stage engagement model · evidence-backed interventions · two-sided feasibility</p></div>',unsafe_allow_html=True)

if page=='Portfolio':
    heading('Supplier portfolio','Select a synthetic supplier case to see how different capability gaps and incentives change the recommended path.')
    rows=[]
    for item in st.session_state.cases.values():
        v=E.calc(item)
        rows.append({'Supplier':item['name'],'Type':item['type'],'Criteria':', '.join(item.get('criteria',[])), 'Stage completed':item.get('completed_stage',0), 'Siemens net value (EUR)':round(v['net']), 'Current outcome':v['disposition']})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    a,b,d,e=st.columns(4)
    a.metric('Supplier scenarios',len(rows));b.metric('Capability criteria',len(E.CRITERIA));d.metric('Intervention candidates',len(E.INTERVENTIONS));e.metric('Official survey items',len(E.SURVEY['ratedQuestions']))
    st.markdown('### Selected supplier: '+c['name'])
    x,y,z=st.columns(3)
    x.info('**Business need**\n\n'+str(c.get('trigger','')))
    y.info('**Identified gaps**\n\n'+str(c.get('gap','')))
    z.info('**Decision status**\n\n'+calculations['disposition'])
    st.markdown('#### Workflow status')
    for row in E.stage_status(c):
        icon='✓' if row['completed'] else ('◉' if row['current'] else '○')
        with st.container(border=True):
            cols=st.columns([.5,5,3])
            cols[0].markdown(f'**{icon}**')
            cols[1].write(f'**{row["stage"]}. {row["name"]}**')
            cols[2].caption('Recorded' if row['completed'] else ('Ready' if row['pass_check'] else 'Needs evidence / action'))
    st.warning('This is a student proof of concept. Supplier scores, interventions, probabilities and decisions are illustrative, not Siemens Energy policy.')

elif page=='1 · Business need':
    heading('Identify trigger & prioritize','Capture the business requirement, needed outcome, urgency, and accountable owner.',1)
    with st.form('intake_form'):
        a,b=st.columns(2)
        name=a.text_input('Supplier',value=c.get('name',''))
        supplier_type=b.selectbox('Relationship',['Existing','New'],index=['Existing','New'].index(c.get('type','Existing')))
        trigger=st.text_area('Business trigger',value=c.get('trigger',''))
        objective=st.text_area('Required business outcome',value=c.get('objective',''))
        d1,d2,d3=st.columns(3)
        need_date=d1.text_input('Need-by date (YYYY-MM-DD)',value=c.get('need_date',''))
        owner=d2.text_input('Siemens owner',value=c.get('owner',''))
        country=d3.text_input('Country',value=c.get('country',''))
        if st.form_submit_button('Save intake',type='primary'):
            update(dict(name=name,type=supplier_type,trigger=trigger,objective=objective,need_date=need_date,owner=owner,country=country))
    allow_completion(1)

elif page=='2 · Diagnosis':
    heading('Diagnose supplier capability gap','Use assessment evidence and the 16 project criteria. Questionnaire scores alone do not confirm a gap.',2)
    criterion_names={r['code']:r['label'] if 'label' in r else r.get('name',r['code']) for r in E.CRITERIA}
    options=list(criterion_names)
    with st.form('diagnosis_form'):
        criteria=st.multiselect('Relevant capability criteria',options,default=c.get('criteria',[]),format_func=lambda k:f'{k} · {criterion_names[k]}')
        gap=st.text_area('Capability gap (not just the performance symptom)',value=c.get('gap',''))
        evidence=st.text_area('Supporting evidence, baseline, and outstanding questions',value=c.get('evidence',''),height=130)
        if st.form_submit_button('Save diagnosis draft',type='primary'):
            update({'criteria':criteria,'gap':gap,'evidence':evidence})
    if c.get('data_snapshot'):
        with st.expander('Attached synthetic Snowflake data'):
            st.json(c['data_snapshot'])
    st.divider()
    st.write('**Assessor decision (synthetic scenario)**')
    st.caption('A human assessor must confirm source sufficiency and the gap. This is a demo attestation, not independent evidence verification.')
    st.write(f"Evidence verified: **{bool(c.get('evidence_verified'))}**  ·  Diagnosis approved: **{bool(c.get('diagnosis_approved'))}**")
    confirm=st.checkbox('I reviewed the evidence and confirm this illustrative diagnosis',key=f'diag-confirm-{c["id"]}')
    if st.button('Record assessor confirmation',disabled=not confirm or not c.get('evidence') or not c.get('criteria'),key='confirm-diagnosis'):
        update({'evidence_verified':True,'diagnosis_approved':True})
    if st.button('Reopen diagnosis',key='reopen-diagnosis'):
        update({'evidence_verified':False,'diagnosis_approved':False})
    allow_completion(2)

elif page=='3 · Interventions':
    heading('Identify and tailor business solutions','Recommendations are candidate practices matched to documented criteria, not automatically approved solutions.',3)
    picks=E.recommendations(c,limit=30)
    if not picks:
        st.warning('No researched intervention matches this case. Return to Stage 2 and review criteria and evidence.')
    else:
        d=[]
        for r in picks:d.append({'ID':r['id'],'Intervention':r['name'],'Matching criteria':', '.join(r['matched']),'Evidence status':r['evidence_status'],'Research reference':r['reference']})
        st.dataframe(pd.DataFrame(d),use_container_width=True,hide_index=True)
        selected=st.multiselect('Proposed shortlist',options=[r['id'] for r in picks],default=[x for x in c.get('selected',[]) if x in [r['id'] for r in picks]],format_func=lambda rid:next((f'{r["name"]} · {r["evidence_status"]}' for r in picks if r['id']==rid),rid))
        if st.button('Save shortlisted interventions',key='save-shortlist'):
            update({'selected':selected})
        for r in picks[:8]:
            with st.expander(f"{r['name']} — {r['evidence_status']}"):
                st.write('**Mechanism:** '+r.get('mechanism',''))
                st.write('**Evidence / transfer limitations:** '+r.get('boundary',''))
                st.caption('Research source: '+r['reference'])
        approval=st.checkbox('Siemens reviewer has evaluated evidence and adaptation assumptions (simulated)',key=f'solution-approval-{c["id"]}')
        if st.button('Record shortlist review',disabled=not approval or not c.get('selected') or not c.get('diagnosis_approved'),key='approve-shortlist'):
            update({'solution_approved':True})
    allow_completion(3)

elif page=='4 · Feasibility':
    heading('Business value & feasibility','Four sequential gates: technical, timing, Siemens economics, and supplier willingness. All numbers are illustrative.',4)
    q=E.calc(c);currency=f.get('currency','EUR')
    m1,m2,m3,m4=st.columns(4)
    m1.metric('Potential Siemens gain',eur(q['gross_gain'],currency))
    m2.metric('Success probability',f"{q['probability']:.1%}")
    m3.metric('Siemens intervention cost',eur(q['total_cost'],currency))
    m4.metric('Expected net value',eur(q['net'],currency))
    st.latex(r"\mathrm{Net\ Value}=\mathrm{Gain}\times(P_{technical}\times P_{on\ time}\times P_{sustained})-\mathrm{Cost}")
    for g in q['gates']:
        if g['passed']:st.success(f"{status_tag(True)} · {g['name']} — {g['reason']}")
        else:st.warning(f"{status_tag(False)} · {g['name']} — {g['reason']}")
    with st.expander('Edit Gate 1–3 assumptions and Siemens cost',expanded=False):
        with st.form('finance_inputs'):
            a,b=st.columns(2)
            gain=a.number_input('Gross benefit / protected value',min_value=0.0,value=float(f.get('gain',0)),step=100000.0,format='%.0f')
            horizon=b.number_input('Months in business-case horizon',min_value=1,max_value=120,value=int(f.get('horizon_months',24)))
            pp1,pp2,pp3=st.columns(3)
            ptech=pp1.number_input('P(technical closure)',min_value=0.,max_value=1.,value=float(f.get('p_technical',.75)),step=.01,format='%.4f')
            ptime=pp2.number_input('P(on-time completion)',min_value=0.,max_value=1.,value=float(f.get('p_on_time',.75)),step=.01,format='%.4f')
            psust=pp3.number_input('P(sustained result)',min_value=0.,max_value=1.,value=float(f.get('p_sustain',.75)),step=.01,format='%.4f')
            cost_keys=['cost_experts','cost_travel','cost_testing','cost_tooling','cost_incentives']
            cost_labels=['Siemens experts','Travel','Testing','Tooling funded by Siemens','Commercial incentives']
            costs={}
            aa,bb=st.columns(2)
            for i,(key,label) in enumerate(zip(cost_keys,cost_labels)):
                costs[key]=(aa if i%2==0 else bb).number_input(label,min_value=0.,value=float(f.get(key,0)),step=10000.0,format='%.0f')
            ok1,ok2=st.columns(2)
            tech_ok=ok1.checkbox('Gate 1: technical feasibility confirmed',value=bool(f.get('tech_ok',False)))
            timing_ok=ok2.checkbox('Gate 2: timing / resources confirmed',value=bool(f.get('timing_ok',False)))
            gain_basis=st.text_area('Business gain basis (what creates value)',value=f.get('gain_basis',''))
            if st.form_submit_button('Update Siemens case',type='primary'):
                update({'finance':{'gain':gain,'horizon_months':horizon,'p_technical':ptech,'p_on_time':ptime,'p_sustain':psust,'tech_ok':tech_ok,'timing_ok':timing_ok,'gain_basis':gain_basis,**costs}})
    st.markdown('### Gate 4 · Supplier business case')
    s1,s2,s3=st.columns(3)
    s1.metric('Supplier potential benefits',eur(q['supplier_value'],currency))
    s2.metric('Supplier CapEx + OpEx',eur(q['supplier_cost'],currency))
    s3.metric('Illustrative supplier balance',eur(q['supplier_balance'],currency))
    st.caption('This is an undiscounted scenario balance, not a validated supplier NPV. Future orders are not guaranteed.')
    with st.expander('Edit supplier economics, commitment mechanisms, and uncertainty',expanded=False):
        with st.form('supplier_inputs'):
            aa,bb=st.columns(2)
            skeys=['supplier_capex','supplier_opex','supplier_contribution','retained_savings','productivity_relief','other_customer_upside']
            labels=['Supplier capital expenditure','Supplier operating expenditure','Siemens-funded supplier contribution','Supplier-retained savings','Reduced annual productivity ask benefit','Other-customer capacity upside']
            updates={}
            for i,(k,label) in enumerate(zip(skeys,labels)):
                updates[k]=(aa if i%2==0 else bb).number_input(label,min_value=0.,value=float(f.get(k,0)),step=25000.,format='%.0f')
            willingness=st.selectbox('Supplier willingness',['Unknown','No','Yes with conditions','Yes'],index=['Unknown','No','Yes with conditions','Yes'].index(f.get('supplier_willing','Unknown')))
            volume=st.text_input('Order / forecast status',value=f.get('volume_status',''))
            mechanism=st.text_area('Commercial or non-cash incentive being considered',value=f.get('mechanism',''))
            qlow,qhigh=st.columns(2)
            low=qlow.number_input('Illustrative low success probability',value=float(f.get('p_low',0.2)),min_value=0.,max_value=1.,step=.01)
            high=qhigh.number_input('Illustrative high success probability',value=float(f.get('p_high',0.8)),min_value=0.,max_value=1.,step=.01)
            if st.form_submit_button('Update supplier case',type='primary'):
                update({'finance':{'supplier_willing':willingness,'volume_status':volume,'mechanism':mechanism,'p_low':low,'p_high':high,**updates}})
    if q.get('scenario_net_range'):
        lo,hi=q['scenario_net_range'];st.info(f"Sensitivity across entered probabilities: **{eur(lo,currency)} to {eur(hi,currency)}** net. This is a user-entered scenario range, not a statistical confidence interval.")
    st.markdown('### Human judgment')
    if q['blockers']:
        for reason in q['blockers']:st.warning(reason)
    st.write('Recorded decision: **'+q['recorded_decision']+'**')
    review=st.checkbox('I am recording an illustrative reviewer decision; not a real Siemens approval',key=f'review-{c["id"]}')
    x,y=st.columns(2)
    if x.button('Record simulated GO',type='primary',disabled=bool(q['blockers']) or not review):
        update({'finance':{'sponsor_review':'Approved in simulated scenario'}})
    if y.button('Record REVISE / HOLD',disabled=not review):
        update({'finance':{'sponsor_review':'Revise / hold in simulated scenario'}})
    allow_completion(4)

elif page=='5 · Commitment':
    heading('Agree and commit','Convert a feasible solution into clear responsibilities, milestones, resource commitments, and dual approvals.',5)
    k=c.get('commitments',{})
    with st.form('commit_form'):
        a,b=st.columns(2)
        siemens_owner=a.text_input('Siemens engagement owner',value=k.get('siemens_owner',''))
        supplier_owner=b.text_input('Supplier owner',value=k.get('supplier_owner',''))
        milestone=st.text_area('First verifiable milestone / agreed scope',value=k.get('milestone',''))
        x,y=st.columns(2)
        se_ok=x.checkbox('Siemens simulated approval',value=bool(k.get('siemens_approved',False)))
        supplier_ok=y.checkbox('Supplier simulated approval',value=bool(k.get('supplier_approved',False)))
        if st.form_submit_button('Save commitments',type='primary'):
            update({'commitments':{'siemens_owner':siemens_owner,'supplier_owner':supplier_owner,'milestone':milestone,'siemens_approved':se_ok,'supplier_approved':supplier_ok}})
    st.warning('Commercial and contracting terms must be approved outside this tool. A simulated checkbox cannot authorize commitments.')
    allow_completion(5)

elif page=='6 · Implementation':
    heading('Implement capability building','Track actual work packages, responsible owners, dates, progress and source evidence.',6)
    actions=c.get('actions',[])
    rows=copy.deepcopy(actions) or [{'task':'','owner':'','due':'','status':'Not started','evidence':''}]
    st.caption('Add or remove rows. Every action must be Done and supported by evidence before Stage 6 can close.')
    with st.form('actions_form'):
        ed=st.data_editor(pd.DataFrame(rows),hide_index=True,use_container_width=True,num_rows='dynamic',column_config={'status':st.column_config.SelectboxColumn('Status',options=['Not started','In progress','Blocked','Done'])},key='action_editor')
        if st.form_submit_button('Save implementation plan',type='primary'):
            new=ed.fillna('').to_dict('records')
            new=[{'task':str(a.get('task','')),'owner':str(a.get('owner','')),'due':str(a.get('due','')),'status':str(a.get('status','Not started')),'evidence':str(a.get('evidence',''))} for a in new if str(a.get('task','')).strip()]
            update({'actions':new})
    allow_completion(6)

elif page=='7 · Verification':
    heading('Verify and review','Compare the measured outcome against agreed targets and document independent evidence and sustainment.',7)
    v=c.get('verification',{})
    with st.form('verification_form'):
        metric=st.text_input('Performance metric',value=v.get('metric',''))
        a,b,d=st.columns(3)
        baseline=a.number_input('Baseline',value=float(v.get('baseline',0)),step=1.0)
        target=b.number_input('Target',value=float(v.get('target',0)),step=1.0)
        actual=d.number_input('Actual result',value=float(v.get('actual',0)),step=1.0)
        evidence=st.text_area('Verified measurement record',value=v.get('evidence',''))
        verifier=st.text_input('Independent verifier',value=v.get('verifier',''))
        sustained=st.checkbox('Evidence supports a sustained result',value=bool(v.get('sustained',False)))
        if st.form_submit_button('Save verification',type='primary'):
            update({'verification':dict(metric=metric,baseline=baseline,target=target,actual=actual,evidence=evidence,verifier=verifier,sustained=sustained)})
    allow_completion(7)

elif page=='8 · Handover':
    heading('Close, hand over and learn','Document the sustaining owner, follow-up triggers, lessons and a human closure decision.',8)
    k=c.get('closure',{})
    with st.form('closure_form'):
        owner=st.text_input('Sustainment owner',value=k.get('owner',''))
        followup=st.text_area('Ongoing review and follow-up trigger',value=k.get('followup',''))
        lessons=st.text_area('Lessons to reuse in future engagements',value=k.get('lessons',''))
        approved_by=st.text_input('Person recording closure decision (synthetic)',value=k.get('approved_by',''))
        if st.form_submit_button('Save closure',type='primary'):
            update({'closure':dict(owner=owner,followup=followup,lessons=lessons,approved_by=approved_by)})
    allow_completion(8)

elif page=='Specialist agents':
    heading('Three domain specialists & coordinator','Domain analyses are separated by the problem type. Only active domains return intervention leads.')
    agents=E.specialist_analysis(c)
    tabA,tabB,tabC=st.tabs([f'Agent {x["code"]} · {x["name"]}' for x in agents])
    for tab,a in zip([tabA,tabB,tabC],agents):
        with tab:
            if not a['active']:
                st.info('Not activated: no recorded capability gap in this domain.')
            else:
                st.write('**Active criteria:** '+', '.join(a['criteria']))
                st.write('**Evidence:** '+a['evidence_state'])
                if a['missing']:st.warning(' · '.join(a['missing']))
                for r in a['interventions']:
                    with st.container(border=True):
                        st.write(f"**{r['name']}**  ·  {r['evidence_status']}")
                        st.caption(r['mechanism']+' | '+r['reference'])
    st.markdown('### Coordinator: combined findings')
    st.write('The coordinator matches validated capability gaps to source-linked solutions, flags missing evidence, and applies the same financial gates across domains.')
    st.dataframe(pd.DataFrame([{'Agent':r['code'],'Active':r['active'],'Criteria':', '.join(r['criteria']),'Candidate interventions':len(r['interventions'])} for r in agents]),use_container_width=True,hide_index=True)
    st.info('Default specialist logic is deterministic. It does not imply three autonomous AI models are running.')
    if str(secret_value('OPENAI_API_KEY','')):
        st.markdown('### Optional external model analysis')
        st.warning('Only use fictional or explicitly approved, sanitized data. This may send summary fields to an external API.')
        consent=st.checkbox('I authorize sending this SYNTHETIC supplier summary to the configured model API')
        if st.button('Run three bounded model specialists',disabled=not consent):
            try:
                from optional_ai import run_specialists
                with st.spinner('Generating bounded specialist drafts...'):
                    result=run_specialists(c,api_key=str(secret_value('OPENAI_API_KEY')),model=str(secret_value('OPENAI_MODEL','gpt-4.1-mini')))
                for r in result:st.markdown(f"**Agent {r['agent']}**");st.write(r['analysis'])
            except Exception as exc:st.error('Model call failed: '+str(exc)[:250])

elif page=='Official questionnaire':
    heading('Supplier Capability Survey','55 rated questions from the supplied Microsoft Forms PDF. Ratings 1–5 are supplier-reported until independently verified.')
    qs=E.SURVEY['ratedQuestions']; survey=c.setdefault('survey',{})
    sections=list(dict.fromkeys(q['section'] for q in qs))
    section=st.selectbox('Survey category',sections)
    rated=sum(1 for q in qs if isinstance(survey.get('Q'+str(q['id']),{}),dict) and survey.get('Q'+str(q['id']),{}).get('rating') in range(1,6))
    st.progress(rated/len(qs),text=f'{rated}/{len(qs)} questions rated · based on the supplied PDF')
    sub=[q for q in qs if q['section']==section]
    with st.form('questionnaire_form'):
        patch={}
        for q in sub:
            key='Q'+str(q['id'])
            old=survey.get(key,{}) if isinstance(survey.get(key),dict) else {}
            st.markdown(f"**Question {q['id']} — {q['text']}**")
            choices=['Not answered',1,2,3,4,5]
            original=old.get('rating'); default=choices.index(original) if original in choices else 0
            rating=st.selectbox('Supplier self-rating',choices,index=default,key=f'rating_{c["id"]}_{key}')
            ev=st.text_input('Evidence note / document reference',value=str(old.get('evidence','')),key=f'evidence_{c["id"]}_{key}')
            patch[key]={'rating':rating if rating!='Not answered' else None,'evidence':ev}
            st.caption('Provisional crosswalk: '+str(q.get('illustrativeCriterion','Not mapped'))+' · PDF page '+str(q.get('page','?')))
            st.divider()
        if st.form_submit_button('Save this survey section',type='primary'):
            update({'survey':patch})
    st.warning('The seven official survey categories and the project\'s 16 benchmark criteria are not equivalent. The crosswalk shown above is exploratory and must be validated by Siemens.')

elif page=='Benchmark research':
    heading('Benchmark knowledge & intervention library','Browse the team’s sector research and source-linked intervention candidates. Screening status is not deployment approval.')
    tab1,tab2=st.tabs(['Intervention candidates','Research document search'])
    with tab1:
        d=[]
        for r in E.INTERVENTIONS:d.append({'Case':r['name'],'Criteria':r['criteria'],'Mechanism':r['mechanism'],'Screening':r['evidence_status'],'Reference':r['reference']})
        st.dataframe(pd.DataFrame(d),use_container_width=True,hide_index=True)
        for r in E.INTERVENTIONS:
            with st.expander(f"{r['name']} · {r['evidence_status']}"):
                st.write(r['mechanism']);st.caption('Limitations: '+r['boundary']);st.caption('Reference: '+r['reference'])
    with tab2:
        sectors=sorted(set(r['sector'] for r in E.RESEARCH))
        a,b=st.columns([3,1]);q=a.text_input('Search within research paragraphs',placeholder='capacity certification, bottleneck, supplier investment')
        sector=b.selectbox('Sector',['All']+sectors)
        if q.strip():
            results=E.search_research(q,domain=None if sector=='All' else sector,limit=20)
            if not results:st.warning('No matching research paragraphs.')
            for r in results:
                with st.container(border=True):
                    st.write(f"**{r['title']}** · {r['section']}")
                    st.write(r['quote']);st.caption('Sector: '+r['sector']+' · source location '+str(r.get('index','?')))
                    if r.get('url'):st.link_button('Source document',r['url'])

elif page=='Snowflake data':
    heading('Snowflake integration · demo','Explore four synthetic supplier data sources and the proposed read-only connector contract. No live Siemens connection is included.')
    st.caption('Logical source views: risk management, performance, evaluation and supplier relationship management')
    data=E.snowflake_case(c['id'])
    if data:
        src=data['record']
        st.success(f"Synthetic Snowflake-like record found: {src['supplier_name']} ({src['supplier_id']})")
        r1,r2=st.columns(2)
        with r1:
            st.write('**Supplier risk**');st.json(src['risk'])
            st.write('**Supplier evaluation**');st.json(src['evaluation'])
        with r2:
            st.write('**Supplier performance**');st.json(src['performance'])
            st.write('**Supplier relationship management**');st.json(src['relationship_mgmt'])
        if st.button('Attach synthetic data to supplier case',type='primary'):
            E.attach_synthetic_snapshot(c)
            st.rerun()
        if c.get('data_snapshot'):st.success('Mock snapshot attached. Diagnosis and intervention approvals reopened for assessor validation.')
    else:st.info('No matching mock record for this case ID.')
    with st.expander('How Siemens could connect real Snowflake data'):
        st.write('The package includes `connectors/snowflake_adapter.py` and `VIEW_CONTRACT.sql`. A read-only service account, approved schemas/views, network access and credentials are required. Use a secure backend or an approved Snowflake connection rather than embedding credentials in the browser.')
        st.code('SCP_V_SUPPLIER_RISK\nSCP_V_SUPPLIER_PERFORMANCE\nSCP_V_SUPPLIER_EVALUATION\nSCP_V_SUPPLIER_RELATIONSHIP',language='text')
    st.warning('Mock data is illustrative and must never be mistaken for an assessment verified by Siemens.')

elif page=='Ask the copilot':
    heading('Ask the copilot','Ask about gaps, benchmark interventions, investment feasibility, or the next stage. Default answers use traceable local rules.')
    suggestions=['Which interventions fit this supplier?','What blocks the next stage?','Is the business case positive?','Why would a new supplier invest before award?']
    for row in [suggestions[:2],suggestions[2:]]:
        a,b=st.columns(2)
        for col,question in zip([a,b],row):
            if col.button(question,key='prompt_'+hashlib.md5((c['id']+question).encode()).hexdigest()[:10],use_container_width=True):
                st.session_state['pending_prompt']=question
    conversation=st.session_state.conversation.setdefault(c['id'],[])
    for m in conversation:
        with st.chat_message(m['role']):st.write(m['content'])
    prompt=st.chat_input('Ask a question about this supplier...')
    if st.session_state.get('pending_prompt'):prompt=st.session_state.pop('pending_prompt')
    if prompt:
        result=E.bounded_copilot(c,prompt)
        conversation.extend([{'role':'user','content':prompt},{'role':'assistant','content':result['answer']}])
        st.rerun()
    st.caption('Guided copilot mode is rule-based and does not browse the web or invent approvals. Research citations are included in the intervention studio.')

elif page=='Export / import':
    heading('Export & import supplier cases','Streamlit Community Cloud sessions are temporary. Export your work to JSON and re-import it to continue later.')
    st.download_button('Download selected case JSON',data=json.dumps(c,indent=2,ensure_ascii=False),file_name=f'{c["id"]}_demo_case.json',mime='application/json',type='primary')
    full={'cases':list(st.session_state.cases.values()),'synthetic':True,'note':'Student demo; no real Siemens supplier records'}
    st.download_button('Download all session cases',data=json.dumps(full,indent=2,ensure_ascii=False),file_name='all_supplier_demo_cases.json',mime='application/json')
    uploaded=st.file_uploader('Import a previously exported case JSON',type=['json'])
    if uploaded and st.button('Import JSON into this session'):
        try:
            obj=json.loads(uploaded.getvalue().decode('utf-8'))
            if isinstance(obj,dict) and 'cases' in obj:raise ValueError('Import one case at a time (not the all-cases export).')
            incoming=E.clean_imported_case(obj)
            st.session_state.cases[incoming['id']]=incoming
            st.session_state.selected_case=incoming['id']
            st.success('Imported. Diagnosis, evidence and approvals must be revalidated.')
            st.rerun()
        except (ValueError,UnicodeDecodeError,TypeError) as exc:st.error('Import rejected: '+str(exc))
    st.markdown('### Important deployment limitations')
    st.warning('This demo uses in-session storage and synthetic inputs. A production deployment needs durable authenticated data storage, review audit logs, role-based access, approved vendor contracts, and validated scoring / feasibility policies.')

st.divider()
st.caption('Independent Ross student prototype · synthetic figures and cases · 16 criteria / three domains · official survey crosswalk provisional · not an official Siemens Energy system')
