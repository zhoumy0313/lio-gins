"""Seal the available seen-data analysis; missing new raw data cannot authorize testing."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR']);rid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');dest=ROOT/'freezes/r2'/('analysis_'+rid);dest.mkdir(parents=True,exist_ok=False)
sources=[*list((ROOT/'src').rglob('*.py')),*[ROOT/'experiments/r2'/name for name in ['run_seen_candidate.py','run_seen_baseline.py','reanalyse.py','reacquisition_metrics.py','independent_check.py','make_figures.py','collect_index.py','complete_clocks.py','strict_nis_controls.py','test_reacquisition_metrics.py']]]
protocol=ROOT/'configs/r2/protocol_v1.yaml';configs=json.loads((ROOT/'configs/final_evaluation_methods.json').read_text())
for duration in [2,5,10,15,30,60,90]:
    conf=json.loads(json.dumps(configs['P_time_only']));conf['motion']['good_duration_s']=duration;configs['Clock'+str(duration)]=conf
for i in range(3):configs['NIS'+str(i)]=json.loads((ROOT/'outputs/20261011T141054205503Z_P3_e03a0b15/configs'/('B4_C'+str(i)+'.json')).read_text())
sources+=[protocol,ROOT/'configs/sources.lock.json',ROOT/'containers/base_image.lock.json',ROOT/'containers/derived_rootfs.local.json',ROOT/'configs/initialization_protocol.json',ROOT/'configs/development_experiment_protocol.json']
checks={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
for p in sources:
    target=dest/'snapshots'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
(dest/'all_method_configs.json').write_text(json.dumps(configs,indent=2)+'\n');audit=json.loads((ROOT/'artifacts/r2/S0/inheritance_audit.json').read_text());new=json.loads((ROOT/'artifacts/r2/S4/new_data_audit.json').read_text())
freeze={'freeze_id':dest.name,'type':'ANALYSIS_FREEZE_ONLY','UTC':rid,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_config_SHA':checks,'method_configs_SHA':hashlib.sha256((dest/'all_method_configs.json').read_bytes()).hexdigest(),'raw_seen_SHA':audit['raw_files'],'cache_seen_SHA':audit['caches'],'new_data_audit':new,'scientific_question':'fixed clean30s and biased10m90s re-entry with full fixed clocks and actual-update censoring','new_heldout_opening_authorized':False,'new_heldout_freeze_complete':False,'reason':'building01 raw inputs unavailable; unknown identities cannot be frozen or replaced by seen parking','random_seed':None,'method_revision_used':0,'protected_R1_base':'c12a42a3484458e1737e63201792e1122fc99c0d','protocol_SHA':checks[str(protocol.relative_to(ROOT))]}
(dest/'analysis_freeze.json').write_text(json.dumps(freeze,indent=2)+'\n');digest=hashlib.sha256((dest/'analysis_freeze.json').read_bytes()).hexdigest();(dest/'analysis_freeze.sha256').write_text(digest+'  analysis_freeze.json\n');(OUT/'freeze_receipt.json').write_text(json.dumps({'directory':str(dest),'SHA':digest,'new_heldout_opening_authorized':False},indent=2)+'\n');print(json.dumps({'directory':str(dest),'SHA':digest,'type':freeze['type']}))
