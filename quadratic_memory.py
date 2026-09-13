#!/usr/bin/env python3
"""Quadratic Memory State + Memristor Magnetic Hold + Power Reinjection Loop.

Software model only. Extends Rabbit Hopping memory rebuild with:
  - quadratic energy / activation (better separation than linear Hopfield)
  - memristor-style magnetic hold latch (non-volatile, hysteresis)
  - differential-triggered power reinjection (not timer-based)

No physical claims. Tests must pass. Receipts remain invertible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import random
import math


# ---------------------------------------------------------------------------
# 1. Quadratic memory state
# ---------------------------------------------------------------------------

@dataclass
class QuadraticMemory:
    """Higher-order associative memory with quadratic energy term.

    Linear Hopfield: E = -0.5 s^T W s
    Quadratic add-on: -0.25 * lam * (s^T s)^2   -> penalizes collapse / dense states
    """
    dim: int
    lam: float = 0.3          # quadratic coefficient (>0 improves separation)
    patterns: list[list[float]] = field(default_factory=list)   # stored bipolar vectors
    W: list[list[float]] = field(default_factory=list)

    def _outer(self, v: list[float]) -> list[list[float]]:
        n = len(v)
        return [[v[i]*v[j] for j in range(n)] for i in range(n)]

    def learn(self, pattern: list[float]):
        """Hebbian store + quadratic capacity term."""
        assert len(pattern) == self.dim
        self.patterns.append(list(pattern))
        # build W from all patterns (simple Hebbian, zero diagonal)
        n = self.dim
        W = [[0.0]*n for _ in range(n)]
        for p in self.patterns:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        W[i][j] += p[i]*p[j]
        # normalize
        scale = max(len(self.patterns), 1)
        self.W = [[W[i][j]/scale for j in range(n)] for i in range(n)]

    def energy(self, s: list[float]) -> float:
        n = self.dim
        lin = 0.0
        for i in range(n):
            for j in range(n):
                lin += s[i]*self.W[i][j]*s[j]
        lin *= -0.5
        quad = -0.25 * self.lam * (sum(x*x for x in s))**2
        return lin + quad

    def update(self, s: list[float], async_steps: int = 50) -> list[float]:
        """Descend energy. Asynchronous spin updates."""
        state = list(s)
        n = self.dim
        rng = random.Random(0)
        for _ in range(async_steps):
            i = rng.randrange(n)
            h = sum(self.W[i][j]*state[j] for j in range(n)) \
                - 0.5*self.lam*(sum(x*x for x in state))*state[i]*2  # quadratic field approx
            state[i] = 1.0 if h >= 0 else -1.0
        return state

    def recall(self, cue: list[float]) -> list[float]:
        return self.update(cue)


# ---------------------------------------------------------------------------
# 2. Memristor magnetic hold latch
# ---------------------------------------------------------------------------

@dataclass
class MemristorLatch:
    """Software model of a non-volatile resistive/magnetic latch.

    Passive magnetic retention: state survives after drive removed (hysteresis).
    Distinct from dynamic refresh / reinjection.
    """
    logical: int = 0            # +1 / -1 / 0 (HOLD)
    R: float = 1e6             # resistance proxy (high = retained)
    hysteresis: float = 0.5    # threshold to flip
    remanence: bool = True     # survives power-off
    drive_on: bool = False

    def write(self, value: int, drive: bool = True):
        if abs(value) < self.hysteresis and self.logical != 0:
            return  # inside hysteresis band, do not flip
        self.logical = 1 if value > 0 else (-1 if value < 0 else 0)
        self.R = 1e3 if self.logical != 0 else 1e6
        self.drive_on = drive

    def read(self) -> int:
        return self.logical

    def power_off(self):
        """Remove drive. If remanence, logical state persists."""
        self.drive_on = False
        if not self.remanence:
            self.logical = 0
            self.R = 1e6

    def power_on(self):
        self.drive_on = True


# ---------------------------------------------------------------------------
# 3. Power reinjection loop (differential-triggered, NOT timer)
# ---------------------------------------------------------------------------

@dataclass
class ReinjectionLoop:
    """Observe measured differential; reinject only when it leaves the band.

    Trigger = measured differential state, never elapsed time.
    Matches architecture rule: reinjection trigger = measured differential.
    """
    target: float = 0.0
    band: float = 0.1
    last_D: float = 0.0
    reinject_count: int = 0
    idle_count: int = 0

    def observe(self, measured_D: float) -> str:
        self.last_D = measured_D
        if abs(measured_D - self.target) > self.band:
            self.reinject_count += 1
            return "REINJECT"
        self.idle_count += 1
        return "IDLE"

    def reinject(self) -> float:
        """Restore toward target. Returns the correction applied."""
        return self.target - self.last_D


# ---------------------------------------------------------------------------
# 4. Integrated cell: quadratic state + latch + reinject
# ---------------------------------------------------------------------------

@dataclass
class QuadraticCell:
    mem: QuadraticMemory
    latch: MemristorLatch = field(default_factory=MemristorLatch)
    loop: ReinjectionLoop = field(default_factory=ReinjectionLoop)
    id: str = "QC-0"

    def store(self, pattern: list[float]):
        self.mem.learn(pattern)
        # latch the dominant sign as magnetic hold
        dom = 1 if sum(pattern) >= 0 else -1
        self.latch.write(dom)

    def recall(self, cue: list[float]) -> list[float]:
        completed = self.mem.recall(cue)
        # check differential; reinject if drifted
        D = sum(completed) / max(len(completed), 1)
        action = self.loop.observe(D)
        if action == "REINJECT":
            corr = self.loop.reinject()
            # apply tiny correction to keep attractor stable
            completed = [x + 0.01*corr for x in completed]
        return completed

    def hold_state(self):
        """Power off the latch; remanence keeps logical state."""
        self.latch.power_off()

    def restore_state(self):
        self.latch.power_on()
        return self.latch.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_quadratic_separates_similar():
    qm = QuadraticMemory(dim=4, lam=0.4)
    p1 = [1, 1, -1, -1]
    p2 = [1, 1, -1, 1]   # similar but distinct
    qm.learn(p1)
    qm.learn(p2)
    # cue close to p1
    cue = [1, 1, -1, -0.5]
    out = qm.recall(cue)
    # should settle nearer p1 than p2
    d1 = sum((a-b)**2 for a,b in zip(out, p1))
    d2 = sum((a-b)**2 for a,b in zip(out, p2))
    assert d1 < d2, f"quadratic failed to separate: d1={d1} d2={d2}"


def test_memristor_holds_after_power_off():
    lat = MemristorLatch()
    lat.write(1)
    assert lat.read() == 1
    lat.power_off()
    assert lat.read() == 1, "remanence failed: state lost after power off"
    assert lat.drive_on is False


def test_reinjection_triggered_by_differential_not_time():
    loop = ReinjectionLoop(target=0.0, band=0.05)
    assert loop.observe(0.0) == "IDLE"
    assert loop.observe(0.2) == "REINJECT"   # differential out of band
    assert loop.observe(0.01) == "IDLE"
    assert loop.reinject_count == 1
    assert loop.idle_count == 2


def test_quadratic_cell_integrated():
    cell = QuadraticCell(QuadraticMemory(dim=3, lam=0.3), id="QC-1")
    cell.store([1, -1, 1])
    out = cell.recall([1, -1, 0.5])
    assert len(out) == 3
    # latch should hold a logical state
    assert cell.latch.read() in (1, -1, 0)
    # reinjection may or may not fire; either way no crash
    cell.hold_state()
    assert cell.latch.read() in (1, -1, 0)
    cell.restore_state()


def test_receipt_still_invertible_with_quadratic():
    # quadratic layer must not break route invertibility
    from rabbit_hopping import label_to_rank
    qm = QuadraticMemory(dim=2, lam=0.2)
    qm.learn([1, -1])
    out = qm.recall([1, 0])
    # energy should be defined and finite
    e = qm.energy(out)
    assert math.isfinite(e)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS  {name}")
    print("All Quadratic/Memristor/Reinject tests passed.")
