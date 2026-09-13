# Quadratic Memory State + Memristor Magnetic Hold + Power Reinjection Loop

Status: **PROPOSED STRUCTURE** (software model + tests). Not physical hardware. Not proven cell behavior.

This extends the Rabbit Hopping memory rebuild engine with the three missing pieces you named:

1. **Quadratic memory state** — richer than linear Hopfield overlap. Uses a quadratic energy / activation term so similar-but-distinct memories separate instead of collapsing.
2. **Memristor magnetic hold** — a software model of a non-volatile resistive/magnetic latch that holds state after drive is removed (hysteresis / remanence). Distinct from dynamic refresh.
3. **Power reinjection loop** — differential-triggered feedback that observes decay and reinjects only when the measured state leaves the allowed band. Trigger = measured differential, not elapsed time.

These map directly onto the balanced-cell architecture notes (passive magnetic retention vs dynamically maintained reinjected state) without pretending the software is the physical cell.

## Separation rules (do not collapse)

- Quadratic state = the *memory energy landscape* (attractors, separation).
- Memristor hold = the *storage medium* (non-volatile latch, hysteresis).
- Reinjection loop = the *maintenance mechanism* (feedback, threshold, restore).
- Rabbit hopping = the *route/coordinate* used to navigate and rebuild.
- Hopfield/Boltzmann in `memory_rebuild.py` = the original completion/fill engines. This module adds the quadratic + hold + reinject layer on top.

## Core model

### Quadratic energy

For a state vector `s` (bipolar or feature-overlap) and weight matrix `W`:

```text
E(s) = -0.5 * s^T W s  - 0.25 * lambda * (s^T s)^2   + bias terms
```

- Linear term: classic Hopfield attractor.
- Quadratic term (`lambda > 0`): penalizes dense/collapsed states, improves capacity and separation of similar patterns (inspired by quadratic Hadamard / higher-order associative memory ideas).
- Dynamics: asynchronous or synchronous update that descends E.

### Memristor magnetic hold (software latch)

Each memory cell has a latch:

```text
state_logical : +1 / -1 / 0 (HOLD)
R_memristor  : resistance proxy (high = retained 0/1, low = volatile)
hysteresis   : threshold band that must be crossed to flip
remanence    : whether state survives after drive removed
```

- Write: set logical state + update R.
- Hold: after drive removed, logical state persists if remanence=True (passive magnetic retention).
- Read: non-destructive in this model (real core memory is destructive; we model the *hold* property, not the full physics).

### Power reinjection loop

```text
observe measured_differential D
if |D - D_target| > band:
    reinject (restore toward target)
else:
    idle (no power waste)
```

Trigger is the **measured differential**, never a timer. This matches the architecture rule: reinjection trigger = measured differential state.

## Files

- `quadratic_memory.py` — model + tests (this commit).
- Integrated into `run_all.py`.
- Updates to README + card.

## What this does NOT claim

- No physical memristor, no real magnetic core, no measured B-field.
- No claim that quadratic energy = nested rotation.
- No claim that reinjection = cell life. It is a maintenance loop model.

## Next physical step (outside this repo's execution)

Build the first BC-DC differential, measure D1 against CENTER, then add a real memristor/magnetic latch and a differential-triggered reinject circuit. Software here is the mirror, not the proof.
