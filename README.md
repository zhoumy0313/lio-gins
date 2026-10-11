# LIO-GINS-R1

Independent localization research: pinned i2Nav AT128/ADIS FAST-LIO2 supplies local motion; raw F9P SPP updates a3D position KF. KF-GINS is an independent GNSS/INS comparator. **Final research conclusion: NO_ADDITIONAL_GAIN.** Original registered parking00 B4→P target macro RMSE2.122390→1.911108m (9.9549%) is preserved, but stronger fixed-duration controls beat P on both development caches at eligible natural cost. No efficacy/novelty/submission readiness is claimed. See [delivery](docs/DELIVERY.md), [final decision](docs/reports/P4/late_control_decision.md), [complete heldout report](docs/reports/P5_frozen_heldout.md), [state](docs/GOAL_STATE.json) and [claims](docs/CLAIMS_SUPPORTED.md).

## Existing archive: one-command backend replay

From the project root:

```bash
.venv/bin/python scripts/resume.py
.venv/bin/python scripts/run_development.py --sequence building00 --mode cached --method B6 --case natural
.venv/bin/python scripts/run_development.py --sequence building00 --mode cached --method P --case all
.venv/bin/python scripts/replay_frozen_backend.py --method B6 --case natural
.venv/bin/python scripts/replay_frozen_backend.py --method P --case natural
```

Development B6 one-command replay actually passed in20261011T152315911135Z_P7_d04c590f. Frozen parking B6/P archive recovery passed in20261011T163106760681Z_P7_804d7747 and20261011T163820527256Z_P7_a26caac5: trajectory and update-log bytes exact, numeric metrics equal. `--case all` includes all eight original conditions. These commands need the retained original outputs/cache/initialization and are archive reproductions, never new blind tests. Each new invocation gets an exclusive recorded directory; no run is overwritten. Cached timing excludes the frontend.

The original entry rejects unordered/duplicate GNSS times. For a **new, unlabeled development-only** observed CSV, `scripts/canonicalize_development_gnss.py SOURCE NEW_COPY` can establish chronological order without changing values or original IDs. It verifies source/initialization identity and refuses labeled/heldout input. Numerical results survive unique ID renumbering; ID-bearing logs and input-byte SHA necessarily change, and old cached input identity must not be reused. This helper is outside the scientific freeze and never changed an original experiment.

## Clean checkout with already downloaded data: environment and full development replay

There is no authorized remote. A local Git clone or local source bundle can supply this checkout. Git excludes raw data, outputs, caches, builds and the venv; they are not magically present in a source clone. Point `data/i2nav-dataset` at the retained read-only building00/parking00 source directory, or retain the downloaded originals at that path. Do not copy75GiB unnecessarily. Source-only reproduction can regenerate **building00** components; exact archived parking results additionally require the original archive and frozen runtime registry, including their original path bindings.

Supported recorded host: Ubuntu22.04 x86_64, GCC11.4, CMake3.22, Python3.10.12. Existing host prerequisites: Git/CMake/C++ compiler, Bubblewrap with usable user namespaces, dpkg/apt download, NumPy1.21.5, SciPy1.8.0, PyYAML5.4.1, Matplotlib3.5.1 and lz4. No host packages were installed by this project. A different host missing these prerequisites is not silently repaired with sudo. Keep>=80GiB free, build<=4 jobs. The per-process public proxy used here is127.0.0.1:7890; rootless pull/build scripts use that existing proxy, never reconfigure host networking. If it is unavailable, restore the existing project network prerequisite or record a local adaptation before a development rebuild.

Run from a clean checkout root:

```bash
python3 -m venv --without-pip --system-site-packages .venv
.venv/bin/python -c 'import numpy,scipy,yaml,matplotlib,lz4; print(numpy.__version__, scipy.__version__)'
.venv/bin/python scripts/fetch_sources.py --proxy http://127.0.0.1:7890
.venv/bin/python scripts/fetch_dependencies.py --proxy http://127.0.0.1:7890
cmake -S third_party/KF-GINS -B build/kf-gins-original -DCMAKE_BUILD_TYPE=Release
cmake --build build/kf-gins-original -j4
.venv/bin/python scripts/record_run.py --phase P1 --purpose official_demo --input scripts/run_kf_demo.py --input third_party/KF-GINS/dataset/kf-gins.yaml -- .venv/bin/python scripts/run_kf_demo.py
.venv/bin/python scripts/record_run.py --phase P1 --purpose raw_data_identity --input scripts/audit_data.py -- .venv/bin/python scripts/audit_data.py
```

`sources.lock.json`/`dependencies.lock.json` fix upstream commits; their initial status strings are historical, not current execution state. Fetch checks commit, dirty source and submodules. Original FAST-LIO2 is attribution/diff reference; the i2Nav adaptation is the actual AT128 implementation. No upstream algorithm is silently upgraded.

For isolated Noetic, first obtain the project-local unpacker; `apt download` fetches a package without host installation:

```bash
mkdir -p cache/local-tools
(cd cache/local-tools && apt download umoci=0.4.7+ds-2ubuntu0.1)
dpkg-deb -x cache/local-tools/umoci_0.4.7+ds-2ubuntu0.1_amd64.deb cache/local-tools/umoci
```

Record each stage and capture its actual output path, rather than copying this machine's historic run names into a new checkout:

