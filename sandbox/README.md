# RABBIT-HOPPING Physics Sandbox

Expanded virtual breadboard with real physics constraints.

## Files
- `physics_sandbox.py` — core models: Memristor, QuadraticHopfield, ReinjectionLoop, VirtualBreadboard, CellStack
- `physics_app.py` — interactive GUI (tkinter). Run: `python sandbox/physics_app.py`
- `headless_runner.py` — no-display runner. Run: `python sandbox/headless_runner.py`

## Status
SIMULATION ONLY. No hardware. Yellow until real measurements.

## Tests
`python sandbox/physics_sandbox.py` — all pass.
`python sandbox/headless_runner.py` — produces text visual snapshot.
