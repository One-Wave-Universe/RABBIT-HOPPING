# Linux Visual Interface — Rabbit Hopping Physics Sandbox

Two ways to get the GUI on Linux:

## Option 1: AppImage (portable, no install)

1. Download `RabbitHoppingSandbox.AppImage` from the repo releases or raw file.
2. Make it executable:
   ```bash
   chmod +x RabbitHoppingSandbox.AppImage
   ```
3. Run:
   ```bash
   ./RabbitHoppingSandbox.AppImage
   ```

If it complains about missing libraries:
```bash
sudo apt install libgl1 libglib2.0-0 libxkbcommon0 libxcb-xinerama0
```

## Option 2: Build from source (recommended if you have Python)

```bash
git clone https://github.com/One-Wave-Universe/RABBIT-HOPPING.git
cd RABBIT-HOPPING
pip install numpy scipy
chmod +x sandbox/build_linux_app.sh
./sandbox/build_linux_app.sh
```

This produces `RabbitHoppingSandbox.AppImage` in the repo root.

## Option 3: Just run the script

```bash
python3 sandbox/physics_app.py
```

or use the launcher:
```bash
./sandbox/run_linux.sh
```

## Requirements

- Python 3.8+
- tkinter (usually `sudo apt install python3-tk`)
- numpy, scipy (`pip install numpy scipy`)

## What you get

Four live tabs:
- **CELL STACK** — BC-DC / TC-AC / QC-RC differentials, R27 target, magnetic hold, reinjection
- **MEMRISTOR** — pinched hysteresis V-I loop
- **QUADRATIC HOPFIELD** — recall from noise + energy surface
- **REINJECTION** — differential-triggered firing log

Still pure simulation. Still yellow. No hardware.
