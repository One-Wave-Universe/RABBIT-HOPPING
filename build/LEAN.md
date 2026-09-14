# Lean control (no extra ICs)

Balanced CENTER = both gates at the same voltage.
Lean = one gate up, the other down. D follows.
Parts that exist: two 10 k trimmers (or one dual pot).

## Bias

Do not use "both gates only on 100 k bleeds" as analog center. That is both OFF.
Analog center is both gates sitting near the same voltage in the 2N7000 on-slope (~2–3 V on a 5 V rail).

Keep the 100 k bleeds. Add pots in parallel as the control.

```
5V ---- RV_B 10k ---- GND     wiper → gate B
5V ---- RV_C 10k ---- GND     wiper → gate C
```

## How to use

1. Power 5 V. Both wipers mid (~2.5 V). Measure D. That is rest. Write it. It will not be 0.000 because Vth mismatch.
2. Turn RV_B up and RV_C down the same amount. D leans one way. That is up.
3. Reverse the two knobs. D leans the other way. That is down.
4. Return both to the same mid. D comes back toward rest. That is stay / balance.

One dual-gang pot wired opposite (CW raises B and lowers C) is the same lean on a single barrel.

## Do not

- Do not add an op-amp inverter to make a fancy single-ended lean. Extra step.
- Do not lean by tying CENTER to GND.
- Do not drive a gate past the 5 V rail.
- Pots are control. The ferrite is still hold. When you take 5 V away, D dies; Br should not if T5 passes.

## Log

Rest D at matched mid: ______
Lean B-up D: ______
Lean C-up D: ______
Back to mid D: ______
