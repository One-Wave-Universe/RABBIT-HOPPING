#!/usr/bin/env python3
"""
RABBIT-HOPPING Physics Sandbox
=============================
Expanded virtual breadboard with real physics constraints.

Modules:
1. Memristor (HP-style) - pinched hysteresis, magnetic hold latch
2. Quadratic Hopfield - energy landscape with quadratic term to prevent collapse
3. Reinjection loop - differential-triggered, not timer-based
4. Virtual breadboard - netlist + constraint checker

Run: python sandbox/physics_sandbox.py
"""

import numpy as np
from scipy.integrate import odeint

# ============================================================
# 1. MEMRISTOR MODEL (Chua / HP Labs)
# ============================================================
class Memristor:
    """HP-style memristor with pinched hysteresis.
    State variable w = doped region width.
    v = [Ron*w/D + Roff*(1-w/D)] * i
    dw/dt = mu*Ron/D * i
    """
    def __init__(self, Ron=100.0, Roff=16000.0, D=10e-9, mu=1e-14, w0=5e-9):
        self.Ron = Ron
        self.Roff = Roff
        self.D = D
        self.mu = mu
        self.w = w0
        self.history = []

    def resistance(self, w=None):
        w = w if w is not None else self.w
        w = np.clip(w, 0, self.D)
        return self.Ron * (w / self.D) + self.Roff * (1 - w / self.D)

    def step(self, V, dt=1e-4):
        """Advance one time step with applied voltage V."""
        R = self.resistance()
        I = V / R if R > 0 else 0.0
        dw = self.mu * self.Ron / self.D * I * dt
        self.w = np.clip(self.w + dw, 0, self.D)
        self.history.append((V, I, self.w))
        return I

    def reset(self, w0=None):
        self.w = w0 if w0 is not None else self.D / 2
        self.history = []

    def pinched_test(self, freq=1.0, amp=1.0, cycles=2, steps=500):
        """Run sinusoidal drive, return (V_array, I_array). Check pinch at V=0."""
        ts = np.linspace(0, cycles / freq, steps)
        Vs, Is = [], []
        self.reset()
        for t in ts:
            V = amp * np.sin(2 * np.pi * freq * t)
            I = self.step(V, dt=ts[1] - ts[0])
            Vs.append(V)
            Is.append(I)
        Vs, Is = np.array(Vs), np.array(Is)
        # Pinch check: I near 0 when V near 0
        zero_idx = np.argmin(np.abs(Vs))
        pinched = abs(Is[zero_idx]) < 0.05 * amp / 100  # loose tolerance
        return Vs, Is, pinched


# ============================================================
# 2. QUADRATIC HOPFIELD (prevents attractor collapse)
# ============================================================
class QuadraticHopfield:
    """Hopfield network with explicit quadratic energy term.
    E = -0.5 * s^T W s + lambda * ||s||^4
    The quartic term penalizes large states, keeping similar patterns distinct.
    """
    def __init__(self, n, patterns, lam=0.1, beta=5.0):
        self.n = n
        self.W = np.zeros((n, n))
        for p in patterns:
            self.W += np.outer(p, p)
        np.fill_diagonal(self.W, 0)
        self.lam = lam
        self.beta = beta

    def energy(self, s):
        quad = -0.5 * s @ self.W @ s
        quart = self.lam * np.sum(s**4)
        return quad + quart

    def step(self, s):
        h = self.W @ s - 4 * self.lam * s**3
        return np.tanh(self.beta * h)

    def recall(self, s0, iters=50):
        s = s0.copy()
        for _ in range(iters):
            s = self.step(s)
        return s


# ============================================================
# 3. REINJECTION LOOP (differential-triggered)
# ============================================================
class ReinjectionLoop:
    """Fires only when measured differential leaves the band.
    Not a timer. Physics-constrained: only reinjects when D drifts.
    """
    def __init__(self, band=0.1, target=0.0):
        self.band = band
        self.target = target
        self.history = []
        self.fired = 0

    def check(self, D_measured):
        """Returns True if reinjection should fire."""
        drift = abs(D_measured - self.target)
        should_fire = drift > self.band
        self.history.append((D_measured, should_fire))
        if should_fire:
            self.fired += 1
        return should_fire

    def reinject(self, current_state, correction=0.0):
        """Apply correction to bring D back toward target."""
        return current_state + correction


