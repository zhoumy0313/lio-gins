# D strong-baseline fairness review

All19 policies retained, no service/cost filtering in raw comparisons. Qualification independently matches inherited summaries; strict NIS thresholds11.3448667301/16.266236/30 verified, B4 is the wider100 gate. All six routes plus separately labeled same-bag sensitivity included. Actual biased-return admissions are distinct from clean first admission and availability-bound clocks. No new parameter search or posterior injection.

|Route|Best standard raw3m|P3m|P qualified|Best qualified including ablations|
|---|---|---:|---|---|
|building00|B2 1.772961435|2.967860383|True|P_without_decay|
|building00_repeat|B2 0.696059914|2.760111331|True|Clock10|
|parking00|B2 2.226471750|2.297382010|True|NIS0|
|building01|B2 1.325268593|1.867700868|False|B3|
|street00|Clock60 2.325368272|2.032243524|True|P_without_decay|
|playground00|B3 4.162229155|6.597319194|False|B3|
|building02|B3 2.865917892|10.122215883|False|B3|

|Street00 policy|3m90m|180m|Clean actual each s|Bias actual each s|Accepted/270|Qualified|
|---|---:|---:|---|---|---:|---|
|B2|3.062290475|3.029032800|[null, null, null]|[null, null, null]|0/270|False|
|B3|2.766421500|2.244102003|[0.0, 0.0, 0.0]|[0.0, 0.0, 0.0]|270/270|True|
|B4|2.766421500|2.244102003|[0.0, 0.0, 0.0]|[0.0, 0.0, 0.0]|270/270|True|
|B5|2.759905181|2.241201785|[0.0, 0.0, 0.0]|[0.0, 0.0, 0.0]|270/270|True|
|B6|2.649742790|2.172484847|[2.0, 2.0, 2.0]|[2.0, 2.0, 2.0]|264/270|True|
|NIS0|2.647273864|2.171017327|[0.0, 0.0, 0.0]|[16.0, 0.0, 0.0]|254/270|True|
|NIS1|2.766421500|2.244102003|[0.0, 0.0, 0.0]|[0.0, 0.0, 0.0]|270/270|True|
|NIS2|2.766421500|2.244102003|[0.0, 0.0, 0.0]|[0.0, 0.0, 0.0]|270/270|True|
|Clock2|2.607520753|2.146565989|[7.0, 7.0, 7.0]|[7.0, 7.0, 7.0]|249/270|True|
|Clock5|2.585096173|2.132940338|[10.0, 10.0, 10.0]|[10.0, 10.0, 10.0]|240/270|True|
|Clock10|2.551917429|2.112937834|[15.0, 15.0, 15.0]|[15.0, 15.0, 15.0]|225/270|True|
|Clock15|2.521764702|2.094919271|[20.0, 20.0, 20.0]|[20.0, 20.0, 20.0]|210/270|False|
|Clock30|2.439798069|2.046546723|[35.0, 35.0, 35.0]|[35.0, 35.0, 35.0]|165/270|False|
|Clock60|2.325368272|1.962631384|[65.0, 65.0, 65.0]|[65.0, 65.0, 65.0]|75/270|False|
|Clock90|2.388010586|2.052834785|[95.0, 95.0, 95.0]|[95.0, 95.0, 95.0]|0/270|False|
|P|2.032243524|1.689730366|[7.0, 7.0, 7.0]|[25.0, 7.0, 7.0]|102/270|True|
|P_without_motion|2.649742790|2.172484847|[2.0, 2.0, 2.0]|[2.0, 2.0, 2.0]|264/270|True|
|P_without_anchor|2.607561540|2.258046495|[7.0, 7.0, 7.0]|[7.0, 7.0, 7.0]|249/270|True|
|P_without_decay|2.001474694|1.677726654|[7.0, 7.0, 7.0]|[25.0, 7.0, 7.0]|102/270|True|

The narrow street003m comparison supports a descriptive local advantage over all tested standard policies, including unqualified long waits, at unchanged service/cost gates. It does not beat no-decay, and parking00 strict NIS and building00 long wait remain stronger raw counterexamples. The third street event is nearly neutral.10m street NIS/P tie, building01 cost failure, and both S9 adverse routes remain. Events and repeated caches are dependent; no IID p values or population-generalized superiority.

S10 is a post-hoc focus after these routes were opened. It does not change R1 NO_ADDITIONAL_GAIN or earlier10m joint-failure flags. E1 completes read-only mechanism reconstruction; E2 amplitude search and E3 independent confirmation deferred, E4 prohibited. A new confirmatory test requires a separate pre-access protocol and unseen data.
