# Full executed experiment report

Scope: retrospective seen building00 (two caches of one route) and previously opened parking00. No new independent route was executed. R1 P-r03/filter/core are unchanged. The paired primary scenarios are30s observation deletion followed by unmodified receiver data or90s of10m artificial bias. Seven event categories plus natural data, three fixed offsets150/450/750s and N/E/NE directions are unchanged from R1. All other categories are retained, not selected out.

The matrix is19 named policies ×3caches ×8cases =456pairs, with1197event records and5985post-return windows.296pairs are inherited and160are added cached controls (88complete waits/B2,72strictNISdiagnostics). No old frontend pipeline was redeployed. All expected-grid windows are complete; inherited whole-route RMSE parity is exactly0. Independent recomputation checks6441error values,1197admission clocks/exposure records, max4.44e-16m. Original64+new9tests pass.

## Protocol and fair comparison

Identical inputs/cache/filter/Q/R/lever/initial state are paired within each comparison. Natural cost cap is the minimum frozen originalB4/B5/B6 natural RMSE plusmax(2%,0.05m); strictNISandablations do not change that reference retrospectively. Primary clean service deadline is15s inclusive measurement-time; availability is a separately reported conservative cache bound, not real receiver latency. Every original GNSS ID is consumed once. Real accepted=true updates determine admission; no-updateB2 is right-censored at180s. Error recovery is offline error<=3m held5s within90s, distinct from admission and potentially preceding a GNSS update. Every10/30/60/90/180s window uses the full common10Hzexpected grid; incomplete windows retain missing status, not a successful-only RMSE. Equal event RMSE macro is used.

Motion/time monitor differences and historical raw GNSS anchors are not reused as independent position measurements. Truth/fault labels are offline except the explicit common initialization. Measurements are initialization-conditioned localNED results, not a no-prior absoluteWGS84 claim. Exposure is acceptance of synthetic injected rows, not real GNSS fault probability.

## Complete primary building00 comparison

Units:m; clean delay:s maximum over allthreeevents; C180 denotes180s censoring. Q satisfies both natural-cost and15s clean admission gates. No policies are excluded from this table.

|Policy|Natural|Clean delay|Clean90|Bias90|Bias180|Accepted injected /270|Q|
|---|---:|---:|---:|---:|---:|---:|---|
|B2|3.4457|C180|1.7730|1.7730|2.5561|0|no|
|B3|2.5614|0|2.1817|8.3713|6.9712|270|yes|
|B4|2.5614|0|2.1817|8.3713|6.9712|270|yes|
|B5|2.5383|0|2.1419|7.6445|6.6134|270|yes|
|B6|2.5869|2|2.2647|5.7798|5.5674|254|yes|
|Clock10|2.5869|15|2.3189|5.3611|5.3061|219|yes|
|Clock15|2.5869|20|2.3214|4.8986|4.9674|202|no|
|Clock2|2.5869|7|2.3133|5.5580|5.4291|243|yes|
|Clock30|2.5869|35|2.3091|4.4265|4.6339|161|no|
|Clock5|2.5869|10|2.3163|5.4902|5.3862|234|yes|
|Clock60|2.5869|65|2.4488|2.8377|3.0437|73|no|
|Clock90|2.5869|95|2.5094|2.5098|2.4111|0|no|
|NIS11.3449|3.1854|0|2.0954|3.6529|4.2786|115|no|
|NIS16.2662|3.1643|0|2.1398|3.7002|4.2240|121|no|
|NIS30|2.6212|0|2.1817|3.9082|3.8979|127|no|
|P|2.5847|7|2.2361|3.0222|2.9760|68|yes|
|P-no-anchor|2.5847|7|2.2482|5.4893|5.6111|237|yes|
|P-no-decay|2.5283|7|2.1623|3.0589|2.9682|68|yes|
|P-no-motion|2.5869|2|2.2647|5.7798|5.5674|254|yes|

Complete19-policy second-cache/parking values are in paper TableII, `artifacts/r2/S3/summary_table.csv` and the full event table/JSON; all windows and availability bounds are retained there. This is not an independently heldout R2 matrix.

