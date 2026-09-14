# M4 ring mirrors

Three mirror pairs around one loop. Six hexes. Magnets on the board.

Do not start this file as hardware until CELL0.md T5 has a pass in LOG.md.

## Object

- **M4** = middle closed path. CENTER + shared timing. Not a fourth brain IC.
- **Six hexes** on the ring: H1..H6
- **Three mirrors** = opposite hexes:
  - A: H1 ↔ H4
  - B: H2 ↔ H5
  - C: H3 ↔ H6
- **Polarity** of a spoke: **+ field** or **− void** (winding sense / remanence well)
- **Ternary** on that connection: **up / down / stay**

Polarity chooses which well. Ternary chooses whether the page turns.

```
          H1
       /      \
    H6          H2
      \   M4   /
    H5          H3
       \      /
          H4
```

## Frozen choices (change here if you change the board)

- Opposite hexes are the mirror (not adjacent).
- Field/void is **per pair** by winding sense, not a CPU enum.
- Prefer **one square-loop core per spoke** so one mirror cannot scramble the other two.
- First ring may use **one shared core on M4** only as a bring-up. If mirror A moves and B forgets, shared core is rejected.

## Netlist (three Cell-0 pairs, common M4)

Each pair is CELL0.md copied:

- Pair A: Q1A/Q2A, drains DBA/DCA, gates BA/CA, core CA on spoke A into M4
- Pair B: same
- Pair C: same
- All sources (or spoke returns) land on **one M4 node / ring wire**
- M4 is not power GND

VCC and GND are common. Bleeds on every gate.

## Ring tests (after each pair has its own T3)

**R1** Pair A T5 still true while pair B is idle.

**R2** Move pair B (T3/T4). Pair A remanence unchanged. Fail = M4 is a short, not a ring.

**R3** Third pair. Same isolation.

**R4** Name hexes on the board. Opposite names = one mirror.

**R5** Assign field/void per pair by winding. Write it. Do not rename in software.

## Agreement vs differential

- On a spoke: D / Br **is** the new live state.
- On M4: accept only if the other mirrors still close the ring and N / family / field-void map were not overwritten.

Matching a number is not matching a complete state.

## What this is not

- Not six binary chips called ternary
- Not quadratic memory
- Not grid cells
- Not muscle-map-brain collapsed into one FET

Body (this ring) first. Tiled rings later = field/map. Recall later = brain-side.
