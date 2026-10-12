# Building01 prospective experiment report

Scientific freeze: `freezes/s8/building01_20261012T050221174017Z/scientific_freeze.json`; SHA `bdff768cb3fe71aa11a7459799ffb7e8acab95c39612e4a7674398912a712f68`; exact remote commit `c9aa4c9a870eb1a7b1ab81685abad644debdb059` verified2026-10-12T05:03:29.450848+00:00 before first controller2026-10-12T05:04:05.679367Z. No scientific code/config/evaluation changes after freeze. R1/R2 preserved.

## Predeclared joint conclusion

P clean admission7s in all3 fixed clean events and full coverage. P natural RMSE=5.273450323m exceeds frozen cap=5.055153848m by0.218296475m. The cap derives from B4/B5/B6 min+max(2%,0.05m). P bias90=2.378450430m versus eligible B3/B4=4.029944136m (same biased error); this directional reduction is observed, but P does not satisfy the registered normal-cost condition. Therefore independent_case_specific_effect_supported=false, positive_effect_supported=false for the joint S8 claim, novelty_supported=false. No new method increment or tuning. Do not describe this as no numerical biased reduction, or as successful constrained generalization.

## Complete fixed comparison

| Policy | Natural(m) | Clean max(s) | Clean90(m) | Bias90(m) | Bias180(m) | Injected accepted/exposed | Joint15s |
|---|---:|---:|---:|---:|---:|---:|---|
| B2 | 8.404516 | None | 1.325269 | 1.325269 | 1.741577 | 0/270 | False |
| B3 | 4.908538 | 0.0 | 2.319464 | 4.029944 | 3.584792 | 270/270 | True |
| B4 | 4.956033 | 0.0 | 2.319464 | 4.029944 | 3.584792 | 270/270 | True |
| B5 | 5.149425 | 0.0 | 2.301720 | 3.782364 | 3.498295 | 270/270 | False |
| B6 | 5.251980 | 2.0 | 2.338041 | 3.181587 | 3.332646 | 262/270 | False |
| Clock10 | 5.251980 | 15.0 | 2.376263 | 3.139601 | 3.305583 | 225/270 | False |
| Clock15 | 5.251980 | 20.0 | 2.389359 | 2.902298 | 3.156346 | 211/270 | False |
| Clock2 | 5.251980 | 7.0 | 2.355073 | 3.159949 | 3.318931 | 249/270 | False |
| Clock30 | 5.251980 | 35.0 | 2.334158 | 2.843942 | 3.112807 | 183/270 | False |
| Clock5 | 5.251980 | 10.0 | 2.363615 | 3.156524 | 3.316522 | 240/270 | False |
| Clock60 | 5.251980 | 65.0 | 1.973417 | 2.368449 | 2.358033 | 123/270 | False |
| Clock90 | 5.251980 | 95.0 | 1.902440 | 2.361516 | 2.424605 | 73/270 | False |
| NIS0 | 5.398238 | 0.0 | 2.229298 | 2.998477 | 3.657992 | 180/270 | False |
| NIS1 | 5.300299 | 0.0 | 2.286887 | 2.471888 | 2.453926 | 180/270 | False |
| NIS2 | 5.078671 | 0.0 | 2.313443 | 3.170446 | 3.597846 | 235/270 | False |
| P | 5.273450 | 7.0 | 2.355073 | 2.378450 | 2.649473 | 166/270 | False |
| P_without_anchor | 5.273450 | 7.0 | 2.355073 | 3.171784 | 3.576318 | 249/270 | False |
| P_without_decay | 5.177244 | 7.0 | 2.341621 | 2.387579 | 2.532026 | 166/270 | False |
| P_without_motion | 5.251980 | 2.0 | 2.338041 | 3.181587 | 3.332646 | 262/270 | False |

B3 and B4 are the only joint-qualified policies on this route; their bias90 is exactly equal. B3 natural4.908538m is below B4 natural4.956033m. B2 has best raw bias90=1.325269m but never admits GNSS (C180) and natural8.404516m. NIS30 is faster at0s, with bias90=3.170446m and natural5.078671m, narrowly above cap; fully retained. Clock90 raw bias90=2.361516m is slightly below P, but clean95s and natural5.251980m fail gates. P-no-decay has slightly larger bias90=2.387579m, lower natural5.177244m and lower bias180=2.532026m than P2.649473m; decay is not uniformly necessary.

## All P biased fixed events

| Event/direction | Admit(s) | Bias90(m) | Bias180(m) | Injected accepted/exposed |
|---|---:|---:|---:|---:|
| 0/N | 97.0 | 1.166707984 | 1.242876542 | 0/90 |
| 1/E | 7.0 | 3.413112746 | 4.335334049 | 83/90 |
| 2/NE | 7.0 | 2.555530560 | 2.370209308 | 83/90 |

P event1 bias90=3.413113m is worse than B4/B3 event1=3.313884m; first-event improvement drives much of macro reduction. Events1/2 accept83/90 rows each. First-event97s is biased actual admission, not clean7s. All399 event records and1995 windows are retained, no successful-only subset. Figure event0 is fixed by pre-registered order, not selected after observing its favorable difference.

Clock90 is a qualification-duration policy, not an unconditional90s quarantine. Its biased event1 first admits at17s and accepts73/90 rows. The actual log at original GNSS ID529/SOW11179 has local_health_verified=false, stateUNRESOLVED, reason unavailable_local_evidence_mature_recovery_fallback. This inherited fallback is unchanged; clean maximum95s does not imply every biased event waits95s. No post-test strict-clock redesign is permitted.

