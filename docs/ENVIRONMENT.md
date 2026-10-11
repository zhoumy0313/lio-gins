# P0 environment audit — 2026-10-11

Workspace: `/home/aaron/lio_gins`; independent Git branch `research/lio-gins-r1`. No remote. Supplied files are preserved and hashed in `artifacts/initial_workspace.json`.

Ubuntu 22.04 kernel 6.8, Intel i7-12700H (20 logical CPUs), 15 GiB RAM (about 12 GiB available), no swap. Filesystem has 325 GiB available. Keep at least 80 GB free; actual dataset sizes must be checked before large downloads. Build concurrency limit: 4.

Python 3.10.12, CMake 3.22.1, GCC 11.4.0, Git 2.34.1. CUDA/GPU is informational only. Docker and Podman executables are absent (individual audit exit codes 127). Neither is installed or started by this task.

System Python lacks pip and ensurepip; a normal venv creation failed. A project venv uses `--without-pip --system-site-packages` to read existing scientific packages without changing global Python. This is an environment limitation to record, not a reason to install system packages. Versions will be locked before backend use.

Evidence: `outputs/20261011T050426113275Z_P0_163c0131/environment.json`; actual audit commands and individual exit codes are inside it. Audit recorder exit: 0. CPU experiments can proceed; isolated ROS build awaits a usable container runtime.

Git has no configured author identity. Local commits use `Codex checkpoint <codex@localhost>` solely as tool attribution; this does not assign scientific authorship. No global Git configuration is changed.
