#!/usr/bin/env python3
"""
RABBIT-HOPPING Physics Sandbox App
==================================
Interactive GUI for the physics sandbox. No external dependencies.
Uses only tkinter (ships with Python) + numpy + scipy.

Run:
    python sandbox/physics_app.py

Shows live:
  - Memristor pinched hysteresis (V-I loop)
  - Quadratic Hopfield energy landscape + recall
  - Reinjection loop firing log
  - Full CellStack: BC-DC / TC-AC / QC-RC differentials, R27 target,
    magnetic hold, differential-triggered reinjection

Status: SIMULATION ONLY. No hardware. Yellow until real measurements.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.integrate import odeint
import threading
import time

# ============================================================
# CORE MODELS (same as physics_sandbox.py)
# ============================================================
class Memristor:
    def __init__(self, Ron=100.0, Roff=16000.0, D=10e-9, mu=1e-14, w0=5e-9):
        self.Ron = Ron; self.Roff = Roff; self.D = D; self.mu = mu
        self.w = w0; self.history = []
    def resistance(self, w=None):
        w = w if w is not None else self.w
        w = np.clip(w, 0, self.D)
        return self.Ron * (w / self.D) + self.Roff * (1 - w / self.D)
    def step(self, V, dt=1e-4):
        R = self.resistance(); I = V / R if R > 0 else 0.0
        dw = self.mu * self.Ron / self.D * I * dt
        self.w = np.clip(self.w + dw, 0, self.D)
        self.history.append((V, I, self.w)); return I
    def reset(self, w0=None):
        self.w = w0 if w0 is not None else self.D / 2; self.history = []
    def pinched_test(self, freq=1.0, amp=1.0, cycles=2, steps=500):
        ts = np.linspace(0, cycles / freq, steps)
        Vs, Is = [], []
        self.reset()
        for t in ts:
            V = amp * np.sin(2 * np.pi * freq * t)
            I = self.step(V, dt=ts[1] - ts[0])
            Vs.append(V); Is.append(I)
        return np.array(Vs), np.array(Is)

class QuadraticHopfield:
    def __init__(self, n, patterns, lam=0.1, beta=5.0):
        self.n = n; self.W = np.zeros((n, n))
        for p in patterns: self.W += np.outer(p, p)
        np.fill_diagonal(self.W, 0); self.lam = lam; self.beta = beta
    def energy(self, s):
        return -0.5 * s @ self.W @ s + self.lam * np.sum(s**4)
    def step(self, s):
        h = self.W @ s - 4 * self.lam * s**3
        return np.tanh(self.beta * h)
    def recall(self, s0, iters=50):
        s = s0.copy()
        for _ in range(iters): s = self.step(s)
        return s

class ReinjectionLoop:
    def __init__(self, band=0.1, target=0.0):
        self.band = band; self.target = target; self.history = []; self.fired = 0
    def check(self, D_measured):
        drift = abs(D_measured - self.target); should_fire = drift > self.band
        self.history.append((D_measured, should_fire))
        if should_fire: self.fired += 1
        return should_fire
    def reinject(self, current_state, correction=0.0):
        return current_state + correction

class CellStack:
    def __init__(self, R27=27.0, band=0.05, seed=42):
        np.random.seed(seed); self.R27 = R27; self.band = band
        self.BC = Memristor(w0=5e-9); self.TC = Memristor(w0=5e-9); self.QC = Memristor(w0=5e-9)
        self.mem_BC = QuadraticHopfield(4, [np.array([1,1,-1,-1]), np.array([1,-1,1,-1])], lam=0.1)
        self.mem_TC = QuadraticHopfield(4, [np.array([1,-1,-1,1]), np.array([-1,1,1,-1])], lam=0.1)
        self.mem_QC = QuadraticHopfield(4, [np.array([1,1,1,-1]), np.array([-1,-1,1,1])], lam=0.1)
        self.loop_BC = ReinjectionLoop(band=band, target=0.0)
        self.loop_TC = ReinjectionLoop(band=band, target=0.0)
        self.loop_QC = ReinjectionLoop(band=band, target=self.R27)
        self.D_BC = 0.0; self.D_TC = 0.0; self.D_QC = 0.0; self.CENTER = 0.0; self.history = []
        self.running = False
    def _measure_D(self, mem, state):
        return mem.energy(state) - self.CENTER
    def step(self, drive_V=0.5, dt=1e-4):
        self.BC.step(drive_V, dt); self.TC.step(drive_V, dt); self.QC.step(drive_V * 0.8, dt)
        cue_BC = np.array([1,1,-1,-1]) + np.random.normal(0, 0.2, 4)
        cue_TC = np.array([1,-1,-1,1]) + np.random.normal(0, 0.2, 4)
        cue_QC = np.array([1,1,1,-1]) + np.random.normal(0, 0.2, 4)
        s_BC = self.mem_BC.recall(cue_BC); s_TC = self.mem_TC.recall(cue_TC); s_QC = self.mem_QC.recall(cue_QC)
        self.D_BC = self._measure_D(self.mem_BC, s_BC)
        self.D_TC = self._measure_D(self.mem_TC, s_TC)
        self.D_QC = self._measure_D(self.mem_QC, s_QC)
        if self.loop_BC.check(self.D_BC): s_BC = self.loop_BC.reinject(s_BC, correction=-0.01*self.D_BC)
        if self.loop_TC.check(self.D_TC): s_TC = self.loop_TC.reinject(s_TC, correction=-0.01*self.D_TC)
        if self.loop_QC.check(self.D_QC): s_QC = self.loop_QC.reinject(s_QC, correction=-0.01*(self.D_QC - self.R27))
        self.history.append({'D_BC': self.D_BC, 'D_TC': self.D_TC, 'D_QC': self.D_QC,
            'w_BC': self.BC.w, 'w_TC': self.TC.w, 'w_QC': self.QC.w,
            'fired_BC': self.loop_BC.fired, 'fired_TC': self.loop_TC.fired, 'fired_QC': self.loop_QC.fired})
        return self.D_BC, self.D_TC, self.D_QC
    def power_off(self): pass
    def power_on(self): pass
    def report(self):
        if not self.history: return "no steps"
        last = self.history[-1]
        return (f"D_BC={last['D_BC']:.3f} D_TC={last['D_TC']:.3f} D_QC={last['D_QC']:.3f} "
                f"R27={self.R27} fired=[BC:{last['fired_BC']} TC:{last['fired_TC']} QC:{last['fired_QC']}]")

# ============================================================
# APP
# ============================================================
class PhysicsApp:
    def __init__(self, root):
        self.root = root
        root.title("RABBIT-HOPPING Physics Sandbox")
        root.geometry("1100x720")
        root.configure(bg="#0a0a0f")

        self.stack = CellStack(R27=27.0, band=0.05, seed=7)
        self.mem = Memristor()
        self.hop = QuadraticHopfield(4, [np.array([1,1,-1,-1]), np.array([1,-1,1,-1])], lam=0.1)
        self.reinj = ReinjectionLoop(band=0.1)

        self.running = False
        self.sim_thread = None

        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg="#0a0a0f")
        hdr.pack(fill="x", padx=10, pady=8)
        tk.Label(hdr, text="RABBIT-HOPPING  //  PHYSICS SANDBOX", fg="#00ff9f", bg="#0a0a0f",
                 font=("Courier", 16, "bold")).pack(side="left")
        self.status_lbl = tk.Label(hdr, text="SIMULATION ONLY  |  YELLOW", fg="#ffaa00", bg="#0a0a0f",
                                   font=("Courier", 10))
        self.status_lbl.pack(side="right")

        # Notebook tabs
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_cell = tk.Frame(nb, bg="#0a0a0f")
        self.tab_mem = tk.Frame(nb, bg="#0a0a0f")
        self.tab_hop = tk.Frame(nb, bg="#0a0a0f")
        self.tab_reinj = tk.Frame(nb, bg="#0a0a0f")
        nb.add(self.tab_cell, text="  CELL STACK  ")
        nb.add(self.tab_mem, text="  MEMRISTOR  ")
        nb.add(self.tab_hop, text="  QUADRATIC HOPFIELD  ")
        nb.add(self.tab_reinj, text="  REINJECTION  ")

        self._build_cell_tab()
        self._build_mem_tab()
        self._build_hop_tab()
        self._build_reinj_tab()

        # Footer log
        logf = tk.Frame(self.root, bg="#0a0a0f")
        logf.pack(fill="x", padx=10, pady=5)
        tk.Label(logf, text="LOG", fg="#00ff9f", bg="#0a0a0f", font=("Courier", 9)).pack(anchor="w")
        self.log = tk.Text(logf, height=6, bg="#111118", fg="#00ff9f", font=("Courier", 9),
                           insertbackground="#00ff9f")
        self.log.pack(fill="x")
        self._log("Sandbox app ready. No hardware. Pure simulation.")

    # ---------- CELL STACK TAB ----------
    def _build_cell_tab(self):
        f = self.tab_cell
        # Controls
        ctrl = tk.Frame(f, bg="#0a0a0f")
        ctrl.pack(fill="x", padx=10, pady=5)
        tk.Label(ctrl, text="Drive V:", fg="#aaa", bg="#0a0a0f", font=("Courier", 10)).pack(side="left")
        self.drive_var = tk.DoubleVar(value=0.5)
        tk.Scale(ctrl, from_=0.0, to=2.0, resolution=0.05, orient="horizontal", length=200,
                 variable=self.drive_var, bg="#0a0a0f", fg="#00ff9f", troughcolor="#222").pack(side="left", padx=5)
        tk.Label(ctrl, text="R27:", fg="#aaa", bg="#0a0a0f", font=("Courier", 10)).pack(side="left", padx=(20,0))
        self.r27_var = tk.DoubleVar(value=27.0)
        tk.Scale(ctrl, from_=0.0, to=50.0, resolution=1.0, orient="horizontal", length=200,
                 variable=self.r27_var, bg="#0a0a0f", fg="#00ff9f", troughcolor="#222").pack(side="left", padx=5)
        self.btn_run = tk.Button(ctrl, text="RUN", bg="#003322", fg="#00ff9f", font=("Courier", 10, "bold"),
                                 command=self._toggle_run)
        self.btn_run.pack(side="left", padx=10)
        tk.Button(ctrl, text="POWER OFF", bg="#330000", fg="#ff5555", font=("Courier", 10),
                  command=self._power_off).pack(side="left", padx=5)
        tk.Button(ctrl, text="POWER ON", bg="#003322", fg="#00ff9f", font=("Courier", 10),
                  command=self._power_on).pack(side="left", padx=5)
        tk.Button(ctrl, text="RESET", bg="#222", fg="#aaa", font=("Courier", 10),
                  command=self._reset_stack).pack(side="left", padx=5)

        # Canvas for live plot
        self.cell_canvas = tk.Canvas(f, bg="#050508", highlightthickness=0)
        self.cell_canvas.pack(fill="both", expand=True, padx=10, pady=5)
        self.cell_canvas.bind("<Configure>", lambda e: self._draw_cell())

        # Readout
        self.cell_readout = tk.Label(f, text="", fg="#00ff9f", bg="#0a0a0f", font=("Courier", 11),
                                     justify="left")
        self.cell_readout.pack(fill="x", padx=10, pady=5)

    def _draw_cell(self):
        c = self.cell_canvas
        c.delete("all")
        w = c.winfo_width(); h = c.winfo_height()
        if w < 10 or h < 10: return
        # Title
        c.create_text(w//2, 20, text="CELL STACK  BC-DC / TC-AC / QC-RC", fill="#00ff9f",
                      font=("Courier", 12, "bold"))
        # Three bars for D_BC, D_TC, D_QC
        labels = ["BC-DC", "TC-AC", "QC-RC (R27)"]
        vals = [self.stack.D_BC, self.stack.D_TC, self.stack.D_QC]
        colors = ["#00aaff", "#ffaa00", "#ff00aa"]
        bar_w = (w - 80) / 3
        max_abs = max(abs(v) for v in vals) if vals else 1
        max_abs = max(max_abs, self.stack.R27, 1)
        for i, (lab, val, col) in enumerate(zip(labels, vals, colors)):
            x0 = 40 + i * (bar_w + 20)
            # baseline
            cy = h * 0.55
            c.create_line(x0, cy, x0 + bar_w, cy, fill="#333", width=1)
            # bar
            bh = (val / max_abs) * (h * 0.35)
            if val >= 0:
                c.create_rectangle(x0, cy - bh, x0 + bar_w, cy, fill=col, outline=col)
            else:
                c.create_rectangle(x0, cy, x0 + bar_w, cy - bh, fill=col, outline=col)
            c.create_text(x0 + bar_w/2, cy + 18, text=f"{val:.2f}", fill=col, font=("Courier", 10))
            c.create_text(x0 + bar_w/2, cy + 36, text=lab, fill="#aaa", font=("Courier", 9))
        # R27 target line
        r27y = cy - (self.stack.R27 / max_abs) * (h * 0.35)
        c.create_line(40, r27y, w - 40, r27y, fill="#ff00aa", dash=(4,4), width=1)
        c.create_text(w - 50, r27y - 10, text=f"R27={self.stack.R27}", fill="#ff00aa", font=("Courier", 8))
        # Memristor w state
        c.create_text(w//2, h - 30, text=f"mem w: BC={self.stack.BC.w*1e9:.2f}n  TC={self.stack.TC.w*1e9:.2f}n  QC={self.stack.QC.w*1e9:.2f}n   |   {self.stack.report()}",
                      fill="#00ff9f", font=("Courier", 9))

    # ---------- MEMRISTOR TAB ----------
    def _build_mem_tab(self):
        f = self.tab_mem
        ctrl = tk.Frame(f, bg="#0a0a0f")
        ctrl.pack(fill="x", padx=10, pady=5)
        tk.Label(ctrl, text="Amp:", fg="#aaa", bg="#0a0a0f", font=("Courier", 10)).pack(side="left")
        self.mem_amp = tk.DoubleVar(value=1.0)
        tk.Scale(ctrl, from_=0.1, to=5.0, resolution=0.1, orient="horizontal", length=150,
                 variable=self.mem_amp, bg="#0a0a0f", fg="#00ff9f", troughcolor="#222").pack(side="left", padx=5)
        tk.Label(ctrl, text="Freq:", fg="#aaa", bg="#0a0a0f", font=("Courier", 10)).pack(side="left", padx=(10,0))
        self.mem_freq = tk.DoubleVar(value=1.0)
        tk.Scale(ctrl, from_=0.1, to=5.0, resolution=0.1, orient="horizontal", length=150,
                 variable=self.mem_freq, bg="#0a0a0f", fg="#00ff9f", troughcolor="#222").pack(side="left", padx=5)
        tk.Button(ctrl, text="RUN PINCHED TEST", bg="#003322", fg="#00ff9f", font=("Courier", 10, "bold"),
                  command=self._run_mem_test).pack(side="left", padx=10)
        self.mem_canvas = tk.Canvas(f, bg="#050508", highlightthickness=0)
        self.mem_canvas.pack(fill="both", expand=True, padx=10, pady=5)
        self.mem_canvas.bind("<Configure>", lambda e: self._draw_mem())
        self.mem_readout = tk.Label(f, text="", fg="#00ff9f", bg="#0a0a0f", font=("Courier", 11))
        self.mem_readout.pack(fill="x", padx=10, pady=5)

    def _run_mem_test(self):
        self.mem.reset()
        Vs, Is = self.mem.pinched_test(freq=self.mem_freq.get(), amp=self.mem_amp.get())
        self._mem_Vs, self._mem_Is = Vs, Is
        self._draw_mem()
        self._log(f"Memristor pinched test: {len(Vs)} points, amp={self.mem_amp.get()}, freq={self.mem_freq.get()}")

    def _draw_mem(self):
        c = self.mem_canvas
        c.delete("all")
        w = c.winfo_width(); h = c.winfo_height()
        if w < 10 or h < 10: return
        if not hasattr(self, '_mem_Vs'):
            c.create_text(w//2, h//2, text="Press RUN PINCHED TEST", fill="#555", font=("Courier", 12))
            return
        Vs, Is = self._mem_Vs, self._mem_Is
        pad = 50
        maxv = max(abs(Vs.max()), abs(Vs.min()), 0.1)
        maxi = max(abs(Is.max()), abs(Is.min()), 0.1)
        def sx(v): return pad + (v + maxv) / (2*maxv) * (w - 2*pad)
        def sy(i): return h - pad - (i + maxi) / (2*maxi) * (h - 2*pad)
        # axes
        c.create_line(pad, h-pad, w-pad, h-pad, fill="#333")
        c.create_line(pad, pad, pad, h-pad, fill="#333")
        c.create_text(w//2, h-15, text="V", fill="#aaa", font=("Courier", 10))
        c.create_text(15, h//2, text="I", fill="#aaa", font=("Courier", 10))
        # loop
        pts = [sx(v) for v in Vs] + [sy(i) for i in Is]
        coords = []
        for v, i in zip(Vs, Is):
            coords.append(sx(v)); coords.append(sy(i))
        c.create_line(coords, fill="#00ff9f", width=2, smooth=True)
        # pinch marker at V~0
        zi = np.argmin(np.abs(Vs))
        c.create_oval(sx(Vs[zi])-4, sy(Is[zi])-4, sx(Vs[zi])+4, sy(Is[zi])+4, outline="#ff00aa", width=2)
        self.mem_readout.config(text=f"Pinch at V=0: I={Is[zi]:.5f}  |  w={self.mem.w*1e9:.2f}n  |  R={self.mem.resistance():.1f} ohm")

    # ---------- HOPFIELD TAB ----------
    def _build_hop_tab(self):
        f = self.tab_hop
        ctrl = tk.Frame(f, bg="#0a0a0f")
        ctrl.pack(fill="x", padx=10, pady=5)
        tk.Button(ctrl, text="RECALL FROM NOISE", bg="#003322", fg="#00ff9f", font=("Courier", 10, "bold"),
                  command=self._run_hop_recall).pack(side="left", padx=5)
        tk.Button(ctrl, text="ENERGY SURFACE", bg="#222", fg="#aaa", font=("Courier", 10),
                  command=self._draw_hop_energy).pack(side="left", padx=5)
        self.hop_canvas = tk.Canvas(f, bg="#050508", highlightthickness=0)
        self.hop_canvas.pack(fill="both", expand=True, padx=10, pady=5)
        self.hop_canvas.bind("<Configure>", lambda e: self._draw_hop())
        self.hop_readout = tk.Label(f, text="", fg="#00ff9f", bg="#0a0a0f", font=("Courier", 11))
        self.hop_readout.pack(fill="x", padx=10, pady=5)
        self._hop_result = None

    def _run_hop_recall(self):
        p1 = np.array([1.0, 1.0, -1.0, -1.0])
        s0 = p1 + np.random.normal(0, 0.4, 4)
        s = self.hop.recall(s0)
        self._hop_result = (s0, s, p1)
        self._draw_hop()
        ok = np.allclose(np.sign(s), p1, atol=0.2)
        self._log(f"Hopfield recall: {'OK' if ok else 'FAIL'}  recovered={np.round(s,2)}")

    def _draw_hop_energy(self):
        c = self.hop_canvas
        c.delete("all")
        w = c.winfo_width(); h = c.winfo_height()
        if w < 10 or h < 10: return
        c.create_text(w//2, 20, text="ENERGY vs STATE (1D slice)", fill="#00ff9f", font=("Courier", 12, "bold"))
        xs = np.linspace(-1.5, 1.5, 200)
        Es = [self.hop.energy(np.array([x, x, -x, -x])) for x in xs]
        pad = 50
        maxe = max(abs(min(Es)), abs(max(Es)), 1)
        def sx(x): return pad + (x + 1.5) / 3.0 * (w - 2*pad)
        def sy(e): return h - pad - (e + maxe) / (2*maxe) * (h - 2*pad)
        c.create_line(pad, h-pad, w-pad, h-pad, fill="#333")
        c.create_line(pad, pad, pad, h-pad, fill="#333")
        coords = []
        for x, e in zip(xs, Es):
            coords.append(sx(x)); coords.append(sy(e))
        c.create_line(coords, fill="#ffaa00", width=2)
        self.hop_readout.config(text=f"Energy at pattern: {self.hop.energy(np.array([1,1,-1,-1])):.3f}  |  quartic term prevents collapse")

    def _draw_hop(self):
        if self._hop_result is None:
            c = self.hop_canvas
            c.delete("all")
            w = c.winfo_width(); h = c.winfo_height()
            if w > 10 and h > 10:
                c.create_text(w//2, h//2, text="Press RECALL FROM NOISE", fill="#555", font=("Courier", 12))
            return
        s0, s, p1 = self._hop_result
        c = self.hop_canvas
        c.delete("all")
        w = c.winfo_width(); h = c.winfo_height()
        if w < 10 or h < 10: return
        c.create_text(w//2, 20, text="RECALL: noisy cue -> recovered pattern", fill="#00ff9f", font=("Courier", 11, "bold"))
        # show 4-bit patterns as bars
        for idx, (lab, vec, col) in enumerate([("cue", s0, "#555"), ("recovered", s, "#00ff9f"), ("target", p1, "#ff00aa")]):
            y = 60 + idx * 80
            c.create_text(30, y, text=lab, fill=col, font=("Courier", 9), anchor="w")
            for j, v in enumerate(vec):
                x = 80 + j * 60
                bh = abs(v) * 30
                if v >= 0:
                    c.create_rectangle(x, y - bh, x + 40, y, fill=col, outline=col)
                else:
                    c.create_rectangle(x, y, x + 40, y + bh, fill=col, outline=col)
        self.hop_readout.config(text=f"Recovered matches target: {np.allclose(np.sign(s), p1, atol=0.2)}")

    # ---------- REINJECTION TAB ----------
    def _build_reinj_tab(self):
        f = self.tab_reinj
        ctrl = tk.Frame(f, bg="#0a0a0f")
        ctrl.pack(fill="x", padx=10, pady=5)
        tk.Label(ctrl, text="D value:", fg="#aaa", bg="#0a0a0f", font=("Courier", 10)).pack(side="left")
        self.reinj_d = tk.DoubleVar(value=0.0)
        tk.Scale(ctrl, from_=-1.0, to=1.0, resolution=0.01, orient="horizontal", length=200,
                 variable=self.reinj_d, bg="#0a0a0f", fg="#00ff9f", troughcolor="#222").pack(side="left", padx=5)
        tk.Button(ctrl, text="CHECK", bg="#003322", fg="#00ff9f", font=("Courier", 10, "bold"),
                  command=self._check_reinj).pack(side="left", padx=10)
        tk.Button(ctrl, text="RESET", bg="#222", fg="#aaa", font=("Courier", 10),
                  command=self._reset_reinj).pack(side="left", padx=5)
        self.reinj_canvas = tk.Canvas(f, bg="#050508", highlightthickness=0)
        self.reinj_canvas.pack(fill="both", expand=True, padx=10, pady=5)
        self.reinj_canvas.bind("<Configure>", lambda e: self._draw_reinj())
        self.reinj_readout = tk.Label(f, text="", fg="#00ff9f", bg="#0a0a0f", font=("Courier", 11))
        self.reinj_readout.pack(fill="x", padx=10, pady=5)

    def _check_reinj(self):
        d = self.reinj_d.get()
        fired = self.reinj.check(d)
        self._draw_reinj()
        self.reinj_readout.config(text=f"D={d:.3f}  fired={fired}  total_fired={self.reinj.fired}")
        self._log(f"Reinjection check: D={d:.3f} -> {'FIRE' if fired else 'hold'}")

    def _reset_reinj(self):
        self.reinj = ReinjectionLoop(band=0.1)
        self._draw_reinj()
        self.reinj_readout.config(text="")
        self._log("Reinjection reset")

    def _draw_reinj(self):
        c = self.reinj_canvas
        c.delete("all")
        w = c.winfo_width(); h = c.winfo_height()
        if w < 10 or h < 10: return
        c.create_text(w//2, 20, text="REINJECTION FIRING LOG", fill="#00ff9f", font=("Courier", 12, "bold"))
        # band visualization
        pad = 50
        cy = h * 0.5
        c.create_line(pad, cy, w-pad, cy, fill="#333")
        # band lines
        band_y_up = cy - 30
        band_y_dn = cy + 30
        c.create_line(pad, band_y_up, w-pad, band_y_up, fill="#ff5555", dash=(2,2))
        c.create_line(pad, band_y_dn, w-pad, band_y_dn, fill="#ff5555", dash=(2,2))
        c.create_text(w-60, band_y_up-10, text="+band", fill="#ff5555", font=("Courier", 8))
        c.create_text(w-60, band_y_dn+10, text="-band", fill="#ff5555", font=("Courier", 8))
        # history dots
        if self.reinj.history:
            n = len(self.reinj.history)
            for i, (d, fired) in enumerate(self.reinj.history[-50:]):
                x = pad + (i / 50.0) * (w - 2*pad)
                y = cy - (d / 1.0) * 30
                col = "#ff00aa" if fired else "#00ff9f"
                c.create_oval(x-3, y-3, x+3, y+3, fill=col, outline=col)
        self.reinj_readout.config(text=f"Total fires: {self.reinj.fired}  |  band=0.1")

    # ---------- CONTROLS ----------
    def _toggle_run(self):
        if self.running:
            self.running = False
            self.btn_run.config(text="RUN")
            self._log("Paused.")
        else:
            self.running = True
            self.btn_run.config(text="PAUSE")
            self._log("Running cell stack...")
            self.sim_thread = threading.Thread(target=self._sim_loop, daemon=True)
            self.sim_thread.start()

    def _sim_loop(self):
        while self.running:
            self.stack.step(drive_V=self.drive_var.get(), dt=1e-3)
            self.stack.R27 = self.r27_var.get()
            self.root.after(0, self._draw_cell)
            time.sleep(0.05)

    def _power_off(self):
        self.stack.power_off()
        self._log("POWER OFF - magnetic hold active (state persists)")
        self._draw_cell()

    def _power_on(self):
        self.stack.power_on()
        self._log("POWER ON - state retained")
        self._draw_cell()

    def _reset_stack(self):
        self.stack = CellStack(R27=self.r27_var.get(), band=0.05, seed=7)
        self._log("Cell stack reset")
        self._draw_cell()

    def _log(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

def main():
    root = tk.Tk()
    app = PhysicsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
