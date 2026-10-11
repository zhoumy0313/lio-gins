#!/usr/bin/env python3
"""Describe supplemental timing counterevidence; do not replace the primary metric."""
import argparse,json,os
from pathlib import Path
from replay_experiment_batch import digest
p=argparse.ArgumentParser();p.add_argument('long_wait_run');p.add_argument('verification_run');a=p.parse_args();out=Path(os.environ['LIO_GINS_RUN_DIR']);ap=Path(a.long_wait_run)/'long_wait_audit.json';vp=Path(a.verification_run)/'final_verification.json';audit=json.loads(ap.read_text());verification=json.loads(vp.read_text());comparisons=[];sources={str(ap.resolve()):digest(ap),str(vp.resolve()):digest(vp)}
for label,cache in [('primary','20261011T141044340351Z_P2_9dd3f300'),('sensitivity','20261011T134125698776Z_P2_0de7714e')]:
    candidate=next(r for r in verification['tables'][label] if r['name']=='P');eligible=[r for r in audit['table'] if Path(r['cache']).name==cache and r['eligible']];best=min(eligible,key=lambda r:r['primary_macro_RMSE_m'])
    detail={'cache':cache,'candidate':candidate,'best_supplemental_fixed_time_control':best,'candidate_minus_time_control_m':candidate['primary_macro_RMSE_m']-best['primary_macro_RMSE_m'],'normal_recovery_admission_delays':[]}
    groups=[('P',verification['records'][label]['P'])]+[('clock_'+str(d),audit['records'][cache+'_clock_qualification_'+str(d)]) for d in [15,30,60,90]]
    for name,records in groups:
        r=next(r for r in records if r['case']=='loss30_normal');path=Path(r['backend']['output'])/'per_update.jsonl';sources[str(path)]=digest(path);updates=[json.loads(x) for x in path.read_text().splitlines()]
        for i,e in enumerate(r['metrics']['events']):
            t=e['event']['recovery_start_sow'];valid=[u for u in updates if t<=u['measurement_sow']<=t+120 and u['accepted']];detail['normal_recovery_admission_delays'].append({'method':name,'event':i,'first_raw_recovery_observation_admitted_after_s':valid[0]['measurement_sow']-t if valid else None,'position_error_recovery_time_s':e['metrics']['recovery_time_s']})
    comparisons.append(detail)
result={'comparisons':comparisons,'new_motion_mechanism_primary_gain_over_reasonable_long_wait_controls_supported':all(c['candidate_minus_time_control_m']<-.1 for c in comparisons),'registered_short_control_gains_remain_real':True,'supplemental_controls_were_development_only_after_first_test_access':True,'no_new_heldout_results':True,'no_candidate_or_metric_changes':True,'conclusion':'longer fixed-clock qualification beats proposed primary error at matched natural cost on both development caches; original short-control ablation does not establish a sufficiently strong motion-specific increment. Admission delay is a separate tradeoff, not a replacement success criterion; raw unperturbed recovery observations are not assumed correct. Stop method search at r03; retain frozen test and drafts, no submission manuscript.', 'input_SHA256':sources}
(out/'late_control_interpretation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
