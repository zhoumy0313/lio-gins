#!/usr/bin/env python3
"""Offline revision diagnostic; actual update admissions and natural cost only."""
import argparse,hashlib,json,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('candidate_screen');p.add_argument('baseline_screen');a=p.parse_args();out=Path(os.environ['LIO_GINS_RUN_DIR']);source=Path(a.candidate_screen).resolve();baseline=Path(a.baseline_screen).resolve();c=json.loads((source/'candidate_screen.json').read_text());b=json.loads((baseline/'selected_baselines.json').read_text());records=[];sources=[source/'candidate_screen.json',baseline/'selected_baselines.json']
for r in c['complete_selected']:
    log=Path(r['backend']['output'])/'per_update.jsonl';u=[json.loads(v) for v in log.read_text().splitlines()];sources.append(log)
    record={'case':r['case'],'candidate':r['name'],'backend':r['backend']['output'],'evaluation':r['evaluation'],'metrics':r['metrics']['metrics'],'rejections':sum(not v['accepted'] for v in u),'receiver_rows':len(u),'health_unavailable_times':[v['measurement_sow'] for v in u if v.get('local_health_verified') is False],'motion_scores_missing':sum(v.get('motion_score') is None for v in u),'events':[]}
    for e in r['metrics']['events']:
        event=e['event'];case=event['fault_parameters'];t0=event['recovery_start_sow'];hold=case.get('bias_hold_s',0);active=[v for v in u if t0<=v['measurement_sow']<t0+hold]
        record['events'].append({'event':event,'metrics':e['metrics'],'artificial_persistent_bias_rows':len(active),'bias_rows_admitted':sum(v['accepted'] for v in active),'final_state_in_bias_interval':active[-1]['state'] if active else None})
    records.append(record)
first=next((r for r in c['complete_selected'] if r['case']=='natural'),None)
if first:
    base=next(r for r in b['complete_selected']['B6'] if r['case']=='natural');bl=Path(base['backend']['output'])/'per_update.jsonl';pl=Path(first['backend']['output'])/'per_update.jsonl';x=[json.loads(v) for v in bl.read_text().splitlines()];y=[json.loads(v) for v in pl.read_text().splitlines()];sources.append(bl);difference=None
    for i,(v,w) in enumerate(zip(x,y)):
        if v['original_gnss_id']!=w['original_gnss_id']:raise ValueError('natural update pairing failed')
        if v['accepted']!=w['accepted'] or abs(v['correction_norm_m']-w['correction_norm_m'])>1e-9:
            difference={'index':i,'baseline':v,'candidate':w,'preceding_candidate_updates':y[max(0,i-2):i]};break
else:difference=None
result={'revision':c['revision'],'gate':c['development_gate_on_primary_cache'],'selected_is_eligible':c['selected_is_eligible'],'selected':c['selected'],'shared_normal_cap_m':c['shared_natural_cap_m'],'first_natural_difference_from_B6':difference,'all_case_diagnostics':records,'interpretation_limits':'offline fault labels used only for admission counts; natural rejections are not automatically known false GNSS rejections','input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
(out/'revision_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'revision':c['revision'],'eligible':c['selected_is_eligible'],'gate':c['development_gate_on_primary_cache'],'natural_first_different_sow':difference['candidate']['measurement_sow'] if difference else None}))
