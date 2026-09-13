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

## Status

- Established: reversible addressing, shared wrappers between centers two apart, signed mirrors, branch ambiguity on missing metadata.
- Proposed: candidate state record, Point/Path/Field reading.
- Speculative: multiplication = outward field transition; wrappers close loops; same numbers describe music or planets.

See `rabbit_hopping.py` for the model + tests.
See `cards/RABBIT-HOPPING.md` in Great-Galactic-Library for the catalog card.
