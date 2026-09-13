# Physics Sandbox

Expanded physics sandbox with real constraints:

- `physics_sandbox.py` — headless tests (memristor, quadratic Hopfield, reinjection, CellStack, virtual breadboard)
- `physics_app.py` — interactive GUI (tkinter + numpy + scipy)
- `headless_runner.py` — runs the same models without a display
- `build_linux_app.sh` — builds a portable Linux AppImage
- `run_linux.sh` — quick launcher
- `LINUX_APP.md` — download and run instructions

## Run GUI
```bash
python3 sandbox/physics_app.py
```

## Build AppImage (Linux)
```bash
./sandbox/build_linux_app.sh
```

## Headless test
```bash
python3 sandbox/headless_runner.py
```

Status: SIMULATION ONLY. Yellow until real measurements.
