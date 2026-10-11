# LIO-GINS-R1

Independent localization research: FAST-LIO2 local motion and receiver F9P SPP updates; KF-GINS is the independent GNSS/INS comparison. Follow [goal](docs/GOAL_LIO_GINS_R1.md), [status](docs/CURRENT_STATUS.md), and [state](docs/GOAL_STATE.json). Official KF-GINS demo, real building00 KF-GINS initialization/sensitivity and rootless Noetic build/ROS smoke passed. Full building00 FAST-LIO replay and native timing now completed; the finite B3–B6 screen is running. Two same-input frontends differ materially, so scientific freeze additionally requires fixed-parameter robustness on both preserved caches. Proposed-method performance is pending.

Run commands from `/home/aaron/lio_gins`. Data originals remain read-only at `data/i2nav-dataset/{building00,parking00}/`; locations are in `configs/data_locations.json`. Both bags match official SHA. Never mount the entire dataset folder into an estimator: it also contains reference files. Online frontend mounts only its bag. Parking00 performance remains closed until development evidence and scientific freeze.

The existing `.venv` reads host NumPy/SciPy/PyYAML/Matplotlib without global installs. Pinned upstreams live in ignored `third_party/`; source/build/logging/research changes stay separate. No old VPR, host ROS/Python, SSH, drivers or global networking changes. No remote push, authorship or submission.

Official native KF-GINS and data audit:

```bash
cmake -S third_party/KF-GINS -B build/kf-gins-original -DCMAKE_BUILD_TYPE=Release
cmake --build build/kf-gins-original -j4
.venv/bin/python scripts/record_run.py --phase P1 --purpose official_demo --input scripts/run_kf_demo.py --input third_party/KF-GINS/dataset/kf-gins.yaml -- .venv/bin/python scripts/run_kf_demo.py
.venv/bin/python scripts/resume.py
```

`resume.py` first checks state, Git and active processes; it avoids duplicate experiments. Every actual experiment must use `record_run.py`, add its relevant scripts/config/input identities with `--input`, and retain the exclusive output directory. Read resolved configuration and recorded commands for exact completed-run argv; abbreviated recipes here are not substitute evidence.

The robot initialization protocol is `configs/initialization_protocol.json`, declared before accuracy: isolated exporter reads exactly one initial reference state; initial position comes from a causally available F9P and one lever correction. The online estimators read only `initial_condition.json`, sensor files and declared configs. Unknown geographic reference origin means shared initial-position-conditioned errors, not absolute WGS84 accuracy. B1 three-case noise screening is in `artifacts/robot_baselines/KF_noise_screen.json`.

Noetic is isolated with the already available Bubblewrap and project-local umoci, using a digest-locked official OCI filesystem. No Docker daemon or sudo is needed. The Docker recipe remains an alternative and has not been tested. Rootless unpack/package ownership is a declared single-UID approximation. See [environment report](docs/reports/P1_rootless_environment.md) for failures and actual verified package/build chain.

```bash
.venv/bin/python scripts/record_run.py --phase P1 --purpose pinned_OCI --input scripts/pull_noetic_oci.py --input containers/base_image.lock.json -- .venv/bin/python scripts/pull_noetic_oci.py
.venv/bin/python scripts/record_run.py --phase P1 --purpose context --input scripts/prepare_noetic_context.py --input containers/run_inside.sh -- .venv/bin/python scripts/prepare_noetic_context.py
.venv/bin/python scripts/record_run.py --phase P2 --purpose availability_context --input scripts/prepare_availability_context.py --input containers/run_inside.sh -- .venv/bin/python scripts/prepare_availability_context.py outputs/CONTEXT_RUN
.venv/bin/python scripts/record_run.py --phase P1 --purpose rootless_build --timeout 3600 --input scripts/build_noetic_rootless.py --input containers/build_rootless_inside.sh -- .venv/bin/python scripts/build_noetic_rootless.py outputs/OCI_RUN outputs/AVAILABILITY_CONTEXT_RUN
.venv/bin/python scripts/record_run.py --phase P2 --kind real_frontend --purpose building00 --timeout 3600 --input scripts/run_lio.py --input containers/run_inside.sh --input containers/shutdown_clock.py --input containers/derived_rootfs.local.json -- .venv/bin/python scripts/run_lio.py data/i2nav-dataset/building00/building00.bag
```

Replace run placeholders by real printed run IDs. The current verified build recovered a retained package configuration chain; a fresh-clone dependency-to-full-route run is not yet revalidated. Frontend uses official AT128/ADIS parameters, log-only patches, isolated networking, read-only OCI subtrees/original bag, and an exclusive writable output. Inspect coverage, point/pose timestamps and availability before making a cache.

`build_lio_cache.py` validated a complete real cache and native timing correspondence; `run_outer_baseline.py` is executing the finite registered controls. Cached-backend runtime must not be advertised as including frontend processing. No validated candidate implementation or scientific gain exists yet; mechanism revision budget remains 0/3. Baseline/event protocol is declared in `configs/development_experiment_protocol.json` before LIO global accuracy.

Run logs, configs, trajectories and failures are never overwritten. New recorder runs preserve exact small source inputs and dirty patch; sealed SHA distinguishes regular bytes and symlink target text. Older receipts lack that source snapshot feature and keep their original hash semantics. Large raw data, clones and outputs stay local/ignored; lightweight receipts, scripts and figures are in Git. `scripts/verify_evidence.py` checks local integrity; SHA is not an off-site backup. Original data currently have one local copy. Checkpoints are local only.
