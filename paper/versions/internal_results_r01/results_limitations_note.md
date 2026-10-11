# Internal results and limitations note

This is a research handover note accompanying the method and experimental setup drafts, not a submission manuscript. Final classification: **NO_ADDITIONAL_GAIN**. There are no invented authors, affiliations, abstract claims, acceptance promises or final publication PDF.

## Bounded development and the originally registered comparison

Three mechanism revisions and 36 main configurations were executed on building00 with common sensors, initialization, Q/R, immutable LIO and evaluation clocks. All r01 configurations failed the natural cost cap. r02 restored acceptable cost but its best primary improvement (0.067067 m, 2.18%) was below the registered 0.1 m and 3% continuation criteria. r03 retained a rule-qualified raw GNSS anchor across gap-triggered isolation, with no second measurement update.

Under the original registered controls, r03 changed the target-event macro horizontal RMSE from 3.074919 to 2.373985 m on the primary cache, and from 2.893789 to 2.198809 m on the preserved sensitivity cache. Natural costs and coverage passed. Removing motion management reproduced B6 exactly; removing the anchor reproduced r02 on the primary cache. These facts justified the contemporaneous freeze under the registered protocol. They do not by themselves exclude a stronger duration-only explanation.

## First frozen heldout result

The scientific archive was created before any positioning-performance access to parking00. First access was the controlled single-reference-epoch initialization at 2026-10-11T15:44:46.793235 UTC. The original ten-method, eight-condition matrix completed 80 backend/evaluation pairs and 210 event evaluations with full coverage. The strongest eligible original fixed control B4 achieved 2.122390 m target macro RMSE; unchanged P achieved 1.911108 m, a 0.211282 m or 9.9549% difference. Natural errors were 2.362022 and 2.362052 m, within the common cap of 2.412022 m. The no-decay ablation reached 1.893773 m and was not promoted after opening the test.

All seven categories, whole-route errors, P95/max errors, update corrections, rejected observations, recovery times and failures are retained in the linked source summary and original child runs. Native KF-GINS with development-selected noise scale2 had parking00 horizontal RMSE76.561301 m despite finite ordered output and full coverage. This is a transferred-configuration failure, not a claim about the best achievable KF-GINS. It is excluded as the main percentage-gain denominator. Receiver-STD subsets are descriptive associations; they do not diagnose the failure causally.

## Counterevidence from the late control audit

At 2026-10-11T16:12:33.144856 UTC, after first heldout access and with partial heldout stdout already visible, a single supplemental development-only plan registered fixed qualification durations15/30/60/90 s. It disabled motion-score and anchor veto, retained other frozen parameters, evaluated all eight conditions on both original building00 caches, and did not evaluate parking00 or change P. This was not part of the original blind matrix and is not described retrospectively as preregistered independent evidence.

| Duration | Primary cache target macro RMSE/m | Sensitivity cache target macro RMSE/m |
|---|---:|---:|
| 15s | 2.849704 | 2.686695 |
| 30s | 2.720413 | 2.562542 |
| 60s | 2.348402 | 2.124439 |
| 90s | 2.285876 | 2.024895 |
| Frozen P | 2.373985 | 2.198809 |

The fixed controls have eligible natural errors2.586890/2.070218 m. The60/90 s controls beat P on both caches. Thus the new motion-anchor mechanism does not surpass a reasonable stronger matched control on the declared primary metric. Original restricted improvements remain genuine but do not support the broader incremental claim. P readmits after7 s in the three natural-recovery stress events versus95 s for the90 s control. This tradeoff does not justify switching the primary metric or claiming that every readmitted raw observation is correct.

## Limitations and decision

The reference MM/INS uses AT128, and initialization uses one reference state. Errors are conditioned on a common initial local pose rather than proven absolute WGS84/no-prior startup. The two same-input building00 frontend trajectories differ by3.601 m local3D RMS for an unresolved reason; cache sensitivity is not independent-route replication. Artificial errors overlay naturally erroneous F9P and may cancel them. Long-lived anchors can be biased, and GNSS bias versus LIO drift can be observationally equivalent. Neither the engineering score nor the covariance is a calibrated integrity guarantee. Gradual protection is an existing control component and its removal was slightly better in the target metric. Ramps and normal recovery can worsen relative to individual controls.

FAST-LIO2 native processing averages17.3215 ms on building00 and17.9452 ms on parking00, with P95 22.7675/24.7482 ms. Those measures cover IMU processing through incremental map update; input preprocessing, callbacks/publication and waiting are excluded. Python replay timing excludes the frontend and is not measured field latency.

WinTA-GIL already studies windowed motion alignment and reacquisition heading; Dual-ACKF already uses phase-dependent adaptive updates. The local B6 is not a full reproduction of either paper. Full neighboring formulas were not all accessible and none were invented. Newness and publication readiness remain unsupported. Stop the bounded mechanism search, preserve all evidence and deliver the runnable pipeline, internal drafts, author brief and recovery audit. No fourth revision, new blind test, failure-study submission manuscript or publication action follows automatically.

Exact numbers, scripts, original and late registration times, run/config/input SHA and scope decisions are bound in claim_evidence_map.json/.md. Figures are static scientific plots generated from those same sources.
