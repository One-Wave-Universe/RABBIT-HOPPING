# Hardware build (body state first)

Simulation in `sandbox/` does not count as a cell.

Build order:

1. [CELL0.md](CELL0.md) — one mirror pair + square-loop core on CENTER
2. [M4_RING_MIRRORS.md](M4_RING_MIRRORS.md) — three mirrors, six hexes, one M4 loop
3. [FERRITE.md](FERRITE.md) — which core is hold vs EMI sponge
4. [LOG.md](LOG.md) — write measured D here or the cell is still paper

Score: design on paper ~42%. Hardware 0% until T3 is a millivolt number.
No extra comparator/latch chips. Available MOSFET voltage only.
Magnets on the board from the first solder.
