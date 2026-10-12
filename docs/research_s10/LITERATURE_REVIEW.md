# Primary-source recheck, 2026-10-12

[FAST-LIO2](https://arxiv.org/abs/2107.06829), Xu et al., direct point-to-map LIO and incremental kd-tree. Existing fixed upstream frontend supplies local displacement; S10 changes no point-cloud estimator.

[i2Nav-Robot v3](https://arxiv.org/abs/2508.11485v3), Tang et al.; current title ends “Multi-Sensor Fusion Navigation.” S10 bibliography corrects the inherited older title locally; old bibliography preserved. Real AT128/ADIS/F9P originals plus artificial post-reacquisition injection are distinct from natural degradation.

[KF-GINS](https://github.com/i2Nav-WHU/KF-GINS), official EKF GNSS/INS implementation. Independent archived native comparator, never repeated posterior measurements in the position KF. No same-fault native results invented.

[WinTA-GIL](https://arxiv.org/abs/2607.04879v1), Feng et al.; windowed trajectory alignment and repeatable heading refinement under intermittent GNSS. Our alignment is fixed; only receiver-position admission changes. Temporal consistency and heading recovery precedent constrain novelty claims.

[Dual-ACKF](https://www.mdpi.com/2079-9292/15/10/2064), Shan et al., Electronics15(10):2064. Primary indexed article includes explicit GNSS bias state, slave innovation-energy noise adaptation and scenario-dependent update regulation; recovery covariance inflation relaxes quadratically. Thus gradual recovery weighting is prior work, not a new S10 contribution. Direct HTML/PDF attempts returned429/inaccessible; primary-domain search returned article metadata and method text, which suffices for these scope distinctions. No numerical SOTA comparison or reproduced accuracy claim.

[Dong et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC7014498/), Sensors20(2):561, published primary article. Sequential innovation-based Gaussian testing and robust adaptation of individual tightly coupled GNSS channels; our common receiver-position interface is looser and no raw satellite channel reconstruction is attempted.

[Huber1964](https://doi.org/10.1214/aoms/1177703732), inherited standard robust-estimation source. It supports the weighting comparator, not historical-anchor novelty.

A closed ScienceDirect outlier-rejection article could not be fully rechecked (403); it is not used to claim a mechanism or included just to increase reference count. Adjacent WinTA-GIL/Dual-ACKF/Dong are contextual sources, not executed SOTA methods. Strong experimental comparisons are the complete19 fixed local policies. Algorithm novelty remains unproved. Publication assessment: a narrow event case with measurable control differences; acceptance is a human decision.
