"""Optional genuine model calls, never authoritative for calculation or approvals.

Only use with synthetic/approved sanitized supplier data on an authorized endpoint.
"""
import json
import engine as E


def run_specialists(case,api_key,model='gpt-4.1-mini'):
    from openai import OpenAI
    client=OpenAI(api_key=api_key,timeout=22.0,max_retries=1)
    results=[]
    for agent in E.specialist_analysis(case):
        if not agent['active']:
            results.append({'agent':agent['code'],'analysis':'Not activated: no identified gap in this domain.'})
            continue
        allowed=[{'id':r['id'],'name':r['name'],'mechanism':r['mechanism'],
                'reference':r['reference'],'evidence_status':r['evidence_status'],'boundary':r['boundary']}
                for r in agent['interventions']]
        context={'case_type':case.get('type'),'gap_description':case.get('gap'),
                 'criteria':agent['criteria'],'assessment_evidence':case.get('evidence','')[:1500],
                 'evidence_verified':case.get('evidence_verified'),'diagnosis_approved':case.get('diagnosis_approved'),
                 'allowed_interventions':allowed}
        instruction=(f"You are Agent {agent['code']} for {agent['name']}, one specialist in a student Siemens Energy prototype. "
            'Only use the supplied synthetic scenario and allowlisted benchmark intervention records. '
            'Do not invent supplier evidence, numerical predictions, company policies or commercial terms. '
            'Distinguish observed evidence, assumptions and missing information. '
            'Reply in no more than 190 words covering: domain gap, missing evidence, up to two allowed intervention IDs '
            '(with source references and fit limitations), implementation uncertainties. '
            'Do not approve suppliers, Stage 3 or Stage 4. If gap is unverified state clearly.')
        response=client.responses.create(model=model,input=[{'role':'system','content':instruction},
            {'role':'user','content':json.dumps(context,ensure_ascii=False)}],max_output_tokens=450)
        text=response.output_text.strip() if getattr(response,'output_text',None) else 'No text returned'
        results.append({'agent':agent['code'],'analysis':text})
    return results
