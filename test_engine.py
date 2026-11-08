import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import engine as E

class BusinessCaseTests(unittest.TestCase):
    def setUp(self):
        self.ex=copy.deepcopy(E.CASES[0]);self.new=copy.deepcopy(E.CASES[1])
    def test_expected_value(self):
        r=E.calc(self.ex)
        self.assertAlmostEqual(r['probability'],.6,places=5)
        self.assertAlmostEqual(r['net'],5_200_000,delta=1)
        self.assertAlmostEqual(r['supplier_balance'],800_000,delta=1)
    def test_four_gates(self):
        self.assertEqual(len(E.calc(self.ex)['gates']),4)
        self.assertFalse(E.calc(self.new)['human_go'])
        self.assertTrue(E.calc(self.new)['blockers'])
    def test_interventions_are_source_linked(self):
        picks=E.recommendations(self.ex)
        self.assertTrue(picks)
        self.assertTrue(all(x.get('reference') and x.get('matched') for x in picks))
    def test_agent_isolation(self):
        agents=E.specialist_analysis(self.ex)
        self.assertEqual(len(agents),3)
        self.assertTrue(all(x['code'] in ['A','B','C'] for x in agents))
        for a in agents:
            self.assertTrue(all(x.startswith(a['code']) for x in a['criteria']))
    def test_finance_edit_cancels_approval_and_stage(self):
        self.assertTrue(E.calc(self.ex)['human_go'])
        E.revise_case(self.ex,{'finance':{'gain':100_000}})
        self.assertEqual(self.ex['finance']['sponsor_review'],'Pending')
        self.assertLessEqual(self.ex['completed_stage'],3)
        self.assertFalse(E.calc(self.ex)['human_go'])
    def test_input_edit_reopens_diagnosis(self):
        E.revise_case(self.ex,{'evidence':'New synthetic measurement'})
        self.assertFalse(self.ex['diagnosis_approved'])
        self.assertFalse(self.ex['evidence_verified'])
        self.assertLessEqual(self.ex['completed_stage'],1)
    def test_snapshot_reopens_diagnosis(self):
        rec=E.attach_synthetic_snapshot(self.ex)
        self.assertEqual(rec['record']['supplier_name'],self.ex['name'])
        self.assertFalse(self.ex['diagnosis_approved'])
        self.assertEqual(self.ex['finance']['sponsor_review'],'Pending')
    def test_stages(self):
        self.assertEqual(len(E.STAGES),8)
        self.assertTrue(E.stage_check(self.ex,8)[0])
        for i in range(1,9): self.assertTrue(E.stage_check(self.ex,i)[0],i)
    def test_survey_55(self):
        self.assertEqual(len(E.SURVEY['ratedQuestions']),55)
        self.assertEqual(E.SURVEY['ratedQuestions'][0]['id'],7)
        self.assertEqual(E.SURVEY['ratedQuestions'][-1]['id'],61)
    def test_import_resets_approvals(self):
        imported=E.clean_imported_case(self.ex)
        self.assertFalse(imported['diagnosis_approved'])
        self.assertEqual(imported['finance']['sponsor_review'],'Pending')
        self.assertEqual(imported['completed_stage'],0)
    def test_local_guidance(self):
        answer=E.bounded_copilot(self.new,'Why would the supplier invest before award?')
        self.assertIn('willingness',answer['answer'].lower())
    def test_do_not_skip_stages(self):
        self.new['completed_stage']=1
        with self.assertRaises(ValueError): E.complete_stage_local(self.new,3)

if __name__=='__main__':unittest.main()
