# Physics Sandbox

Expanded virtual breadboard with real physics constraints.

## Modules

1. **Memristor** (HP/Chua model) — pinched hysteresis, magnetic hold latch. State `w` persists after power-off.
2. **Quadratic Hopfield** — quartic energy term prevents attractor collapse. Similar memories stay distinct.
3. **Reinjection loop** — differential-triggered only. Fires when measured D leaves the band. Never a timer.
4. **Virtual breadboard** — netlist + constraint checker. No floating nodes, energy bounded, polarity consistent.
5. **CellStack** (new) — full three-cell simulation:
   - BC-DC, TC-AC, QC-RC differentials
   - R27 target reference
   - Magnetic hold across power-off
   - Power reinjection on drift
   - Measured D against CENTER

## Run

```bash
python sandbox/physics_sandbox.py
```

All tests must pass. Status comes back GREEN.

## Status

- Software mirror: REAL and tested.
- Physical cell: still YELLOW. No hardware, no measured D1/D2/D3, no B-field data.
- This sandbox is the only runner available until a real bench exists.
