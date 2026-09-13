# Linux Visual Interface — Rabbit Hopping Physics Sandbox

**Downloadable program (no AppImage bullshit that breaks):**

## Direct download (single file, just run it)

1. Download `physics_app.py`:
   https://raw.githubusercontent.com/One-Wave-Universe/RABBIT-HOPPING/main/sandbox/physics_app.py

2. Make it executable and run:
   ```bash
   chmod +x physics_app.py
   python3 physics_app.py
   ```

Or clone the whole repo:
```bash
git clone https://github.com/One-Wave-Universe/RABBIT-HOPPING.git
cd RABBIT-HOPPING
sudo apt update
sudo apt install -y python3 python3-tk python3-pip libgl1 libglib2.0-0 libxkbcommon0 libxcb-xinerama0
pip3 install --user numpy scipy
python3 sandbox/physics_app.py
```

## If you want a real AppImage (build it yourself)

```bash
chmod +x sandbox/build_linux_app.sh
./sandbox/build_linux_app.sh
```

This produces `RabbitHoppingSandbox.AppImage` in the repo root.

## Requirements

- Python 3.8+
- tkinter (`sudo apt install python3-tk`)
- numpy, scipy (`pip install numpy scipy`)

## What you get

Four live tabs:
- **CELL STACK** — BC-DC / TC-AC / QC-RC differentials, R27 target, magnetic hold, reinjection
- **MEMRISTOR** — pinched hysteresis V-I loop
- **QUADRATIC HOPFIELD** — recall from noise + energy surface
- **REINJECTION** — differential-triggered firing log

Still pure simulation. Still yellow. No hardware.
