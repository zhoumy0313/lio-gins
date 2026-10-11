# Exclusive-run reproduction entry points

Run from `/home/aaron/lio_gins` with the working R1 Python environment. Preserve existing outputs; the recorder creates a new UTC/run-hash directory and records code/input identities, real argv, exit, CPU/RSS and timing. No ROS redeployment is needed for cached backend analysis. These commands require the local inherited raw references/caches/full backend logs; a remote-only clone is not the full numeric/runtime/data backup.

## Recompute metrics from the executed 456-pair index

```bash
python3 experiments/r2/record_run.py --stage S7 --purpose author_recompute_metrics --input experiments/r2/reanalyse.py --input outputs_r2/20261011T181051808417Z_S3_274770dc/complete_index.json --timeout 600 -- python3 experiments/r2/reacquisition_metrics.py outputs_r2/20261011T181051808417Z_S3_274770dc/complete_index.json
```

The command prints its new output directory. Use that actual directory for the independent checker rather than overwriting the existing final analysis:

```bash
python3 experiments/r2/record_run.py --stage S7 --purpose author_independent_check --input experiments/r2/independent_check.py --timeout 600 -- python3 experiments/r2/independent_check.py outputs_r2/20261011T181349420151Z_S3_991cd0d6
```

The shown checker command verifies the delivered analysis; to check a fresh recomputation, replace only its analysis-directory argument with the new returned path. It does not import the main evaluator. The metrics entry point delegates to reanalyse.py; future causal estimates are never computed by reading the reference evaluator.

## Regression or plot/PDF rebuild when justified

```bash
python3 experiments/r2/record_run.py --stage S7 --purpose author_regression --input experiments/r2/run_regression.py --timeout 300 -- python3 experiments/r2/run_regression.py
python3 experiments/r2/record_run.py --stage S7 --purpose author_vector_figures --input experiments/r2/make_review_figures.py --timeout 180 -- python3 experiments/r2/make_review_figures.py outputs_r2/20261011T181349420151Z_S3_991cd0d6
python3 experiments/r2/record_run.py --stage S7 --purpose author_PDF_compile --input experiments/r2/build_paper.py --input paper/versions/r2_r03/main.tex --timeout 180 -- python3 experiments/r2/build_paper.py paper/versions/r2_r03
```

The compiler is the retained project-local Tectonic0.17.0 and bundle cache, not a global install. Rebuild output remains in the new run. Do not copy it over an archived paper version; create a new version if adopting changes. Upstream source/rootfs/environment and common input policies are fixed in configs/sources.lock.json, containers/derived_rootfs.local.json, configs/r2/wrapper_lineage.json and the analysis archive.

The original matrix was completed by `complete_clocks.py` (88 missing pairs) and `strict_nis_controls.py` (72 fixed diagnostics); all296 inherited plus160 added pairs already exist. Re-executing these estimators is unnecessary for metric verification. Preserve exact source/index identity if doing an authorized future reproducibility study.

## New building01 route

No runnable new-route performance claim exists yet. The seen-only wrappers deliberately reject building01. First obtain all five official originals, verify bag SHA/timebase/GPS week/calibration/coverage and the declared initial-state protocol, prepare the required new-route adapter, freeze complete input/source/config/event/metric identities, commit and push that freeze, and then execute the complete fixed matrix once. Current ANALYSIS_FREEZE_ONLY is not sufficient. Never tune thresholds or select windows on the future independent result.

Recorded real commands/exit/timing are in COMMAND_INDEX.csv and each artifacts/r2/run_receipts/<run_id>/commands.jsonl. Failures, initial SSH push failures and corrected discovery/metadata attempts remain retained. Cached backend CPU/wall timings and R1 native frontend scan timing are separate from unmeasured end-to-end receiver-arrival latency.
