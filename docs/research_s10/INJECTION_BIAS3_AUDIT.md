# B3m injection/error cancellation audit

All six routes plus separately labeled building00 repeat, all fixed3m and10m events and all19 policies. Each event90 IDs, each deleted interval30 IDs. Natural and disturbed rows match original ID/time/std; only position displacement changes. Reference/lever-arm rotation is offline only; no estimator, observation, weight or threshold modified. A3m displacement does not establish an actual3m absolute GNSS error.

|Route|Event|3m cancellation/90|Raw receiver RMSE|Injected receiver RMSE|10m cancellation/90|
|---|---:|---:|---:|---:|---:|
|building00|0|0/90|2.165477|4.178242|0/90|
|building00|1|0/90|4.548067|6.223461|0/90|
|building00|2|38/90|6.392721|6.227703|16/90|
|building00_repeat|0|0/90|2.165477|4.178242|0/90|
|building00_repeat|1|0/90|4.548067|6.223461|0/90|
|building00_repeat|2|38/90|6.392721|6.227703|16/90|
|parking00|0|27/90|41.756684|42.349322|22/90|
|parking00|1|28/90|12.701784|12.129171|24/90|
|parking00|2|0/90|1.552831|3.675627|0/90|
|building01|0|68/90|3.205761|1.694795|0/90|
|building01|1|65/90|18.883970|18.041966|26/90|
|building01|2|36/90|27.070336|27.933006|18/90|
|street00|0|0/90|0.666210|3.329250|0/90|
|street00|1|0/90|0.980110|2.448665|0/90|
|street00|2|0/90|1.046047|3.601827|0/90|
|playground00|0|0/90|0.716841|3.219162|0/90|
|playground00|1|0/90|1.662333|2.264321|0/90|
|playground00|2|42/90|1.465960|1.662074|0/90|
|building02|0|0/90|1.029597|3.281108|0/90|
|building02|1|0/90|0.631013|2.583197|0/90|
|building02|2|37/90|3.682967|3.368333|18/90|

Per-policy accepted and rejected actual-error distributions are in injection_acceptance_audit.csv; empty accepted/rejected groups are null, never0. Full per-original-ID labels are offline diagnostics only. Controlled injection acceptance is not natural fault-detection probability. Reference errors may correlate with GNSS; prior MM/INS also shares AT128. Known initialization and local alignment condition the receiver-error values. Cancellation requires route/event-specific interpretation; no cancellation-based case exclusion or retrospective tuning is allowed.
