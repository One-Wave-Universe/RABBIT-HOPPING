# RABBIT-HOPPING

Reversible packet addressing and nested-rotation translator.

**Source identity stays fixed while the generated center moves.** Wrappers are opposite-parity neighbors. Operation order, polarity, orientation and route family are retained.

This is a **hypothesis**. The arithmetic is real and reversible. It does not prove nested physical rotations, scale transitions, or musical/planetary structure.

## Core packet

```text
(source_rank N, center T, wrapper W)
```

- N = orientation-dependent rank (stable source label + orientation flag kept separate)
- T = generated center = 2N + K (or other declared family)
- W = T-1 or T+1 (opposite parity)

Positive example (A, normal rank 1, center 4):

```text
(1, 4, 3)
(1, 4, 5)
```

Negative mirror:

```text
(-1, -4, -3)
(-1, -4, -5)
```

## Four operation-order families

- A: T = 2N + K
- B: T = 2(N + K)
- C: T = N/2 + K
- D: T = (N + K)/2

Equal destinations must retain distinct route identity.

## Music adapter

12-label domain (A=1 ... G#=12). Labeling only. No frequency, octave or Circle-of-Fifths claims baked in.

## Nested rotation (speculative)

`hierarchy_transition()` tags a packet as point/path/field. Requires explicit level, parent and branch. Arithmetic alone does not rotate anything.

## Memory rebuild / recall

`memory_rebuild.py` turns the reversible routes into an actual recall engine:

- store constellations (overlapping feature sets)
- present a partial cue
- traverse recorded rabbit-hop neighborhood (2N +/- 1 connectors)
- run Hopfield-style associative completion
- run Boltzmann-style probabilistic fill only when ambiguity remains (marked uncertain)
- validate against current context / state machine
- emit a compact rebuild receipt (cue, route, mirrors, completion, fill, validation)

## Quadratic memory + memristor hold + reinjection (new)

`quadratic_memory.py` adds the three pieces the cell needs:

- **Quadratic memory state**: higher-order energy term so similar memories separate instead of collapsing. Linear Hopfield saturates; quadratic capacity term fixes it.
- **Memristor magnetic hold**: software latch with hysteresis + remanence. State survives power-off (passive magnetic retention), distinct from dynamic refresh.
- **Power reinjection loop**: differential-triggered feedback. Observes measured D; reinjects only when it leaves the allowed band. Trigger = measured differential, never a timer.

Integrated as `QuadraticCell`: quadratic attractor + latch + reinject loop. Tests cover separation, hold-after-power-off, differential trigger, and invertibility.

## Status

- Established: reversible addressing, shared wrappers between centers two apart, signed mirrors, branch ambiguity on missing metadata, 12-label adapter, working memory rebuild engine, quadratic separation + magnetic-hold latch + differential reinject (software).
- Proposed: candidate state record, Point/Path/Field reading, memory rebuild flow, quadratic/memristor/reinject layer.
- Speculative: multiplication = outward field transition; wrappers close loops; same numbers describe music or planets; software latch == physical memristor.

See `rabbit_hopping.py` for the model + tests.
See `memory_rebuild.py` for the recall engine + tests.
See `quadratic_memory.py` for quadratic state + memristor hold + reinject + tests.
See `cards/RABBIT-HOPPING.md` for the catalog card.
See `QUADRATIC_MEMRISTOR_HOLD_REINJECT.md` for the architecture note.
