# LIO-GINS-R1

Independent localization research: FAST-LIO2 local motion + receiver F9P SPP absolute updates; KF-GINS is a separate GNSS/INS comparison. Follow [goal](docs/GOAL_LIO_GINS_R1.md) and [current status](docs/CURRENT_STATUS.md). This checkout has an official KF-GINS demo and tested common interfaces; it does **not** yet have real i2Nav route baselines or a validated proposed method.

All commands below run from `/home/aaron/lio_gins`. Supplied project files are preserved. No changes to old VPR, global Python/ROS, drivers, proxy configuration or SSH. No remote push, authorship or submission.

```bash
python3 -m venv --without-pip --system-site-packages .venv
python3 scripts/record_run.py --phase P1 --purpose pinned_sources --input scripts/fetch_sources.py --input configs/sources.lock.json -- python3 scripts/fetch_sources.py
python3 scripts/record_run.py --phase P1 --purpose pinned_dependencies --input scripts/fetch_dependencies.py --input configs/dependencies.lock.json -- python3 scripts/fetch_dependencies.py
python3 scripts/record_run.py --phase P1 --purpose kf_configure --input third_party/KF-GINS/CMakeLists.txt -- cmake -S third_party/KF-GINS -B build/kf-gins-original -DCMAKE_BUILD_TYPE=Release
python3 scripts/record_run.py --phase P1 --purpose kf_build -- cmake --build build/kf-gins-original -j4
python3 scripts/record_run.py --phase P1 --purpose official_demo --input scripts/run_kf_demo.py --input third_party/KF-GINS/dataset/kf-gins.yaml -- .venv/bin/python scripts/run_kf_demo.py
```

The source-fetch scripts optionally accept `--proxy http://127.0.0.1:7890` for the already running proxy; no global setting is changed. They lock commits and refuse dirty upstream edits. Upstream CMake outputs in its own ignored bin/lib directories, which are not algorithm changes. Demo inputs are the original upstream files; only input/output paths change. For independent health evaluation:

```bash
python3 scripts/record_run.py --phase P1 --purpose demo_health --input scripts/check_kf_demo.py --input src/evaluation/reference.py --input src/adapters/geodesy.py -- .venv/bin/python scripts/check_kf_demo.py outputs/DEMO_RUN_ID
python3 scripts/record_run.py --phase P1 --kind synthetic --purpose interface_tests --input tests/test_common_interfaces.py --input src/fusion/position_kf.py --input src/adapters/geodesy.py --input src/adapters/sensor_text.py --input src/evaluation/reference.py -- .venv/bin/python -m unittest discover -s tests -v
```

`DEMO_RUN_ID` is the actual demo directory printed by the recorder. Current verified dependency versions: NumPy 1.21.5, SciPy 1.8.0, PyYAML 5.4.1, Matplotlib 3.5.1 (read existing host packages). No global installation. The exact host environment is recorded; fresh environments with different package versions require revalidation.

Place unmodified dataset files according to [the consolidated action list](docs/USER_ACTION_REQUIRED.md). Original bag checksum is compared to the fixed upstream repository; text hashes only establish local identity. Reference files stay separate from algorithm input. `scripts/resume.py` detects existing project processes and audits data without evaluating heldout performance.

With an already usable Docker daemon, prepare/build the isolated ROS environment:

```bash
python3 scripts/record_run.py --phase P1 --purpose noetic_context --input scripts/prepare_noetic_context.py --input containers/Dockerfile.noetic --input containers/run_inside.sh -- .venv/bin/python scripts/prepare_noetic_context.py
python3 scripts/record_run.py --phase P1 --purpose noetic_build --blocked-exit 127 --input scripts/build_noetic.py --input scripts/context_integrity.py -- python3 scripts/build_noetic.py outputs/CONTEXT_RUN_ID
```

The build entry verifies every prepared context file against its SHA manifest before invoking Docker. The Dockerfile pins a verified official base manifest. The derived image, apt package versions, build and replay are currently **unverified** because Docker is absent. The build context preserves original FAST-LIO algorithm parameters, applies separate logging and message-generation build-dependency patches, and includes a pinned Livox message-only compatibility package for the otherwise unused Livox header dependency. It is for AT128, not a complete Livox driver. See [source audit](docs/FASTLIO_SOURCE_AUDIT.md).

After a verified container build and bag SHA, the P2 development frontend entry is:

```bash
python3 scripts/record_run.py --phase P2 --kind real_frontend --purpose building00_fastlio --timeout 3600 --input scripts/run_lio.py -- python3 scripts/run_lio.py data/raw/building00.bag
```

This replay entry is prepared but has never run. It restricts the route to building00, mounts raw data read-only and an exclusive output directory writable, drops capabilities, and uses an isolated network. Final scan coverage, point/header time, IMU consistency, initialization and actual frontend runtime must pass before proceeding. KF-GINS robot configuration and B0–B6 real-data evaluation remain pending; the demo config must not be reused unchanged for ADIS/F9P. A one-command complete route/backend pipeline will be delivered after those interfaces are validated, not advertised as available now.

Every recorder invocation creates a new `outputs/<UTC_phase_hash>/`, raw logs, resolved config, input SHA, true exit code, sealed checksums and a small Git receipt. Failed/blocked runs remain. `scripts/verify_evidence.py` verifies local integrity and upstream cleanliness; SHA is not a remote backup. Large raw data, upstream clones and outputs are ignored by Git but preserved locally. Checkpoints are local only.

Heldout parking00 accuracy remains closed until real development evidence, matched recovery controls, ablations and scientific freeze satisfy the goal. No candidate revision budget has been spent and no paper or precision gain is claimed. Restore/clean-clone instructions are prepared; an end-to-end clean-clone robot run is not verified.
