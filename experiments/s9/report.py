"""Complete descriptive report, with all signs and immutable provenance."""
import datetime,gzip,hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=json.loads((ROOT/'docs/research_s9/STATE.json').read_text());registry=json.loads((ROOT/'artifacts/s9/COLLECTIVE_FREEZE.json').read_text());aggregate=Path(state['aggregate_run']);j=json.loads((aggregate/'cross_route_judgment.json').read_text())
lines=['# S9 complete multiscenario experiment report','',
'All nineteen unchanged policies, seven GNSS faults plus natural, every registered route and fixed event are retained. No new-route tuning, favorable route/event subset or successful-only intersection. building01 was prospective in S8 and already known before S9; prior conclusions are unchanged.',
'','## Pre-precision data and protocol',
'Five originals per new route matched registered identity; official bag hashes independently matched. playground00 GPS week2363; street00/building02 week2364, measured GPS−UTC18s. Existing AT128/ADIS/F9P isolated pipeline reused. Stable first reference row per timestamp and single earliest common sensor/cache-covered initial state were declared before precision; reference state used only for common controlled initialization and offline evaluation. Whole expected grid is fixed reference/ADIS/primary-cache overlap; no internal gaps are removed.',
'','## Every route and every policy','']
mapping=[];route_briefs=[]
for route in state['included_routes']:
    s=state['routes'][route];a=Path(s['analysis_run']);rows=json.loads((a/'summary_table.json').read_text());events=json.loads((a/'event_results.json').read_text());r=next(x for x in j['route_reports'] if x['route']==route);support=json.loads((ROOT/'artifacts/s9'/route/'final_common_support.json').read_text());receipt=json.loads((ROOT/'docs/research_s9'/route/'FREEZE_PUSH_RECEIPT.json').read_text());check=json.loads((Path(s['independent_check_run'])/'independent_check.json').read_text())
    lines += ['### '+route,'',f"Common SOW {support['common_sow']}; expected grid {support['whole_grid_expected_samples']} ticks. Selected original reference row {support['single_state_original_row']}; exactly one state used. ADIS minus common tail {support['ADIS_end_minus_common_end_s']:.9f}s. Freeze {receipt['local_commit']} exact remote readback {receipt['UTC']} precedes first precision. Independent checks {check['independent_error_values_checked']} errors/{check['accepted_clocks_checked']} clocks and exposure, max difference {check['max_absolute_error_difference_m']:.17g}m; passed={check['passed']}.",'',
    '|Policy|Natural m|Cap m|Clean max s|Clean90 m|Bias90 m|Bias180 m|Injected accepted/exposed|Q|',
    '|---|---:|---:|---:|---:|---:|---:|---:|---|']
    for row in rows:
        def f(key):return 'C180/missing' if row[key] is None else f'{row[key]:.6f}'
        lines.append('|'+row['method']+'|'+'|'.join(f(k) for k in ['natural_RMSE_m','natural_cap_m','clean_latency_max_s','clean_RMSE_90_m','bias_RMSE_90_m','bias_RMSE_180_m'])+f"|{row['bias_accepted_rows']}/{row['bias_exposed_rows']}|{row['service_qualified']}|")
    p=r['P'];best=r['strongest_eligible_control'];lines+=['',f"P joint qualified={p['service_qualified']}; automatic directional reduction against strongest qualified control={r['joint_directional_error_reduction']}. Strongest qualified control: {best['method'] if best else 'none; empty pool is not gain evidence'}. Automatic directional comparison is not novelty or a significance test.",'',
    '|Control|P minus control bias90 m|P minus control natural m|All event bias90 differences m|Improved/worse events|',
    '|---|---:|---:|---|---:|']
    for c in [x for x in j['pairwise_comparisons'] if x['route']==route]:
        lines.append(f"|{c['control']}|{c['P_minus_control_bias90_m']}|{c['P_minus_control_natural_m']}|{c['event_delta_bias90_m']}|{c['improved_events']}/{c['worse_events']}|")
    lines+=['','All primary P/Clock2/no-anchor/NIS/Huber/long-wait events (all19 and every other category remain in full event JSON):','',
    '|Policy|Event|Bias90 m|Bias180 m|Actual biased admit s|Availability bound s|Injected accepted/exposed|',
    '|---|---:|---:|---:|---:|---:|---:|']
    for row in [x for x in events if x['case']=='loss30_bias10' and x['method'] in ['P','Clock2','P_without_anchor','NIS0','NIS1','NIS2','B5','Clock60','Clock90','P_without_decay']]:
        for e in row['events']:
            lines.append(f"|{row['method']}|{e['event_index']}|{e['post_return']['90']['horizontal_RMSE_m']}|{e['post_return']['180']['horizontal_RMSE_m']}|{e['T_admit_s']}|{e['T_available_bound_s']}|{e['injected_rows_accepted']}/{e['injected_rows_exposed']}|")
    cancellation=json.loads((ROOT/'artifacts/s9'/route/'C/injection_cancellation.json').read_text());lines+=['',f"Injection cancels raw receiver error in {sum(e['injection_reduces_actual_receiver_horizontal_error_rows'] for e in cancellation['events'])}/{sum(e['rows'] for e in cancellation['events'])} primary rows. Artificial exposure is not actual fault probability. Cache/measurement clocks are not field wall latency."]
    # Retain all actual fallback events, never assume clock duration means quarantine.
    fallback=[]
    for row in events:
        if row['case']!='loss30_bias10' or row['method'] not in ['P','Clock2','Clock60','Clock90']:continue
        updates=[json.loads(l) for l in (Path(row['backend'])/'per_update.jsonl').read_text().splitlines()]
        for e in row['events']:
            first=next((u for u in updates if u['original_gnss_id']==e['first_gnss_id']),None)
            if first and 'fallback' in json.dumps(first):fallback.append({'method':row['method'],'event':e['event_index'],'admission_s':e['T_admit_s'],'first_update':first})
    (OUT/(route+'_fallback_events.json')).write_text(json.dumps(fallback,indent=2)+'\n');lines+=['',f"Actual biased first-update fallback records: {len(fallback)}, retained in {route}_fallback_events.json. Clock duration is not unconditional quarantine."]
    native=ROOT/'artifacts/s9'/route/'C/native_KF_metrics.json'
    if native.exists():
        n=json.loads(native.read_text());lines+=['',f"Independent native KF-GINS fixed STD-scale2 transfer: horizontalRMSE={n['metrics_10Hz']['horizontal_rmse_m']}m, coverage={n['metrics_10Hz']['coverage']}. No new-route noise search; not best possible KF-GINS and not P-gain denominator, never posterior-injected."]
    for row in events:mapping.append({'route':route,'method':row['method'],'case':row['case'],**row['provenance']})
    clock=next(c for c in j['pairwise_comparisons'] if c['route']==route and c['control']=='Clock2');anchor=next(c for c in j['pairwise_comparisons'] if c['route']==route and c['control']=='P_without_anchor')
    route_briefs.append(f"{route}：P带偏90秒RMSE {p['bias_RMSE_90_m']:.6f}米；相对Clock2为{clock['P_minus_control_bias90_m']:+.6f}米，相对无锚为{anchor['P_minus_control_bias90_m']:+.6f}米（负值较好）。清洁接入{p['clean_latency_max_s']}秒，自然{p['natural_RMSE_m']:.6f}米/上限{p['natural_cap_m']:.6f}米；联合资格{p['service_qualified']}。全部逐事件差值和更强对照均保留。")