## Scientific judgement and counterexamples

H1 is descriptively supported: fixed waits expose the latency/error/exposure tension. H2 is a conditional building-route tradeoff: P's biased90error3.0222m versus fastest-budget-qualified Clock10's5.3611m,68versus219accepted/270; Pclean7s versus15s. Second-cache direction persists (P2.8837m,66/270). P is not best in every outcome: primaryHuber clean902.1419m versusP2.2361m; second-cacheB6clean901.8601m versusP1.8854m. StrictNIS30outside primary natural cap by~0.0322m remains reported; at5%normalallowance it qualifies andPstillhaslowerbiasederror, a descriptive sensitivity rather than a new primary gate.

Clock90 produces lower biased90 and180error on both building caches while cleanadmission95s violates15s. At the registered90sdeadline Clock60iseligible and moreaccurate thanP on both caches. Six deadlines5/10/15/30/60/90s and all19policies are retained in `artifacts/r2/S5/deadline_sensitivity.csv`,342rows. R1's unrestricted-error NO_ADDITIONAL_GAIN conclusion remains unchanged.

Parking strictNIS30is a stronger simple control:2.0234m biased90 versusP2.2901m,clean0versus7s,119versus108accepted/270. Eleven fewer injected rows does not establish lower real harm. Removing decay also improves parking error and violates the second building-cache natural cap. Removing anchor worsens primarybuilding bias903.0222to5.4893m, supporting conditional attribution of the existing anchor, not a new mechanism contribution. Time-only is exactlyClock2; no-motion isB6.

P's primary biased-event admissions are126/43/25s with0/3/65accepted rows; sensitivity124/43/27s with0/3/63; parking8/64/97s with82/26/0. The representative figure is the first registered primary event, not a best winning event. Clean7s does not imply biased7s. Natural/injection errors remain separately interpreted: offline antenna analysis finds16/270building and46/270parking injected rows reduce declared initialization-conditioned receiver error.

H3 is unsupported. No independent building01performance, method revision or general novelty is established. Zero of one permitted mechanism revisions and zero of eight candidate parameter configurations were used. A further search is not justified by these results.

## Engineering limits, failures and timing

Two verified building frontend caches have identical pose clocks/output counts12440but3.60128849m3DRMSdifference,max9.78764005m,firstdifference>1e-8near80s. Root cause remains unresolved; clockavailability/EOF differ but no proved concurrency explanation. Unflagged numerical reset can propagate through the current interface. Native frontend R1 mean/P95processing17.32/22.77msper scan excludes the GNSS backend/transport; Python cached runtime is not end-to-end online timing. Native transferred KF-GINS parking76.5613m is a configuration-transfer failure, not optimalGNSS/INSaccuracy or an improvement denominator.

Failed regression-discovery/legacy-checker attempts, SSH push failures/retries, paper-layout iterations and closing-audit failures are retained in FAILED_CASES.md and run receipts. Corrected engineering checks do not erase failed attempts.

## Identity and evidence

R1 base:c12a42a3484458e1737e63201792e1122fc99c0d. Final numerical analysis:outputs_r2/20261011T181349420151Z_S3_991cd0d6,exit0/86.899s. Its all456event-result rows bind run/config/cache/reference/input/evaluatorSHA. `CLAIM_EVIDENCE_MAP.json` gives ten supported/negative/unsupported claim groups. SummarySHA275f2c56c618e25fb800393d22bfc3e60fc9f6430dc35c95c8840806c8a9258d. Full source/config/input/environment archive is ANALYSIS_FREEZE_ONLY, new openingunauthorized. Data/reference hashes are from actual file reads, not fabricated registration. The old tests/filter/manager remain unchanged.

building01official metadata/access audit records allfiveinputs absent. This is ModeB: full six-page numerical manuscript with NOT_SUBMISSION_READY, independent/methodincrement/novelty/formalflagsfalse. See AUTHOR_DECISION_BRIEF_ZH.md and AUTHOR_CHECKLIST.md before any human submission decision.
