# LIO-GINS-R1

Independent localization research in `/home/aaron/lio_gins`: the pinned i2Nav AT128/ADIS adaptation of FAST-LIO2 provides local motion; raw F9P SPP positions update a 3D position KF. KF-GINS is an independent GNSS/INS comparison. [Goal](docs/GOAL_LIO_GINS_R1.md), [status](docs/CURRENT_STATUS.md), [state](docs/GOAL_STATE.json) and [run register](docs/RUN_REGISTER.csv) are the recovery entry points.

P0–P3 are complete. All three candidate revisions and 36 main configurations are retained. The final retained-anchor candidate passes fixed-parameter attribution and two-cache development verification: primary target event macro RMSE 3.074919→2.373985m (22.80%) and sensitivity cache 2.893789→2.198809m (24.02%), with full coverage and the common natural cost cap. This is development evidence. The same-input frontend poses still differ materially; the two caches are sensitivity checks, not independent route replications. Frozen-route plumbing is being checked against every retained development output before any parking00 performance access. No novelty, independent gain or paper readiness is claimed.

## Existing-workspace replay

Run from the project root:

```bash
.venv/bin/python scripts/resume.py
.venv/bin/python scripts/run_development.py --mode cached --method B6 --case natural
.venv/bin/python scripts/run_development.py --mode cached --method P --case all
```

The B6 natural one-command entry actually passed in run `20261011T152315911135Z_P7_d04c590f`. Each entry creates an exclusive recorder directory and separately records backend and offline evaluator commands, configs and input identities. Cached mode reuses immutable LIO; its timing excludes the frontend. `--cache-run` can select the other preserved development cache without changing scientific parameters.

A complete sensor replay entry is also provided:

```bash
.venv/bin/python scripts/run_development.py --mode full --method B6 --case all
```

Full mode runs the controlled first-reference-epoch initializer, real 1× FAST-LIO, cache validation, fixed GNSS stress copies, native KF-GINS at preselected noise STD scale2, and the chosen backend/evaluator. Its component commands were actually executed earlier; the assembled full-mode command has not yet been executed as one new run. Running it consumes approximately another full route and can yield frontend numerical variation. It is reproduction, not a new parameter search.

The original 16 data files are read-only under `data/i2nav-dataset/{building00,parking00}`. Both bags match fixed official SHA. Never mount the entire dataset into an estimator: it contains reference files. FAST-LIO mounts only the bag. Online backends receive sensor/cache/initialization files; labels and reference trajectories are read only by the separate evaluator. Initializer reads exactly one reference state under `configs/initialization_protocol.json`, explicitly a controlled known-initial-state experiment. Unknown geographic origin means common initial-position-conditioned errors, not absolute WGS84 accuracy or operational no-prior startup.

## Environment and source reproduction

The current `.venv` uses Ubuntu22.04 system NumPy/SciPy/PyYAML/Matplotlib/lz4 through `--system-site-packages`; no host packages were installed. The source lock is `configs/sources.lock.json`; `scripts/fetch_sources.py` obtains pinned clean upstreams and checks submodules. Native KF-GINS builds with:

```bash
cmake -S third_party/KF-GINS -B build/kf-gins-original -DCMAKE_BUILD_TYPE=Release
cmake --build build/kf-gins-original -j4
.venv/bin/python scripts/record_run.py --phase P1 --purpose official_demo --input scripts/run_kf_demo.py --input third_party/KF-GINS/dataset/kf-gins.yaml -- .venv/bin/python scripts/run_kf_demo.py
```

Noetic runs with existing Bubblewrap user namespaces and project-local umoci, without Docker daemon or sudo. The official OCI digest is locked in `containers/base_image.lock.json`; the verified derived rootfs and binary identity are registered in `containers/derived_rootfs.local.json`. `pull_noetic_oci.py`, `prepare_noetic_context.py`, `prepare_availability_context.py` and `build_noetic_rootless.py` are the recorded build stages. Exact successful argv, dependency recovery chain and preserved build failures are in [environment report](docs/reports/P1_rootless_environment.md) and each recorded manifest/commands file. The Docker recipe remains an untested alternative; package ownership has an explicit single-UID approximation. A fresh checkout-to-full-route build has not been independently revalidated. Do not infer that it was from the available recipe.

Full frontend validation and timing are in [P2](docs/reports/P2_full_frontend.md). All matched controls are in [P3](docs/reports/BASELINE_REPORT.md); candidate decision cards and [final development verification](docs/reports/P4/final_verification.md) retain all cases. Common Q/R, lever, initialization, exact GNSS IDs and evaluation clocks are preserved. Raw receiver differences and retained anchors are monitors, never additional KF observations. Paper method/setup versions are internal drafts, with no authorship or submission.

## Heldout boundary and integrity

Parking00 can be processed only with an archived, SHA-verified scientific freeze supported by sealed gain/attribution/two-cache proof, unchanged mechanism and full development transition parity. Source/config mismatches reject access. Environment variables cannot bypass this boundary. The heldout matrix is preregistered in `configs/heldout_protocol.json`; its entry is `scripts/run_heldout.py FREEZE_DIRECTORY` under `record_run.py` only after freeze. No retuning or promoting a winning ablation after test access.

```bash
.venv/bin/python scripts/resume.py
.venv/bin/python scripts/record_run.py --phase P7 --purpose local_integrity --input scripts/verify_evidence.py -- .venv/bin/python scripts/verify_evidence.py
```

`resume.py` reads state, Git, active processes and receipts; active runs return exit3 to prevent duplicates. `--audit-data` explicitly repeats raw identity/metadata auditing. The recorder accepts individual files as `--input`, not directories. SHA seals regular bytes or symlink target text; historical semantics remain unchanged. All outputs, failures, source snapshots and paper versions are retained. SHA is local integrity, not backup: raw data currently have one local copy and off-site backup is unverified. No project remote is authorized, so checkpoints remain local. Old VPR, SSH, FlClash, host drivers/ROS/Python and global networking are untouched; no sudo, account, paid service, academic authorship or formal submission.