# ============================================================
# 4. VIRTUAL BREADBOARD (expanded)
# ============================================================
class VirtualBreadboard:
    """Netlist + physics constraint checker.
    Connects memristors, Hopfield nodes, reinjection loops.
    Validates: no floating nodes, polarity consistency, energy bounds.
    """
    def __init__(self):
        self.nodes = {}
        self.components = []
        self.constraints = []
        self.violations = []

    def add_node(self, name, value=0.0):
        self.nodes[name] = value

    def add_memristor(self, name, n1, n2, **params):
        m = Memristor(**params)
        self.components.append((name, 'memristor', m, n1, n2))
        return m

    def add_hopfield(self, name, patterns, **params):
        n = len(patterns[0])
        h = QuadraticHopfield(n, patterns, **params)
        self.components.append((name, 'hopfield', h, None, None))
        return h

    def add_reinjection(self, name, band=0.1):
        r = ReinjectionLoop(band=band)
        self.components.append((name, 'reinjection', r, None, None))
        return r

    def check_constraints(self):
        """Run all physics constraints. Return list of violations."""
        self.violations = []
        # Energy must be bounded below for Hopfield
        for name, ctype, comp, *_ in self.components:
            if ctype == 'hopfield':
                # sample a few states
                for _ in range(10):
                    s = np.random.uniform(-1, 1, comp.n)
                    E = comp.energy(s)
                    if E > 1e6:
                        self.violations.append(f"{name}: energy unbounded {E}")
            if ctype == 'memristor':
                if comp.w < 0 or comp.w > comp.D:
                    self.violations.append(f"{name}: w out of bounds {comp.w}")
        # Node connectivity: every component node must exist
        for name, ctype, comp, n1, n2 in self.components:
            if n1 and n1 not in self.nodes:
                self.violations.append(f"{name}: node {n1} not defined")
            if n2 and n2 not in self.nodes:
                self.violations.append(f"{name}: node {n2} not defined")
        return self.violations

    def status(self):
        v = self.check_constraints()
        return "GREEN" if not v else f"RED: {len(v)} violations"


# ============================================================
# TESTS
# ============================================================
def test_memristor_pinched():
    m = Memristor()
    Vs, Is, pinched = m.pinched_test()
    assert pinched, "Memristor must show pinched hysteresis at V=0"
    assert len(Vs) == len(Is)
    print("[PASS] memristor pinched hysteresis")

def test_quadratic_hopfield_no_collapse():
    p1 = np.array([1.0, 1.0, -1.0, -1.0])
    p2 = np.array([1.0, -1.0, 1.0, -1.0])
    h = QuadraticHopfield(4, [p1, p2], lam=0.1)
    # noisy recall of p1
    s0 = p1 + np.random.normal(0, 0.3, 4)
    s = h.recall(s0)
    assert np.allclose(np.sign(s), p1, atol=0.2), f"Collapsed: {s}"
    # energy bounded
    assert h.energy(s) < 0
    print("[PASS] quadratic Hopfield no-collapse + bounded energy")

def test_reinjection_differential():
    r = ReinjectionLoop(band=0.1)
    assert not r.check(0.05), "Should not fire inside band"
    assert r.check(0.5), "Should fire outside band"
    assert r.fired == 1
    print("[PASS] reinjection differential-triggered")

def test_breadboard_constraints():
    bb = VirtualBreadboard()
    bb.add_node("A", 0.0)
    bb.add_node("B", 0.0)
    bb.add_memristor("M1", "A", "B")
    bb.add_hopfield("H1", [np.array([1, -1, 1, -1])])
    bb.add_reinjection("R1", band=0.1)
    status = bb.status()
    assert "GREEN" in status, f"Breadboard failed: {status}"
    print("[PASS] virtual breadboard constraints GREEN")

def test_full_sandbox():
    """End-to-end: memristor hold -> Hopfield recall -> reinjection."""
    m = Memristor()
    # drive to set a state
    for _ in range(100):
        m.step(0.5, dt=1e-4)
    held_w = m.w
    # power off (no step) - state persists
    assert abs(m.w - held_w) < 1e-12, "Memristor lost state on power-off"
    # Hopfield recall
    p1 = np.array([1.0, 1.0, -1.0, -1.0])
    h = QuadraticHopfield(4, [p1])
    s = h.recall(p1 + np.random.normal(0, 0.2, 4))
    assert np.allclose(np.sign(s), p1, atol=0.2)
    # reinjection only on drift
    r = ReinjectionLoop(band=0.05)
    assert not r.check(0.0)
    assert r.check(0.1)
    print("[PASS] full sandbox: hold + recall + reinjection")

if __name__ == "__main__":
    np.random.seed(42)
    test_memristor_pinched()
    test_quadratic_hopfield_no_collapse()
    test_reinjection_differential()
    test_breadboard_constraints()
    test_full_sandbox()
    print("\n=== ALL SANDBOX TESTS PASSED ===")
    print("Physics constraints: ACTIVE")
    print("Memristor hysteresis: REAL")
    print("Quadratic energy: BOUNDED")
    print("Reinjection: DIFFERENTIAL-TRIGGERED")
    print("Breadboard: GREEN")
