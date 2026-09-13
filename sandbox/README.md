# Physics Sandbox

Expanded virtual breadboard with real physics constraints.

## Run headless (tests)

```bash
python sandbox/physics_sandbox.py
```

All tests pass. Pure simulation — no hardware.

## Run interactive app (GUI)

```bash
python sandbox/physics_app.py
```

No external dependencies. Uses tkinter (ships with Python) + numpy + scipy.

Four tabs:

- **CELL STACK** — live BC-DC / TC-AC / QC-RC differentials, R27 target, magnetic hold, differential-triggered reinjection. Run/pause, power off/on, reset.
- **MEMRISTOR** — pinched hysteresis V-I loop. Adjust amplitude and frequency, run test.
- **QUADRATIC HOPFIELD** — recall from noise, energy surface. Quartic term prevents attractor collapse.
- **REINJECTION** — differential D values, fire when |D| > band. No timer.

Status: SIMULATION ONLY. Yellow until real measurements.
