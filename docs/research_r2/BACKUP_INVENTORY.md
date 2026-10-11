# Preservation and partial backup inventory

All R1 and R2 local inputs, failures, intermediate runs and paper versions are retained. No raw data, old outputs, old code or old paper was deleted. The old VPR workspace and global ROS/Python/SSH/network/driver settings were not modified.

| Material | Local | Authorized Git remote | Verified separate offsite copy |
|---|---|---|---|
| R1/R2 tracked source, fixed configs and protocols | Preserved | Pushed on existing R1/R2 branches | Git remote only |
| R1/R2 papers and R2 vector sources | Preserved | R2 source/PDF/bibliography/figure package pushed | Git remote only |
| Lightweight summaries, points, compressed event provenance, tests, real command/log/commit receipts | Preserved | R2 artifacts pushed | Partial evidence archive only |
| Original building00/parking00 data (~75GB) | Preserved, read-only, exact SHA audited | Excluded | **Not verified** |
| Full old outputs (~29GB), full R2 outputs (~1.8GB before closing audits) | Preserved, append-only new runs | Excluded; lightweight extracts only | **Not verified** |
| Frontend caches, isolated Noetic rootfs, binaries/build/bundle caches | Preserved locally | Identity/patch records only | **Not verified** |
| building01 | Missing | Not uploaded | Missing |

Sizes are approximate snapshots, not a quota guarantee; closing audits add small files. The audit records current free disk and requires at least80GiB. Neither a SHA digest nor a Git receipt substitutes for backup of excluded payloads. No raw-dataset redistribution, cloud storage purchase or new account was attempted. A human may arrange a licensed offsite backup separately; this is not required to review the delivered PDF but matters for long-term numerical reproduction.
