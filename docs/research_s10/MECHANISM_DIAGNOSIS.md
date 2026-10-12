# C event-level mechanism diagnosis

Existing logs only; all3m/10m/clean events, all19 policies, six routes and a separate same-bag repeat. Actual per-ID paired decisions, source coordinates and output clocks retained. S10 is post-hoc exploratory.

P/no-anchor is the single-factor comparison. P and actual NIS0 have different posterior histories; a hypothetical NIS decision from P nominal NIS is not substituted for the actual NIS0 log. Constant injected displacement cancels to numerical precision for5s pairs entirely inside each bias interval; this mathematical identity alone is not field fault detection evidence.

|Route/case/event|P−no-anchor90m|Extra rejected|Also NIS0 accepted|Direct anchor veto|Veto while short score good|Prior position difference m|Max offline relative LIO error m|
|---|---:|---:|---:|---:|---:|---:|---:|
|building00/loss30_bias3/0|-0.857788519|82|80|88|85|0|1.0497263406410933|
|building00/loss30_bias3/1|-0.023992895|0|0|0|0|0.0615128499|1.4466510371747416|
|building00/loss30_bias3/2|-0.004198038|5|5|8|5|1.21391754e-05|2.7712184487092517|
|building00_repeat/loss30_bias3/0|-0.887247280|82|80|89|85|0|1.0300930649476436|
|building00_repeat/loss30_bias3/1|-0.002975601|0|0|0|0|0.0136695943|1.2375370754262311|
|building00_repeat/loss30_bias3/2|0.020178450|7|7|11|7|2.50385266e-06|0.9093039783452211|
|parking00/loss30_bias3/0|0.000000000|0|0|1|0|0|1.714296738729259|
|parking00/loss30_bias3/1|-1.803255371|55|3|60|55|0|3.285260768488088|
|parking00/loss30_bias3/2|-0.565038875|83|33|90|85|0.0272173505|2.417427246843601|
|building01/loss30_bias3/0|0.000000000|0|0|0|0|0|0.53830024658985|
|building01/loss30_bias3/1|0.000000000|0|0|0|0|0|0.32456226071226135|
|building01/loss30_bias3/2|0.000000000|0|0|0|0|0|1.4472111804946752|
|street00/loss30_bias3/0|-1.476582391|71|62|76|71|0|1.2582561074719931|
|street00/loss30_bias3/1|-0.249146705|76|76|76|76|0.0012130814|1.3389076217124336|
|street00/loss30_bias3/2|-0.000224952|0|0|0|0|0.00138794353|3.5110194494796896|
|playground00/loss30_bias3/0|0.185796427|83|83|90|85|0|4.342049707688887|
|playground00/loss30_bias3/1|-1.823696039|11|0|16|11|5.9624192|3.8773858972303925|
|playground00/loss30_bias3/2|5.225683362|77|0|90|85|0.0310681989|13.115046652984923|
|building02/loss30_bias3/0|1.123490463|83|0|90|85|0|3.6289401446059966|
|building02/loss30_bias3/1|6.822946753|83|0|90|85|13.0028101|11.527520621354007|
|building02/loss30_bias3/2|8.460753595|77|0|90|85|15.441203|19.931214966265976|

Anchor decomposition is checked exactly: current receiver error minus anchor receiver error minus relative LIO error equals anchor residual. These reference-derived terms are offline explanations, never online scores or qualification. Receiver/anchor errors and reference inaccuracies can correlate, so no single global cause is established by RMSE. Actual healthy-cache flags can coexist with poor relative motion/old anchors; points/plane residual do not certify absolute drift. No truth-free reliable applicability classifier or new threshold is fitted.

All street00 events, including its nearly neutral Event2, remain. Fixed representative timelines are street00 Event0 and building02 Event1, as declared before reconstruction; full other events/logs are retained. No-decay is not asserted necessary.10m NIS/P near-tie and both negative routes are retained. Per-ID additional rejection and direct veto are distinct: veto can also change later qualification and filtering histories. Events within a route are dependent, not IID.

## Focused interpretation from actual logs

street00 Event0: P accepted intervals after return [[25.0, 36.0]]; direct-anchor-veto intervals [[0.0, 22.0], [37.0, 89.0]]. First return anchor score=6.179873216771114, age=31.0, anchor receiver offline error=0.5908424374546842m, relative LIO offline error=0.1567112561341604m.

street00 Event1: P accepted intervals after return [[7.0, 13.0]]; direct-anchor-veto intervals [[14.0, 89.0]]. First return anchor score=3.3167143606450122, age=31.0, anchor receiver offline error=0.7073225561729585m, relative LIO offline error=0.39685860712220894m.

street00 Event2: P accepted intervals after return [[7.0, 89.0]]; direct-anchor-veto intervals []. First return anchor score=0.7349594409276552, age=31.0, anchor receiver offline error=0.434446810055448m, relative LIO offline error=1.7963850944728412m.

Event0 begins with exactly equal P/no-anchor positions: anchor veto rejects observations despite passing short-window motion consistency, and62 extra-rejected IDs were actually accepted by strict NIS0. Its1.476582m error reduction is not injection cancellation (street all0/270). Event1 shows76 additional rejections and0.249147m reduction, with an already1.213mm prior-state difference. Event2 has zero extra rejection/veto; its0.000225m change is a carryover numerical/history difference, not a new anchor-detection success. Three events are dependent.

The adverse routes also show anchor veto while logged local health is verified. On clean building02 Event2 P/no-anchor agree before the outage, yet90 anchor vetoes coincide with a clean180s-censored admission and offline relative LIO error up to14.681994m; on clean playground Event1 the prior positions also agree and the post90 penalty is4.502991m. These controlled log contrasts support a failure mechanism, not a calibrated truth-free applicability rule. Offline decomposition identifies relative-motion and anchor-error terms; reference correlations still limit physical causal attribution. In biased building02 Event1, prior P/no-anchor positions already differ13.002810m, so that event alone is not a fresh independent anchor experiment.
