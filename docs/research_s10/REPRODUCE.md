# S10 offline reproduction and retained artifacts

BaseS9 4f7a4b4c5b87040d7d7307f25a06cd785b1ff7b9; branch research/lio-gins-s10-moderate-bias-paper; no remote push authorized. Current source maintains old19 configs and all7 perturbations; S10 independently analyzes3m/10m/clean only. No new estimator/front-end run or data selection.

Read STATUS.md/STATE.json first; completed stages should not be rerun to recover context. Existing evidence is under artifacts/s10 and sealed cache/s10/runs. Actual commands/rc/wall/source snapshot/UTC are in each run receipt. Full raw outputs/cache stay local/ignored, with inputSHA and original path/run ID mapping, not pretending Git contains bags or complete old outputs. Archived absolute paths relocate only by identical run identity and SHA.

If a fresh offline reproduction is necessary, use the project recorder so no old run is overwritten:

```bash
python3 experiments/s10/record_run.py --stage VERIFY --purpose fresh_offline_audit -- python3 experiments/s10/check_numbers.py paper/submission_candidate/s10
```

The independent A/B/C/D scripts consume existing data/logs and write only LIO_GINS_S10_OUT. Figure input sources/all points are in figure_manifest.json. Use run_inherited_tests_isolated.py through recorder for old tests; direct old recorder/test execution may write the historical root register, so the shadow wrapper copies exact bytes and all required fixed fixtures. No old test/estimator file is patched.

The complete paper builds with project-local cache/r2/tools/tectonic and existing bundle cache. build_paper.py is restricted to preserved new version directories; prior failed/rejected versions and their real source/log/PDF are retained. Built-in editor compiler was attempted against saved candidate and lacks numbers/figures/Bib multi-file support; it does not validate this project. Original S8 tab stays open. Full project compiler, numeric checker and raster review validate the actual deliveredPDF.

The final integrity audit validates R2/S8/S9 delivery manifests, all532 input/output provenance pairs, inherited branch heads and all preceding S10 run seals. Its own recorder seal is validated separately after completion. Independent-confirmation/novelty/human-review/formal-submission flags remain false. No remote push, account action or formal submission performed.
