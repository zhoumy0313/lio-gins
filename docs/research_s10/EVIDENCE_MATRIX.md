# A evidence matrix

Read-only recomputation from archived trajectories and raw accepted logs, full inherited10Hz grids, all six routes plus a separately labeled same-bag repeat, all19 policies. No new frontend/backend run or tuning. S10 is post-hoc and does not replace original10m primary evaluation.

1197 event/case/method records; largest independent RMSE discrepancy 0m. Every source/config/cache/init/input/trajectory/log/reference identity retained in manifest.json. P/no-anchor config differs only method dispatch, whose sole relevant mechanism switch is use_anchor; data, initial state, cache and alignment are equal.

|Route|P3m macro|No-anchor|Fraction improvement|Natural/cap|Clean max|Qualified|
|---|---:|---:|---:|---|---|---|
|building00|2.967860383|3.263186868|0.090502474|2.584656605/2.589027320|7.0|True|
|building00_repeat|2.760111331|3.050126142|0.095082891|2.070368947/2.120218422|7.0|True|
|parking00|2.297382010|3.086813425|0.255743159|2.362052061/2.412021851|7.0|True|
|building01|1.867700868|1.867700868|0.000000000|5.273450323/5.055153848|7.0|False|
|street00|2.032243524|2.607561540|0.220634492|1.673050771/1.705700274|7.0|True|
|playground00|6.597319194|5.401391277|-0.221411088|5.935492604/3.204760172|142.0|False|
|building02|10.122215883|4.653152280|-1.175345932|6.498460468/3.452104599|None|False|
