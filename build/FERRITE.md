# Which ferrite

The loop shape, not the color of the bead.

## Use for hold (on CENTER / spoke)

- Bag or datasheet says **square loop**, **memory core**, or **magamp**
- High Br/Bsat (squareness near 1)
- Half-current must not flip (dead zone = |H| < Hc)
- Surplus 1 mm-class memory toroids (example flip ~0.3 A·turn) or magamp cores
- Fair-Rite 85-class / manganese square-loop only after you see a BH plot

## Reject (forgets when current dies)

- EMI / clamp / USB cable beads (Fair-Rite 43, 61, …)
- PSU yellow/white inductor toroids
- AM ferrite rods
- Any core with only µi and no Br/Hc

Soft loop = inductor. Square loop = memory.

## Bench check

1. One turn of Cell-0 CENTER or drain through the core.
2. T3 one way. Rails off.
3. Sense turn to scope, or Hall / compass.
4. Reverse drive (T4). A flip pulse on the sense turn means remanence existed.

No leftover field and no reverse pulse → wrong ferrite or H never beat Hc. Do not add a driver chip to hide that.
