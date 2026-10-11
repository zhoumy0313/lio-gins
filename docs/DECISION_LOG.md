# Decision log

- 2026-10-11: Start architecture A in the new workspace. No project remote exists; local checkpoints only. No original data present. Preserve all supplied files.

- 2026-10-11 P1: Keep architecture A. No silent switch to GNSS/INS-only research; official demo is not robot-data evidence. No candidate search or holdout evaluation.
- Official demo reference has 2799 equal-time pairs with non-identical rows. Preserve raw input and failed health check; use first-row policy only for demo and report last-row sensitivity (horizontal RMSE 0.01220946 vs 0.01216766 m).
- AT128 logging timestamp differs from scan-end state: keep a separate instrumentation patch, applied only in copied build context. Compilation/replay pending.
- B6 must include an explicitly labeled local adaptation of known recovery covariance protection. Novelty unverified; no manuscript claims or author list.
- Public data access exhausted bounded probes. New Docker/system service requires user authorization under AGENTS/goal; all user actions consolidated once.

- P1 continuation 02: Verify original FAST-LIO CMake consumes generated Livox and Pose6D headers; add explicit exported-message target dependencies in a separate build patch. Reject changed prepared inputs before container build. No algorithm change, no new data/permissions, no heldout results. Same external blocker revalidated for the second consecutive goal turn.

- Third consecutive goal-turn blocking audit: actual raw/reference directories are empty, no runtime/derived image and no live project job. User action unchanged. Mark blocked rather than repeating automatic continuations or claiming P2–P7 completion; preserve full LIO-GINS-R1 scope and evidence gates.
