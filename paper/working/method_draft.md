# Method draft — internal, no efficacy claim or submission text

The system uses the pinned i2Nav AT128/ADIS adaptation of FAST-LIO2 for local motion. A three-dimensional linear position KF propagates local increments through a fixed initial frame rotation. F9P receiver position updates use the current attitude to compensate the antenna lever arm. KF-GINS remains an independent GNSS/INS comparator. Its posterior is never injected into the position KF.

The common robust update combines a Huber position update and finite post-gap covariance protection. The proposed admission manager compares receiver displacement against independently propagated local antenna displacement. Missing local diagnostic support invokes the mature recovery rule and marks evidence unresolved. It does not automatically label the GNSS faulty.

The final development revision stores a previously admitted, continuously rule-qualified raw receiver observation and the corresponding local antenna position. During gap-triggered reacquisition, it compares the new receiver position with the anchor advanced by local motion. The anchor is retained through isolation and recovery. The comparison determines admission only; neither the difference nor the anchor creates a second KF measurement. Covariance normalization includes receiver endpoint covariances and an engineering local uncertainty growth term.

This construction does not identify which sensor is wrong when local drift and receiver bias yield the same observations. Qualification is an operational rule rather than proof of absolute position accuracy. No reference trajectory or artificial fault label enters the online score or weight. The controlled initialization consumes one reference epoch and is disclosed separately from operational startup.

The development protocol fixes a common normal-condition cost, event macro metric, and three-revision search budget. Candidate results are conditional on common immutable local-motion caches. Mandatory ablations and the preserved second frontend cache determine whether any observed gain can be attributed and repeated. No heldout result or efficacy abstract is included in this draft.

References: FAST-LIO2 (Xu et al., 2022), pinned i2Nav-Robot-Baseline, KF-GINS (Niu et al., 2025), WinTA-GIL (arXiv:2607.04879v1), and Dual-ACKF (Electronics 15(10):2064, 2026). The latter systems are neighboring work, not reproduced implementations. See docs/METHOD_SPEC.md and docs/RELATED_WORK_MATRIX.md for exact scope and verification limits.
