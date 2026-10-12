"""S8-based multiscenario author-review manuscript from complete real evidence."""
import hashlib,json,os,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ['LIO_GINS_RUN_DIR'])
version=Path(sys.argv[1]);version.mkdir(parents=True,exist_ok=False)
state=json.loads((ROOT/'docs/research_s9/STATE.json').read_text())
aggregate=Path(state['aggregate_run']);judgment=json.loads((aggregate/'cross_route_judgment.json').read_text())
old=(ROOT/'paper/submission_candidate/s8/main.tex').read_text()
bindings=[]
def number(route,method,field,precision=3):
    source=Path(state['routes'][route]['analysis_run'])/'summary_table.json'
    row=next(r for r in json.loads(source.read_text()) if r['method']==method)
    value=row[field];render='censored' if value is None else f'{value:.{precision}f}'
    bindings.append({'route':route,'method':method,'field':field,'raw_value':value,'rendered':render,'source':str(source),'SHA':hashlib.sha256(source.read_bytes()).hexdigest()})
    return render
qualified=[r['route'] for r in judgment['route_reports'] if r['P']['service_qualified']]
direction=[r['route'] for r in judgment['route_reports'] if r['joint_directional_error_reduction']]
descriptive=[]
for route in state['included_routes']:
    comparisons=[r for r in judgment['pairwise_comparisons'] if r['route']==route]
    clock=next(r for r in comparisons if r['control']=='Clock2')
    anchor=next(r for r in comparisons if r['control']=='P_without_anchor')
    descriptive.append(f"{route}: P versus Clock2 is {clock['numerical_direction']}, and P versus no-anchor is {anchor['numerical_direction']}")
abstract_result='; '.join(descriptive)+'.'
route_paragraphs=[];event_tex=[];event_bindings=[]
for route in state['included_routes']:
    p=next(r for r in judgment['route_reports'] if r['route']==route)
    best=p['strongest_eligible_control']
    best_text=(f"The strongest joint-qualified alternative is {best['method'].replace('_', '-')}, with {number(route,best['method'],'bias_RMSE_90_m')}-m biased error, {number(route,best['method'],'natural_RMSE_m')}-m natural error and {number(route,best['method'],'clean_latency_max_s',1)}-s clean delay." if best else 'No alternative meets every joint qualification; an empty eligible pool is not evidence of improvement.')
    route_paragraphs.append(route+r': P gives natural RMSE '+number(route,'P','natural_RMSE_m')+r' m against the '+number(route,'P','natural_cap_m')+r'-m cap, maximum clean delay '+number(route,'P','clean_latency_max_s',1)+r' s, and biased post90/post180 RMSE '+number(route,'P','bias_RMSE_90_m')+'/'+number(route,'P','bias_RMSE_180_m')+r' m. Clock2 gives '+number(route,'Clock2','bias_RMSE_90_m')+r' m, no-anchor '+number(route,'P_without_anchor','bias_RMSE_90_m')+r' m, NIS30 '+number(route,'NIS2','bias_RMSE_90_m')+r' m, Huber2.5 '+number(route,'B5','bias_RMSE_90_m')+r' m and Clock90 '+number(route,'Clock90','bias_RMSE_90_m')+r' m. '+('P passes' if p['P']['service_qualified'] else 'P fails')+r' the joint qualification. '+best_text)
    source=Path(state['routes'][route]['analysis_run'])/'event_results.json';events=json.loads(source.read_text())
    for i in range(3):
        vals=[]
        for method in ['P','Clock2','P_without_anchor']:
            e=next(r for r in events if r['method']==method and r['case']=='loss30_bias10')['events'][i]
            value=e['post_return']['90']['horizontal_RMSE_m'];render='missing' if value is None else f'{value:.3f}'
            vals.append(render)
            event_bindings.append({'route':route,'method':method,'case':'loss30_bias10','event':i,'field':'post_return.90.horizontal_RMSE_m','raw_value':value,'rendered':render,'source':str(source),'SHA':hashlib.sha256(source.read_bytes()).hexdigest()})
        pe=next(r for r in events if r['method']=='P' and r['case']=='loss30_bias10')['events'][i]
        delay='C180' if pe['T_admit_s'] is None else f"{pe['T_admit_s']:.0f}"
        for field,render in [('T_admit_s',delay),('injected_rows_accepted',str(pe['injected_rows_accepted'])+'/'+str(pe['injected_rows_exposed']))]:
            event_bindings.append({'route':route,'method':'P','case':'loss30_bias10','event':i,'field':field,'raw_value':pe[field],'rendered':render,'source':str(source),'SHA':hashlib.sha256(source.read_bytes()).hexdigest()})
        event_tex.append(route+f"/{['N','E','NE'][i]} & "+' & '.join(vals)+f" & {delay} & {pe['injected_rows_accepted']}/{pe['injected_rows_exposed']}"+r' \\')
