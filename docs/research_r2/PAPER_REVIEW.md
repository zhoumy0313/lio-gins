# Scientific review of the r2_r03 author-review candidate

Disposition: **reviewable empirical study, Mode B; do not submit it as an independently validated new-method paper in its current state.** This is a Codex critical review, not acceptance, human author approval, or a prediction of acceptance. The six-page PDF is complete and numerically bound; scientific execution and paper readiness are separate.

## 1. Method and attribution

The implemented filter is a shared three-dimensional position KF propagated by fixed FAST-LIO2 relative motion. KF-GINS is an independent 21-dimensional GNSS/INS comparator, not the outer filter or a high-rate measurement source. The retained P-r03 manager uses current-window motion and historical raw-GNSS anchors; its engineering score is not a calibrated statistical test. Receiver observations are consumed once, and reference/fault labels are offline only, apart from the explicit common initialization. No mechanism revision was made (0/1 rounds, 0/8 candidate configurations). Claiming a novel general fusion algorithm or first recovery-aware motion-window strategy is unsupported.

## 2. Results and strong controls

All 19 named policies, all seven Clock durations, three stricter NIS controls, four ablation roles and censoring are disclosed. Time-only is exactly Clock2; no-motion equals B6. On the primary seen building cache, P has clean admission 7s and biased post90 error 3.0222m versus Clock10's 15s and 5.3611m, with accepted injected rows 68 versus 219/270. This supports a conditional seen-data tradeoff under the declared normal-cost/15s clean-service gates. It does not show improvement in every endpoint: Huber clean error is lower, and the second cache's B6 clean error is lower. NIS30 misses the primary natural cap by about 0.0322m; it remains visible, including the descriptive 5%-cap sensitivity.

Clock90 has lower biased90/180 error on both building caches, and Clock60 has lower biased90 error at the registered 90s deadline. Strict NIS30 on parking is faster (0 versus 7s) and more accurate (2.0234 versus 2.2901m) than P. P admits fewer injected rows there (108 versus 119/270), but this does not establish less actual harm. P's first primary biased-event admission is 126s, and it admits 65/90 injected rows in the third. These counterexamples belong in the abstract, tables and main narrative, and are included.

## 3. Repeatability and engineering

The 64 retained regression tests plus nine metric tests pass; byte identity is verified for P/B6 wrapper trajectories and update logs. An independent evaluator checks 6,441 error values, 1,197 admission clocks and exposure records with maximum discrepancy 4.44e-16m. These verify backend bookkeeping, not deterministic frontend performance. Two building caches have 3.6013m 3D RMS difference and 9.7876m maximum difference despite matching identities/timestamps/counts; cause remains unresolved. Unflagged numerical LIO resets are not fully detected. Cached backend timing is not end-to-end online timing. A transferred native KF-GINS failure is not that algorithm's best performance or a fair claimed improvement denominator.

## 4. Statistics and risk interpretation

Three fixed outage times/directions per category are correlated within route; two caches from the same bag are not independent route replications. Equal per-event RMSE, exact denominators, common expected-grid coverage and right censoring are appropriate descriptive outputs. No IID significance, real-fault probability or calibrated integrity claim is justified. Offline injection analysis finds 16 building and 46 parking injected rows reduce the declared initialization-conditioned receiver error; exposure counts must therefore be interpreted alongside actual error. The revised metrics and 15s deadline were chosen after R1 outcomes were known. All six registered latency sensitivities are retained rather than replacing the primary gate after seeing results.

## 5. Independent data and generalization

building00 and parking00 were both seen before R2. All five required building01 inputs remain absent; only official metadata and access attempts were audited. The archive is an ANALYSIS_FREEZE_ONLY and explicitly does not authorize opening new-route performance. Independent effect, method increment and novelty remain false. Reference sensing overlaps the frontend and the known common initial state restricts transferability. Neither missing data nor a new state field reverses R1 NO_ADDITIONAL_GAIN.

## 6. Format, references and venue

The final PDF has six pages including references/disclosure, embedded fonts, 285 audited numeric cells, no compile errors/undefined references/overfull boxes, and retained vector/TikZ sources. All pages were inspected by Codex; human review remains pending. Official public app content confirms a 2026-10-15 full-paper deadline, six-page cap, IEEE conference-template link and specific CMT entry. Exact template variant, anonymity, deadline timezone and conference-specific AI-policy applicability remain unverified. The title/abstract make empirical, conditional claims; nearest works are discussed, not falsely represented as executed SOTA comparisons. Authors, affiliations, funding, copyright, originality approval and formal submission remain human decisions.

## Recommendation and permitted claim

The package can support a discussion with the supervisor about an empirical recovery-policy study: admission latency, synthetic exposure and error are different outcomes, and complete matched waits expose a conditional building-route tradeoff plus stronger parking controls. Prefer independent validation and final venue checks before any submission decision. If the deadline prevents validation, the human authors must decide whether an explicitly limited empirical study is suitable; Codex does not remove the red marker or silently promote Mode B to a method paper. No additional parameter search is justified by the current evidence.

Evidence: `S3_report.md`, `BASELINE_AND_PARETO.md`, `FAILED_CASES.md`, `CLAIM_EVIDENCE_MAP.json`, `artifacts/r2/S3/`, `artifacts/r2/S6/`, and `paper/versions/r2_r03/`.
