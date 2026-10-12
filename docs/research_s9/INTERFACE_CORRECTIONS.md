# Pre-precision S9 technical adaptation

All three bag identities match official hashes where audited; no precision opened. Street reference/trajectory contains one repeated first time; raw originals preserved. Stable first-row per timestamp used in offline reference interpolation and single-state initialization, declared before any route precision. No interpolation formula, KF or method parameters changed.

Playground reference starts198501, IMU198869.145107/GNSS198870; building02 reference181133, IMU181295.711679/GNSS181296. Choosing the first file row is outside sensor support. S9 selects one reference row at the earliest timestamp covered by first IMU, first valid GNSS and primary LIO cache. Reads only time until that row, one state payload; no accuracy-dependent row/caching selection. The S8-only first-row convention remains unchanged in historical S8. Event offsets relative to this common initialization; all21 events rechecked before collective freeze. Numeric shared initializer formulas/lever/Q/R/position KF unchanged.

Failures retained: street first strict monotonic audit exit1; playground and building02 literal first-row initializers exit1. Corrections are fully pre-freeze and pre-precision; whole matrices remain first prospective openings.
