# Hardware build (body state first)

Simulation in `sandbox/` does not count as a cell.

**No entanglement.** Two cells share a wire, a CENTER, a current, or a receipt. That is connection. It is not spooky pairing. If one side is not connected by a net you can point at, it is not in the circuit.

Build order:

1. [CELL0.md](CELL0.md) — one mirror pair + core on CENTER
2. [LEAN.md](LEAN.md) — pots / Ys, lean from mid
3. [M4_RING_MIRRORS.md](M4_RING_MIRRORS.md) — three mirrors, six hexes, one M4 loop
4. [FERRITE.md](FERRITE.md) — which core is hold vs EMI sponge
5. [LOG.md](LOG.md) — write measured D or the cell is still paper

Score: design on paper. Hardware 0% until T3 is a number in LOG.md.
No extra comparator/latch chips. 5 V rail. Magnets on the board from the first solder.
