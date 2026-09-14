# RABBIT-HOPPING

Reversible packet addressing and nested-rotation translator.

**Source identity stays fixed while the generated center moves.** Wrappers are opposite-parity neighbors. Operation order, polarity, orientation and route family are retained.

This is a **hypothesis**. The arithmetic is real and reversible. It does not prove nested physical rotations, scale transitions, or musical/planetary structure.

## Hardware build (body first)

Simulation is not the cell. Specific solder path:

- [`build/CELL0.md`](build/CELL0.md) — one mirror pair, square-loop core on CENTER, tests T1–T5
- [`build/M4_RING_MIRRORS.md`](build/M4_RING_MIRRORS.md) — three mirrors, six hexes, one M4 loop
- [`build/FERRITE.md`](build/FERRITE.md) — memory core vs EMI bead
- [`build/LOG.md`](build/LOG.md) — write measured D or the score stays 0% hardware

No extra comparator/latch. Magnets on the board from the first solder. Do not start the ring until Cell-0 T5 passes.

## Core packet

```text
(source_rank N, center T, wrapper W)
```

- N = orientation-dependent rank (stable source label + orientation flag kept separate)
- T = generated center = 2N + K (or other declared family)
- W = T-1 or T+1 (opposite parity)

## Status

- Established: reversible addressing, signed mirrors, memory rebuild engine (software), quadratic + latch models (software).
- Proposed: Cell-0 netlist, M4 ring, field/void polarity as winding sense.
- Hardware: YELLOW / 0% until LOG.md has a T3 millivolt number.
- Speculative: Point/Path/Field as physics; hex lattice as cortex map; software latch == ferrite remanence.
