# Physics Sandbox

Expanded virtual breadboard with real physics constraints.

## Run
```bash
python sandbox/physics_sandbox.py
```

## What it tests
- **Memristor**: HP-style pinched hysteresis. State persists after power-off (magnetic hold).
- **Quadratic Hopfield**: quartic energy term prevents attractor collapse. Similar patterns stay distinct.
- **Reinjection loop**: fires only on differential drift, never on a timer.
- **Virtual breadboard**: netlist + constraint checker. Status GREEN/RED.

## Physics rules enforced
1. Memristor resistance bounded [Ron, Roff]. State w in [0, D].
2. Hopfield energy bounded below (Lyapunov). Quartic term keeps it from diverging.
3. Reinjection only when |D - target| > band.
4. No floating nodes. Every component pin maps to a defined node.

## Status
Software mirror: GREEN. All tests pass.
Physical cell: still YELLOW. This sandbox validates the math, not the hardware.
