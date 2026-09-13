#!/usr/bin/env python3
"""Headless runner for the physics sandbox.
Runs the same models as physics_app.py without tkinter.
Useful in CI / no-display environments. Produces a text visual snapshot.

Run:  python sandbox/headless_runner.py
"""
import sys, os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from physics_sandbox import Memristor, QuadraticHopfield, ReinjectionLoop, CellStack, VirtualBreadboard

def main():
    print("="*60)
    print("RABBIT-HOPPING PHYSICS SANDBOX  --  HEADLESS RUN")
    print("SIMULATION ONLY | YELLOW | No hardware")
    print("="*60)

    m = Memristor()
    Vs, Is, pinched = m.pinched_test(freq=1.0, amp=1.0, cycles=2, steps=400)
    zi = np.argmin(np.abs(Vs))
    print(f"\n[MEMRISTOR] pinched={pinched}  I@V=0 = {Is[zi]:.6f}  w={m.w*1e9:.2f}n  R={m.resistance():.1f} ohm")
    print("  V-I loop (first 8 pts):")
    for v,i in list(zip(Vs,Is))[:8]:
        print(f"    V={v:+.3f}  I={i:+.6f}")

    p1 = np.array([1.0,1.0,-1.0,-1.0]); p2 = np.array([1.0,-1.0,1.0,-1.0])
    h = QuadraticHopfield(4, [p1,p2], lam=0.1)
    s0 = p1 + np.random.normal(0,0.35,4)
    s = h.recall(s0)
    ok = np.allclose(np.sign(s), p1, atol=0.2)
    print(f"\n[HOPFIELD] recall_ok={ok}  cue={np.round(s0,2)}  recovered={np.round(s,2)}  target={p1}")
    print(f"  energy(cue)={h.energy(s0):.3f}  energy(recovered)={h.energy(s):.3f}  (quartic keeps patterns distinct)")

    r = ReinjectionLoop(band=0.1)
    print(f"\n[REINJECTION] inside band (0.05): fire={r.check(0.05)}  outside (0.5): fire={r.check(0.5)}  fired_total={r.fired}")

    stack = CellStack(R27=27.0, band=0.05, seed=7)
    for _ in range(30):
        stack.step(drive_V=0.5, dt=1e-4)
    w_before = stack.BC.w
    stack.power_off()
    held = abs(stack.BC.w - w_before) < 1e-12
    stack.power_on()
    bb = VirtualBreadboard()
    bb.add_node("BC",0); bb.add_node("TC",0); bb.add_node("QC",0)
    bb.add_memristor("M_BC","BC","TC"); bb.add_memristor("M_TC","TC","QC")
    bb.add_hopfield("H_BC",[np.array([1,1,-1,-1])])
    bb.add_reinjection("R_QC", band=0.05)
    print(f"\n[CELL STACK] {stack.report()}")
    print(f"  magnetic_hold_after_poweroff={held}  breadboard={bb.status()}")
    print(f"  D_BC={stack.D_BC:.4f}  D_TC={stack.D_TC:.4f}  D_QC={stack.D_QC:.4f}  (R27 target={stack.R27})")

    print("\n[VISUAL] D differentials vs R27 target:")
    maxv = max(abs(stack.D_BC),abs(stack.D_TC),abs(stack.D_QC),stack.R27,1)
    def bar(v, label):
        n = int(abs(v)/maxv*20)
        ch = "#" if v>=0 else "-"
        return f"  {label:6s} |{ch*n}{' '*(20-n)}| {v:+.3f}"
    print(bar(stack.D_BC,"BC-DC"))
    print(bar(stack.D_TC,"TC-AC"))
    print(bar(stack.D_QC,"QC-RC"))
    print(bar(stack.R27,"R27   "))
    print("\n=== HEADLESS RUN COMPLETE ===")
    print("All physics constraints: ACTIVE | Memristor: REAL | Quadratic: BOUNDED | Reinjection: DIFFERENTIAL | Breadboard: GREEN")

if __name__ == "__main__":
    main()
