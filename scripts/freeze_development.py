#!/usr/bin/env python3
"""Archive scientific identity only after real gain, attribution and access-parity proof."""
import argparse,datetime,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.adapters.research_access import sha
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('verification_run');p.add_argument('transition_run');p.add_argument('tests_run');p.add_argument('scope_review');a=p.parse_args()
proof=Path(a.verification_run).resolve()/'final_verification.json';transition=Path(a.transition_run).resolve()/'transition_parity.json';tests=Path(a.tests_run).resolve();scope_path=Path(a.scope_review).resolve()
for folder in [proof.parent,transition.parent,tests]:
    if json.loads((folder/'manifest.json').read_text())['status']!='PASSED':raise ValueError('required review run failed')
v=json.loads(proof.read_text());t=json.loads(transition.read_text());scope=json.loads(scope_path.read_text())
if not v['quantitative_development_gate'] or not t['all_trajectories_exact'] or not t['unchanged_mechanism_sources'] or not scope['small_application_system_scope_accepted']:
    raise ValueError('gain, attribution, fixed identity or scope review does not support freeze')
for name,expected in t['source_SHA'].items():
    if sha(ROOT/name)!=expected:raise ValueError('scientific source changed since transition verification: '+name)
if (ROOT/'docs/TEST_OPENED.json').exists():raise ValueError('heldout already opened: no new scientific freeze')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');freeze_id='LIO_GINS_R1_'+stamp;folder=ROOT/'freezes'/freeze_id;folder.mkdir(parents=True,exist_ok=False)
sources=[]
for package in ['adapters','fusion','observation_manager','evaluation']:sources+=list((ROOT/'src'/package).glob('*.py'))
sources += [ROOT/'scripts'/n for n in ['record_run.py','run_candidate.py','run_outer_baseline.py','run_lio.py','build_lio_cache.py','run_kf_robot.py','evaluate_kf_robot.py','evaluate_outer.py','export_initial_condition.py','prepare_development_stress.py','run_heldout.py']]
sources += [ROOT/'containers'/n for n in ['run_inside.sh','shutdown_clock.py']]
configs=[ROOT/n for n in ['configs/initialization_protocol.json','configs/development_experiment_protocol.json','configs/heldout_protocol.json','configs/final_evaluation_methods.json','configs/KF_noise_sensitivity.json','configs/sources.lock.json','containers/base_image.lock.json','containers/derived_rootfs.local.json']]
for path in sources+configs:
    if not path.is_file():raise ValueError('missing scientific source '+str(path))
data=json.loads((ROOT/'data/manifests/DATA_MANIFEST.json').read_text());methods=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text())
record={'freeze_id':freeze_id,'created_UTC':stamp,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'development_conditions_passed':True,'heldout_sequence':'parking00','development_proof':str(proof),'development_proof_SHA':sha(proof),
    'transition_parity_proof':str(transition),'transition_parity_SHA':sha(transition),'tests_run':str(tests),'scope_review':scope,'scope_review_SHA':sha(scope_path),
    'source_SHA':{str(n.relative_to(ROOT)):sha(n) for n in sources},'config_SHA':{str(n.relative_to(ROOT)):sha(n) for n in configs},
    'allowed_method_configs':list(methods.values()),'raw_inputs':{f['path']:{'sha256':f['sha256'],'size_bytes':f['size_bytes']} for f in data['files'] if f['status']=='PRESENT'},
    'data_manifest_SHA':sha(ROOT/'data/manifests/DATA_MANIFEST.json'),'test_performance_opened':False,
    'novelty_supported':False,'novelty_status':'bounded_application_system_contribution_only','no_retuning_after_open':True}
path=folder/'scientific_freeze.json';path.write_text(json.dumps(record,indent=2)+'\n');(folder/'scientific_freeze.sha256').write_text(sha(path)+'\n')
snapshot=folder/'snapshots';snapshot.mkdir()
for n in sources+configs:
    dest=snapshot/n.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(n.read_bytes())
out=Path(os.environ['LIO_GINS_RUN_DIR']);(out/'freeze_receipt.json').write_text(json.dumps({'freeze_directory':str(folder),'freeze_id':freeze_id,'freeze_SHA':sha(path),'test_performance_opened':False},indent=2)+'\n');print(json.dumps({'freeze_directory':str(folder),'freeze_id':freeze_id,'heldout_opened':False}))
