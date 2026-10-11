#!/usr/bin/env python3
"""Read-only validation of the final conditional handover, not new science."""
import hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=Path(os.environ['LIO_GINS_RUN_DIR'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
required=['README.md','docs/DELIVERY.md','docs/COMPLETION_AUDIT.md','docs/COMPLETION_AUDIT.json','docs/RESUME.md','docs/AUTHOR_BRIEF_ZH.md','docs/DEFENSE_QA_ZH.md','docs/CLAIMS_SUPPORTED.md','docs/USER_ACTION_REQUIRED.md','docs/reports/P5_frozen_heldout.md','docs/reports/P4/late_control_decision.md','paper/working/claim_evidence_map.json','paper/versions/internal_results_r01/method_draft.md','paper/versions/internal_results_r01/experimental_setup_draft.md','paper/versions/internal_results_r01/results_limitations_note.md']
checks={'required_files_nonempty':all((ROOT/p).is_file() and (ROOT/p).stat().st_size for p in required)}
freeze=ROOT/'freezes/LIO_GINS_R1_20261011T154403129394Z';f=json.loads((freeze/'scientific_freeze.json').read_text())
checks['scientific_freeze_unchanged']=sha(freeze/'scientific_freeze.json')==(freeze/'scientific_freeze.sha256').read_text().strip() and all(sha(ROOT/p)==h for group in ['source_SHA','config_SHA'] for p,h in f[group].items())
for r in ['20261011T163106760681Z_P7_804d7747','20261011T163820527256Z_P7_a26caac5']:
    checks[r+'_restore_exact']=json.loads((ROOT/'outputs'/r/'archive_recovery.json').read_text())['all_outputs_exact']
tests=ROOT/'outputs/20261011T164802218803Z_P7_07de00da';checks['64_required_tests_passed']=json.loads((tests/'manifest.json').read_text())['exit_code']==0 and bool(re.search(r'Ran 64 tests.*?\nOK', (tests/'stderr.log').read_text(),re.S))
integrity=ROOT/'outputs/20261011T164941656901Z_P7_24971931';checks['all_prior_sealed_evidence_passed']=json.loads((integrity/'manifest.json').read_text())['exit_code']==0 and json.loads((integrity/'stdout.log').read_text())['failures']==[]
checks['80_raw_metric_pairs_passed']=json.loads((ROOT/'outputs/20261011T164106339470Z_P7_269b03f9/final_metric_audit.json').read_text())['all_passed']
fig=ROOT/'artifacts/final_figures';identity=json.loads((fig/'figure_identity.json').read_text());checks['figures_and_points_SHA_bound']=all(sha(fig/name)==digest for name,digest in identity['output_SHA256'].items())
checks['ten_author_questions']=len(re.findall(r'^\d+\. ',(ROOT/'docs/DEFENSE_QA_ZH.md').read_text(),re.M))==10
claim=json.loads((ROOT/'paper/working/claim_evidence_map.json').read_text());checks['bounded_negative_claims']=claim['classification']=='NO_ADDITIONAL_GAIN' and claim['submission_manuscript'] is False and claim['support']['new_motion_increment_over_reasonable_long_wait_control'] is False and claim['late_registered_after_first_test_access'] is True
checks['80_per_cell_claim_bindings']=sum(map(len,claim['frozen_heldout_80_pair_bindings'].values()))==80
checks['no_project_remote']=subprocess.check_output(['git','remote'],cwd=ROOT,text=True).strip()==''
# Shell syntax validates documented argv construction, not fresh-machine replay.
blocks=(ROOT/'README.md').read_text().split('```bash\n')[1:];syntax=out/'documented_commands.sh';syntax.write_text('\n'.join(b.split('```')[0] for b in blocks));r=subprocess.run(['bash','-n',str(syntax)],capture_output=True,text=True);checks['README_command_syntax']=r.returncode==0
resume=json.loads((ROOT/'artifacts/delivery_checks/resume_pre_checkpoint.json').read_text());checks['resume_no_active_experiment_exit0']=resume['exit_code']==0
result={'checks':checks,'all_passed':all(checks.values()),'document_SHA':{p:sha(ROOT/p) for p in required},'integrity_run':str(integrity),'tests_run':str(tests),'scope':'authorized bounded goal and conditional internal-draft handover; positive science, fresh-machine rebuild, authorship and submission are not claimed'}
(out/'delivery_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'all_passed':result['all_passed'],'checks':checks}))
if not result['all_passed']:raise SystemExit(2)