event_table='\n'.join([r'\begin{table}[t]\centering\scriptsize',r'\caption{All three registered biased events on every S9 route. Horizontal post90 RMSE (m); P admission is its actual biased-return update delay, separate from clean delay. Exposure is P accepted/exposed injected rows. No favorable event subset.}\label{tab:events}',r'\begin{tabular}{lrrrrr}\toprule',r'Route/direction & P & Clock2 & No-anchor & P delay & Exposure\\\midrule',*event_tex,r'\bottomrule\end{tabular}\end{table}'])
header=old[:old.index(r'\begin{abstract}')]
header=header.replace('GNSS Re-entry with LiDAR--Inertial Odometry: A Prospective Study of Timeliness--Accuracy Tradeoffs','Historical Motion Anchors for GNSS Re-entry: A Prospective Multiscenario Study of Accuracy--Delay Tradeoffs')
related=old[old.index(r'\section{Related Work}'):old.index(r'\section{Data and Prospective Protocol}')]
text=header+r'''\begin{abstract}
Returning GNSS positions can remain biased after an outage. We evaluate a historical motion-anchor admission strategy in a common position filter propagated by FAST-LIO2, separating actual re-entry delay, position error and exposure to artificially displaced observations. All nineteen fixed policies include direct fusion, innovation gates, Huber weighting, seven qualification durations and ablations. Following development, retrospective assessment and a negative joint-gate result on building01, an unchanged multiscenario extension registered new routes and froze complete source, clocks, inputs and caches with verified remote commits before precision access. Every registered route receives natural data and seven fixed GNSS perturbations, without route-specific tuning. '''+abstract_result+r''' Clean recovery, natural cost, all fixed events and stronger simple controls constrain interpretation. The result supports a bounded empirical account of motion anchors and accuracy--delay tradeoffs, not universal superiority or algorithm novelty. Controlled injected-row acceptance and replay-clock bounds are not field fault probabilities or live end-to-end latency.
\end{abstract}
\begin{IEEEkeywords}GNSS recovery, historical anchor, LiDAR--inertial odometry, admission delay, prospective evaluation\end{IEEEkeywords}
\section{Introduction}
A robot may bridge a GNSS outage with LiDAR--inertial odometry (LIO), yet should not necessarily use the first returning receiver position. Persistent position bias can pass a relative-motion check because differences cancel a constant displacement. A historical admitted receiver observation propagated by local motion supplies another constraint, while a stale anchor can veto useful updates. Longer qualification can reduce the error of a finite injected bias by waiting for it to disappear, at a cost to clean re-entry.

The question is whether the inherited P-r03 anchor improves biased-return error relative to the same two-second qualification without an anchor, and relative to complete strong simple alternatives, under explicit clean-delay and natural-cost conditions. All parameters remain unchanged. We distinguish numerical improvement over Clock2 or a no-anchor ablation from satisfying the full service/cost gate, and report any disagreement.

This study adds prospectively registered street00 and playground00, with building02 included on technical availability before any new precision result. building00 and parking00 are seen evidence. building01 was prospective in S8, but its natural-cost failure was known before this extension; it is not relabeled unseen. The contribution is a complete, reproducible empirical comparison and its applicability limits. FAST-LIO2 and KF-GINS retain their attribution; no new full navigation filter or integrity guarantee is claimed.
'''+related+r'''
\section{Data and Prospectively Frozen Protocol}
\subsection{Route Roles and Common Inputs}
The i2Nav-Robot dataset~\cite{i2nav} supplies AT128 LiDAR, ADIS16465 angle/velocity increments and F9P single-point receiver positions. Upstream versions and the existing isolated Noetic frontend remain fixed. All five originals per new route are read-only; each bag matches its official SHA-256. Text digests are local identities. Extras and failed engineering attempts are retained. street00/playground00 are the priority new scenes; building02 is included before opening precision because its actual originals and complete cache passed technical checks, despite a retained download-sidecar file.

Standard/custom IMU, F9P text and ROS headers establish each clock independently: playground00 is GPS week2363, street00/building02 week2364, with18-s GPS--UTC difference. Text uses seconds of week. Custom IMU increments match text; they are not rates multiplied by dt again. One predetermined full1$\times$ replay per route uses the same AT128/ADIS pipeline. At most two isolated technical replays run concurrently; no cache is chosen by accuracy and no deployment timing is inferred.

All policies on a route use identical LIO cache, GNSS observations, initialization, Q/R and lever arm. S9 selects one original reference state at the earliest timestamp covered by IMU, valid causal GNSS and the primary LIO cache. Selection scans timestamps, not positioning error, and the same row initializes every policy. Playground/building02 references begin before recorded sensors; this explicit pre-freeze interface rule avoids initializing outside coverage. street00 has one duplicate first reference timestamp; stable first-row retention is fixed before precision, with raw rows unchanged. Remaining reference states are used only offline. Local-to-NED alignment is fixed, without method-specific trajectory fitting or claimed absolute origin recovery.

The new routes use navigation-grade GNSS/INS reference with OEM719 information; prior building01/parking00 use MM/INS with shared AT128 map matching. Neither reference construction establishes independence from every sensing/error source. The common reference/ADIS/primary-LIO timestamp interval, rather than the longer published reference duration, defines the full expected evaluation grid. The prior unresolved3.6013-m RMS frontend repeat difference remains a limitation, not a reason to select a favorable cache.

\subsection{Fixed Controls, Events and Endpoints}
B2 is LIO-only; B3 direct fusion; B4 NIS100; B5 Huber2.5; B6 availability-based protected recovery. Strict NIS11.3449/16.2662/30 retain their screened parameters. Clock2/5/10/15/30/60/90 disable motion/anchor veto while retaining availability and covariance protection. P-no-anchor and P-no-decay remove those components; P-no-motion equals B6 and time-only equals Clock2. These nineteen names include aliases, not nineteen original algorithms. Clock numbers denote qualification durations: monitoring windows and unresolved local-health fallback affect actual admission. Clock2 has the same two-second qualification as P, but actual event delays are measured rather than assumed equal.

At150/450/750-s offsets from common initialization with N/E/NE directions, seven categories retain three events each:3-m single jump,10-m clustered jumps,30/60-s deletions with unchanged return,30-s deletions then3/10-m biases held90s, and a10-m ramp. Natural data is the eighth case. Complete10/30/60/90/180-s post-return windows are checked against common support before the collective freeze. No event or route is selected by method error. Complete scientific source/tests, nineteen parameters, calibration, runtime/binary/cache, five raw identities and metric definitions are committed, pushed and exactly remotely verified for all included routes before the first new matrix opens.

The primary biased error is the equal-weight mean of three post90 horizontal RMSEs after30-s deletion and90-s10-m bias. All windows and whole-route evaluation use a full10-Hz expected grid, retaining missing/partial/censored status rather than successful intersections. Actual $t_{admit}$ is the first logged \texttt{accepted=true} KF update after the first physically present returning measurement; admission is censored at180s. Clean measurement-time delay must be at most15s, inclusive with $10^{-8}$-s tolerance. Conservative cache-availability bounds and5/10/30/60/90-s sensitivity budgets remain separate. Neither cached clock measures field end-to-end delay.

Joint qualification also requires full coverage and natural RMSE no greater than the best B4/B5/B6 natural error plus $\max(2\%,0.05\,\mathrm{m})$. This gate never removes unqualified controls from raw tables. Injected accepted/exposed IDs measure controlled exposure, not field error probability; displacement can cancel original receiver error. P95/Max, all categories, extended windows and all individual events remain in the evidence. Cross-route aggregates weight each registered route equally and do not discard unfavorable signs.

\section{Results}
\input{generated_tables.tex}
\begin{figure*}[t]\centering
\includegraphics[width=\textwidth]{figures/multiroute_tradeoff.pdf}
\caption{Every fixed route and finite-delay policy. Clock labels are qualification durations; dotted line marks15-s clean measurement-time budget. Red stars are P, crosses ablations, triangles strict NIS, squares established baselines. Each panel has its own vertical scale. Censored LIO-only remains in the table and exported points. Lower raw error outside service/cost gates is retained.}
\label{fig:tradeoff}\end{figure*}
\subsection{Complete New-Route Comparison}
'''+ '\n\n'.join(route_paragraphs)+r'''

The complete matrix runs all19 policies in all8 conditions per new route. An independent checker that does not import the evaluator recomputes whole-route/window RMSE, actual accepted admission, availability bounds and injected exposure. Original64 tests,9 R2 metric tests and three sets of9 S9 role/config/numeric/metric tests pass. All whole-grid coverage, missing records and command exits accompany the tables; technical failures are retained. No new-route parameter or algorithm revision is performed.

\subsection{Anchor Attribution and Adverse Events}
'''+event_table+r'''
Table~\ref{tab:events} reports every prespecified primary event, including delays inside the biased interval and after it. A lower P macro error against Clock2 cannot by itself identify the anchor contribution: no-anchor holds the remaining manager fixed, while no-decay changes weighting. Full per-event paired differences and no-decay results constrain attribution. Same clean qualification does not guarantee equal delayed admissions during biased recovery. Long waiting can obtain lower raw error at a slower clean return; its local-health fallback may also admit earlier unresolved observations. Complete accepted-row logs preserve these cases rather than declaring the duration a guaranteed quarantine.

The new-route descriptive signs are: '''+abstract_result+r''' Table~\ref{tab:allroutes} includes strict NIS, Huber, long waits and every ablation irrespective of qualification; the evidence package reports paired natural-cost differences and all event signs, not only winning comparisons. A small mean advantage with opposing individual events is treated as a conditional effect, not universal rejection of persistent bias. If P fails the natural or clean gate, raw biased improvement is explicitly separated from compliant service gain.

\subsection{Preserved Earlier Counterevidence}
On building01, P clean admission is7s and bias90 error2.378m versus eligible B3/B4 at4.030m, but natural5.273m exceeds the frozen5.055-m cap. Its biased event admissions are97/7/7s; accepted injections are0/83/83 of90 each, and the second event is worse than B3/B4. Clock90 raw error2.362m is lower than P, despite95-s maximum clean delay; its second biased event falls back at17s. No-decay has lower natural and180-s error. These S8 failures remain unchanged.

On seen parking00, NIS30 is faster and lower in bias90 than P (0s/2.023m versus7s/2.290m). On seen building00, P bias90 is3.022m versus Clock10 at5.361m, but Clock90 reaches2.510m with95-s clean delay. Its second frontend cache is retained sensitivity, not another route. R1's \texttt{NO\_ADDITIONAL\_GAIN} remains intact. The independent S8 native KF-GINS fixed-configuration transfer gives17.10-m natural error; it is neither the best possible KF-GINS configuration nor a denominator for P improvement, and its posterior is not injected into P.

\section{Discussion and Applicability}
Persistent receiver displacement cancels in short relative-motion differences; the historical anchor can provide longer memory, while carrying older GNSS error and LIO drift. The observed comparisons apply to the registered finite artificial biases, common controlled initial states and these route overlaps. Accepted injections can partly cancel receiver error, so exposure and position error are distinct endpoints. Anchor staleness, unresolved local-health fallback and nonuniform no-decay effects remain failure mechanisms. Actual delayed updates, clean service and natural-route cost must be assessed jointly.

The extension adds scene diversity without new-route tuning. It remains a fixed descriptive study: within-route events are correlated, reference systems differ, and three new routes do not establish a population-wide effect or calibrated integrity. Known initialization and fixed alignment restrict transfer. Shared GNSS error sources and the earlier frontend repeat discrepancy remain unresolved. Native mapping timing excludes preprocessing/publication/wait; Python cache replay excludes frontend/transport. No result establishes field realtime admission or actual multipath identification.

\section{Conclusion}
Historical motion anchors can alter the error--admission tradeoff, but their value depends on the route, event and application gates. This complete prospectively frozen extension reports all19 unchanged policies, same-qualification/no-anchor contrasts, stronger simple alternatives and all adverse events. Numerical biased-return changes are separated from satisfying clean15-s service, natural-cost and coverage requirements. The evidence supports a bounded empirical review manuscript; it does not automatically establish novelty, compliant universal superiority or readiness for formal submission.

\section*{Reproducibility and Acknowledgments}
S9 source/configuration/input/cache hashes, collective freeze and verified remote receipts, all route/event tables, vector figures and independent checks are retained on the separate authorized branch. R1/R2/S8 sources, failures and paper versions remain unchanged. Raw bags/runtime/full numeric caches remain local; Git is a partial evidence backup. The current PDF is for author review, with no assigned authors/affiliations/funding. Exact venue template variant, anonymity, cutoff/timezone and applicable AI rules require human confirmation; no login, payment, copyright agreement or formal submission is performed.

OpenAI Codex (GPT-6) assisted orchestration, evaluation/plot code, evidence organization and drafting of the abstract and all text sections. Numerical figures derive from retained real runs. Human authors must verify interpretation, code, references and wording before adoption; disclosure does not replace author responsibility or venue-specific rules.
\bibliographystyle{IEEEtran}\bibliography{references}
\end{document}
'''
text=text.replace('week2363','week 2363').replace('week2364','week 2364')
(version/'main.tex').write_text(text)
shutil.copy2(ROOT/'paper/submission_candidate/s8/references.bib',version/'references.bib')
(version/'figures').mkdir()
shutil.copy2(ROOT/'paper/submission_candidate/s8/figures/framework.tikz',version/'figures/framework.tikz')
(version/'narrative_numeric_bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
(version/'event_numeric_bindings.json').write_text(json.dumps(event_bindings,indent=2)+'\n')
(OUT/'paper_source_receipt.json').write_text(json.dumps({'version':str(version),'source_SHA':hashlib.sha256(text.encode()).hexdigest(),'all_routes':state['included_routes'],'new_narrative_bindings':len(bindings),'per_event_cells':len(event_bindings),'novelty_claim':False,'formal_submission_performed':False},indent=2)+'\n')
print('Full S8-based multiscenario manuscript source written from actual complete runs')