Artificial bias reduces the offline initialized raw receiver error in44/270 rows (0/26/18 by event). Exposure is not true fault detection or harm probability. Neither the native processing time nor Python/cache-availability clock is field end-to-end timing.

## Verification and command evidence

First complete controller: `python3 experiments/s8/run_matrix.py`, recorder C_b139c048,152/152 backend runs exit0, parent exit0/wall189.265s. Evaluation: `python3 experiments/s8/reanalyse.py <complete_index.json>`, C_c55d6044 exit0/wall35.151s. Independent: `python3 experiments/s8/independent_check.py <analysis>`, C_78fb8460 exit0/wall39.970s;2147 error values,399 clocks/availability and exposure, maxdiff2.220446049250313e-16m. All whole-route/window grids complete;13689 expected epochs per pair. Real argv/input SHA/commit/exit/resource logs in immutable outputs_s8 and lightweight run_receipts, all failures retained. Original64 + R2 metric9 + S8 interface9 tests passed before freeze.

Native KF-GINS natural fixed STD-scale2 transfer: C_0cb3f986 estimator exit0; C_9393591d evaluator exit0. HorizontalRMSE17.098178m/P95 29.594792m/max112.513364m, coverage1.0. Raw F9P antennaRMSE15.320275m. Configuration-transfer result, not best KF-GINS and not method-gain denominator. Week0 native output is a placeholder; audited week2364 comes from bag/text.

## Evidence and remaining delivery

artifacts/s8/C summary/event/category tables, complete_index.json.gz and event_results.json.gz cover all methods/categories; per-windowP95/Max/coverage/censoring and run/config/input/cache/evaluator SHAs in full JSON. artifacts/s8/independent_check.json and native_KF_metrics.json. Full per-epoch/per-update logs stay in outputs_s8; raw/cache/runtime offsite backup unverified. Prior3.6013m frontend discrepancy/reference sharing/controlled initial state remain limitations. Paper D and final E audits are now complete; no formal submission or author action is performed.

## Cache-availability bound and budget sensitivity

P clean actual measurement delays=[7.0, 7.0, 7.0]s; conservative cache-availability bounds=[7.094380140304565, 7.091545820236206, 7.09679913520813]s. Both are not field wall-clock latency. Clock10 measurement15s is inclusive, but its availability bounds [15.09761643409729, 15.08025574684143, 15.091221570968628]s exceed15s. P fails joint eligibility at every registered5/10/15/30/60/90s budget because the unchanged natural-cost cap fails; no post-test allowance relaxation. Full budget details are in artifacts/s8/C/scientific_judgment.json.

## Final A–E delivery and acceptance

A: Five official originals checked (official bag SHA matched), GPS week2364 and18s GPS–UTC independently confirmed, sensor interfaces reconciled, single unchanged FAST-LIO full replay completed exit0. The first schema/time pairing check and an overly strict GNSS timestamp tolerance failed exit1; both original runs remain, corrected engineering audits passed before freeze.

B: All64 original,9 R2 metrics and9 S8 interface tests passed, nineteen estimator/config bodies preserved; full scientific freeze commit c9aa4c9a870eb1a7b1ab81685abad644debdb059 pushed/read back at2026-10-12T05:03:29.450848+00:00 before first C. One initial checkpoint protection assertion failed locally and is retained; no failed/partial freeze authorized precision access.

C: One independent152-pair matrix, all backend exit0,399 events/1995 windows complete; independent recomputation and native KF transfer exit0. Joint positive claim fails the registered natural-cost condition, no new method revision, novelty unsupported.

D: Complete six-page English author-review manuscript s8_r04 compiled and audited exit0;304 table cells checked, fonts embedded, no overfull boxes/undefined references, all six final pages inspected. Earlier s8_r01–r03, their PDFs, and all R1/R2 versions remain. Final PDF SHA25665023095573b427395b8867f8c676b4534c35ee3bec2fd0c0511b638cc61c11f. Full source, vector figures, numerical bindings, evidence map and Chinese author brief included.

E actual command: `python3 experiments/s8/record_run.py --stage E --purpose final_S8_freeze_order_seals_inheritance_PDF_delivery_audit --input experiments/s8/audit_delivery.py --input docs/research_s8/STATE.json --input docs/research_s8/FREEZE_PUSH_RECEIPT.json --timeout 300 -- python3 experiments/s8/audit_delivery.py`. Run outputs_s8/20261012T053344721656Z_E_4253a7b2 exit0, wall1.819415056s. Audit checked30 frozen inputs,84 source/config identities,186 already sealed runs/6893 entries and111 R2 delivery files: zero mismatches. Raw immutable stat identities unchanged; initial full SHA evidence preserved, no redundant42GiB hash. Two earlier failed interface runs and manual checkpoint failure retained. The E audit stores the pre-terminal flags snapshot; final STATE.json records autonomous execution separately.

Evidence: artifacts/s8/delivery_audit.json, artifacts/s8/DELIVERY_MANIFEST.json, docs/research_s8/DELIVERY.md and per-stage artifacts/s8/checkpoints. Git backup covers lightweight science/results/all paper versions, not raw originals/full runtime caches. Those remain locally retained; offsite raw/cache backup is not claimed. R1/R2 branches and all protected legacy contents unchanged.

No autonomous research blocker remains. Authors decide empirical Full Paper versus Abstract-only, exact cutoff/timezone/template/anonymity/AI policy, attribution/permissions and final submission in the consolidated human checklist. `execution_complete=true` applies to the authorized author-review research delivery; positive_effect_supported/novelty_supported/paper_ready/formal_submission_ready/formal_submission_performed remain false. Do not reopen building01 for tuning.
