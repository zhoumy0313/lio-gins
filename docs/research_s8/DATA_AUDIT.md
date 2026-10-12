# Building01 data and interface audit

Five required originals verified read-only; official bag SHA matches 60931a01...b257. Text hashes are local identity only. No positioning performance was read or computed.

| Input | Bytes | SHA-256 |
|---|---:|---|
| building01.bag | 44769652530 | `60931a01bbc0eb05154e895349be24212cb43b6c795c4c91cbb801c7db73b257` |
| building01_ADIS16465_IMU.txt | 34159216 | `79d11bae567779eb979db89541bbec8caefa358f0231999458b16d2d581904e4` |
| building01_F9P_GNSS.pos | 140300 | `66d275ed1ef55c434a9e6327ded768cf2b71f4209d1543e2bfb0635eda9d1cb4` |
| building01_groundtruth.nav | 22725759 | `d38a7e0223f34a0305d05b91295cf038a8ba08356a45b68b622c95d2c9fefd8d` |
| building01_trajectory.csv | 22398457 | `8e2e34e7f1308239ccceab6914a8a62a62aad4ff5158ba79d949b3a9d38c7342` |

Independently observed GPS week 2364; GPS−UTC=18 seconds. Raw text, including the eight-column trajectory, uses SOW. Standard/custom IMU streams begin at different row indices: timestamp pairing is required, not index pairing. Custom increments and ADIS text agree to <1e−8; no second dt multiplication.

Reference time support is [10681.0004, 12049.986]; raw bag span is 1524.650107s. All 21 fixed events support all five 10/30/60/90/180s windows. Reference states beyond the unique first initializer row remain unused until the pushed scientific freeze.

F9P bag/text LLH and NED standard deviations match; text timestamp rounds to 0.001s, so the declared serialization half-step bound is 0.0005s. Measured residual is recorded in extra_interfaces.json; no observation time is shifted. PointCloud2 AT128 has packed x/y/z/intensity/ring/float64 timestamp fields, 160000 points in bounded samples; monotonic point timestamps and body IMU interfaces verified.

Existing rootless Noetic rosbag info succeeded, exit0. Only one full native1x FAST-LIO frontend is registered, currently running without truth comparison. Reused binary and launch/config are verified; no Docker reinstall, global Python/ROS/driver changes, or home mount.

Retained technical failures: first audit incorrectly paired IMU streams by row index; corrected to exact time matching. First GNSS check used a1µs bound despite3-decimal text; corrected to serialization half-step with actual residual retained. Neither failure read positioning error or changed method parameters.

Sources: outputs_s8/20261012T043425810224Z_A_008eb0d3, ...A_05c52768 (isolated rosbag info), ...A_30c981ed (F9P/schema), ...A_a36aee85 (unique initial state), ...A_facd25d4 (fixed observed perturbations). Full logs and failures retained in RUN_REGISTER.csv. Official source: https://github.com/i2Nav-WHU/i2Nav-Robot/blob/main/sha256sum/sha256sum.json.