```bash
project_record() {
    local project_purpose=$1; shift
    local project_script=$1; shift
    local project_receipt
    if project_receipt=$(.venv/bin/python scripts/record_run.py --phase P1 --purpose "$project_purpose" --timeout 7200 --input "$project_script" -- .venv/bin/python "$project_script" "$@"); then
        printf '%s\n' "$project_receipt" >&2
        .venv/bin/python -c 'import json,sys; print(json.loads(sys.stdin.read().splitlines()[-1])["output"])' <<< "$project_receipt"
    else
        local project_code=$?
        printf '%s\n' "$project_receipt" >&2
        return "$project_code"
    fi
}
project_base=$(project_record locked_noetic_pull scripts/pull_noetic_oci.py) || exit $?
project_context=$(project_record pinned_at128_context scripts/prepare_noetic_context.py) || exit $?
project_availability=$(project_record time_health_logging_context scripts/prepare_availability_context.py "$project_context") || exit $?
project_build=$(project_record isolated_noetic_build scripts/build_noetic_rootless.py "$project_base" "$project_availability") || exit $?
.venv/bin/python scripts/run_development.py --sequence building00 --mode full --method B6 --case all
```

Base OCI digest is locked in `containers/base_image.lock.json`. Build uses a copied project rootfs, signed package downloads, unchanged pinned sources, separate build/logging patches, cleared host ROS environment and `catkin_make -j4 -l4`; derived identity is registered automatically. Single-UID ownership is a declared approximation. The Dockerfile is an untested alternative. Build failures remain sealed; `--resume-from FAILED_BUILD_RUN` verifies a retained failed rootfs before reusing its dependency cache. Do not reset/delete a failed directory or treat exit0 from context preparation as a compiled runtime.

Full mode exports exactly one reference initialization state, performs real1×FAST-LIO, validates cache/time/health, derives fixed stress copies, runs native KF-GINS at development-selected STD scale2 and independently evaluates chosen backend. The individual building00 components and the entire assembled parking matrix were actually executed. **This documented clean-checkout→environment→building00 full command has not been independently executed as a new clean-clone test.** Archive recovery is separately verified and does not remove that portability limitation. [Environment report](docs/reports/P1_rootless_environment.md) preserves exact successful argv, package versions and failure/recovery chain.

For archived parking full reproduction, after verifying the unchanged scientific freeze and its original environment bindings:

```bash
.venv/bin/python scripts/record_run.py --phase P5 --purpose archived_full_parking_reproduction --kind engineering --timeout 5400 --input scripts/run_heldout.py --input freezes/LIO_GINS_R1_20261011T154403129394Z/scientific_freeze.json -- .venv/bin/python scripts/run_heldout.py freezes/LIO_GINS_R1_20261011T154403129394Z
```

That entry was run as20261011T154446522435Z_P5_ae13844a and completed all ten methods/eight conditions. Any new run is post-opening reproduction, not another independent test. It costs a full replay and can yield frontend numerical variation. It must not change P, Q/R, initialization, events or metrics. Source/config mismatches reject access; rebuilding the frozen runtime registry changes a frozen input and must not be passed off as unchanged blind evaluation.

## Interpretation, checks and preservation

Online estimators see only sensor/cache/initialization inputs; fault labels and reference trajectories are excluded. The separate initializer reads one reference epoch under the declared known-initial-state protocol. The MM/INS reference shares AT128; reported localNED errors are initial-position-conditioned, not absoluteWGS84/no-prior startup. Each original GNSS is updated at most once; differences and anchors are monitors, and KF-GINS posterior is never reinjected.

Original files are read-only; the frontend mounts only a single bag, never the dataset/reference directory, host home or Docker socket. Native frontend processing excludes preprocessing/callback/publication/wait, and cached-backend timing excludes the frontend. Same-bag frontend poses differed materially (3.601m local3D RMS) for an unresolved reason. Unflagged numerical LIO reset jumps can be propagated; the interface does not guarantee reset identification. Missing LIO spans produce failed output with visible coverage rather than hidden interpolation/reset.

```bash
.venv/bin/python scripts/record_run.py --phase P7 --purpose contract_tests --kind synthetic --input tests/test_final_contracts.py -- .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/record_run.py --phase P7 --purpose independent_metric_audit --input scripts/audit_final_metrics.py -- .venv/bin/python scripts/audit_final_metrics.py
.venv/bin/python scripts/record_run.py --phase P7 --purpose local_integrity --input scripts/verify_evidence.py -- .venv/bin/python scripts/verify_evidence.py
.venv/bin/python scripts/resume.py
```

The metric audit directly rereads raw trajectories/reference for all80 frozen pairs, independently of evaluator code. Resume reads state/Git/processes/receipts; live project jobs yield exit3 to prevent duplicates. `--audit-data` explicitly repeats raw-data auditing. Recorder `--input` accepts individual files, not directories. All experiments, failures, historical freezes and paper versions remain retained; immutable runs are never edited. Internal drafts and author materials are complete, with no submission manuscript/PDF because the incremental-evidence gate failed.

SHA is integrity, not backup: raw data have one local copy; off-site raw/numeric backup is unverified. No project remote or push. Old VPR, SSH, FlClash, drivers, global ROS/Python/networking are untouched. No sudo, account, paid service, academic authorship or formal submission was performed.
