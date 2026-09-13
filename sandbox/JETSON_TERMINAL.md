# Jetson / Laptop Terminal Quick Start

Run the visual physics sandbox GUI from a terminal on Jetson Nano, Jetson Orin Nano, or any Linux laptop.

## 1. Get the code

```bash
git clone https://github.com/One-Wave-Universe/RABBIT-HOPPING.git
cd RABBIT-HOPPING
```

## 2. Install deps (Jetson / Ubuntu)

```bash
sudo apt update
sudo apt install -y python3 python3-tk python3-pip libgl1 libglib2.0-0 libxkbcommon0 libxcb-xinerama0
pip3 install --user numpy scipy
```

## 3. Run the GUI

```bash
python3 sandbox/physics_app.py
```

or the launcher:

```bash
chmod +x sandbox/run_linux.sh
./sandbox/run_linux.sh
```

## 4. If you have no display / SSH only

Use X11 forwarding or a VNC/NoMachine session. The app needs a graphical display (tkinter).

```bash
ssh -X user@jetson
python3 sandbox/physics_app.py
```

## 5. AppImage (portable, no Python install)

```bash
chmod +x RabbitHoppingSandbox.AppImage
./RabbitHoppingSandbox.AppImage
```

Still pure simulation. Still yellow. No hardware.