lines+=['','## Equal route weighting, counterevidence and limits','']
for c in j['new_route_equal_weight_macro']:lines.append(f"{c['control']}: equal-weight new-route mean P-minus-control bias90={c['equal_weight_route_macro_P_minus_control_bias90_m']}m; all signs={c['all_route_signs']}.")
lines+=['','S8 building01 remains a negative joint-gate result: P clean7s/bias90 2.378450m/natural5.273450m above5.055154 cap, despite B3/B4 bias90 4.029944m. The second biased event is worse;0/83/83 injected rows accepted. Clock90 and no-decay adverse contrasts remain. Seen parking00 NIS30 is faster and lower-error than P; building00 long waits and the unresolved3.6013m repeat discrepancy remain. R1 NO_ADDITIONAL_GAIN unchanged.',
'','One fixed artificial stress matrix per route does not establish field multipath detection, calibrated fault probability, population significance or universal superiority. Initial state is controlled, reference constructions differ (S9 GNSS/INS versus prior MM/INS), errors may correlate, and events within routes are not IID. Natural gates and all adverse signs remain explicit.',
'','## Commands, exits, traceability and remaining human actions','',
'Real per-route recorder argv/input/source SHA/time/exit/seal receipts are in artifacts/s9/<route>/run_receipts and locally retained outputs_s9. A engineering results and B exact freeze push receipts are preserved; C matrices152 pairs each, offline reanalyse, independent checker, all-control judgment and injection diagnostic all have their actual manifests. Native transfer failures, if any, are separate and cannot remove main-policy evidence. D six-page review source/PDF/tables/plots and numeric audits, E integrity audit and checkpoint receipts complete delivery. Never restart an opened route as unseen or tune against new results.',
'','Authors alone decide interpretation, attribution/funding, exact venue deadline/timezone/template/anonymity/AI policy and formal submission. No account/login/payment/copyright/formal submission performed. Raw/runtime/fullcache retained locally; Git is lightweight evidence backup only.']
(OUT/'EXPERIMENT_REPORT.md').write_text('\n'.join(lines)+'\n')
brief='# S9 作者简报\n\n固定三条新路线，全部19策略、自然与七类GNSS扰动、全部事件和五个后验窗口；源码、参数、数据和缓存身份冻结推送核验后才首次计算精度。\n\n'+'\n\n'.join(route_briefs)+'\n\n正负差值都是完整预设事件宏平均，不删路线/事件。与Clock2、无锚的数值改善，不自动等同于胜过所有合格强基线、满足自然代价或算法新颖性。R1/R2/S8反证保持不变，building01自然代价失败明确写入论文。\n\n完整六页英文审阅稿、TeX、矢量图表与数值映射在paper/submission_candidate/s9；全部方法/事件/误差窗在artifacts/s9和本地封存outputs_s9。逐事件退步、长等待更强或严格NIS更优均真实报告，不承诺普适优越或录用。\n\n作者需确认科学措辞、署名/单位/基金/权限、会方模板/匿名/AI规则/精确截止时区，批准稿件后自行处理账号与正式提交。当前保留NOT_SUBMISSION_READY，未署名、登录、付费或投稿。原数据与全量缓存未做异地备份。\n'
(OUT/'AUTHOR_BRIEF_ZH.md').write_text(brief)
evidence={'goal_id':state['goal_id'],'registration':registry,'cross_route_summary_source':str(aggregate/'cross_route_judgment.json'),'cross_route_summary_SHA':sha(aggregate/'cross_route_judgment.json'),'all_pair_provenance':mapping,'claims':{'fixed_parameters':{'supported':True,'source':'artifacts/s9/INHERITANCE_AUDIT.json'},'all_route_comparisons':j['route_reports'],'all_event_signs':j['pairwise_comparisons'],'universal_superiority':False,'algorithm_novelty':False,'field_fault_probability':False,'live_end_to_end_latency':False,'old_S8_negative_retained':True,'formal_submission_performed':False},'old_S8_paper_SHA':sha(ROOT/'paper/submission_candidate/s8/main.pdf')}
(OUT/'CLAIM_EVIDENCE_MAP.json').write_text(json.dumps(evidence,indent=2)+'\n');print(json.dumps({'pairs_mapped':len(mapping),'all_routes':state['included_routes'],'formal_submission_performed':False}))
