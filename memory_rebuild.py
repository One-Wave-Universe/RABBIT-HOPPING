#!/usr/bin/env python3
"""Rabbit Hopping Memory Rebuild / Recall Engine.

Turns reversible routes into an actual recall system:
cue -> constellation neighborhood -> rabbit-hop route -> Hopfield completion ->
probabilistic fill (if needed) -> state-machine validation -> receipt.

No physical claims. Receipts must invert.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional
import random

from rabbit_hopping import (
    Packet, make_packets, FAMILIES, label_to_rank, rank_to_label,
    shared_wrapper_connects, mirror_packet
)


# ---- Constellation: relational memory shape ----

@dataclass
class Memory:
    mem_id: str
    features: set[str]                 # overlapping sensory/motion/language fragments
    anchor_label: str                 # source identity (e.g. "A")
    anchor_domain: str = "alphabet-26"
    orientation: str = "normal"
    route_family: str = "A"
    K: int = 0
    polarity: int = 1
    hierarchy_level: int = 0
    # recorded rabbit-hop neighborhood for this memory
    neighborhood: list[Packet] = field(default_factory=list)

    def build_neighborhood(self):
        self.neighborhood = make_packets(
            self.mem_id, self.anchor_label, self.anchor_domain,
            self.orientation, self.route_family, self.K, self.polarity,
            self.hierarchy_level)
        return self.neighborhood


# ---- Hopfield-style associative completion (tiny, deterministic) ----

def hopfield_complete(cue: set[str], patterns: list[set[str]], max_iter: int = 20) -> set[str]:
    """Settle a partial cue toward the nearest stored pattern.
    Simple overlap attractor. Not a full Hopfield net — just the completion job."""
    if not patterns:
        return set(cue)
    best = max(patterns, key=lambda p: len(cue & p))
    # if cue already matches best, done
    state = set(cue)
    for _ in range(max_iter):
        # reinforce features present in best that are also in cue neighborhood
        new_state = set(state)
        for f in best:
            if f in cue or any(f in p for p in patterns if len(p & state) > 0):
                new_state.add(f)
        if new_state == state:
            break
        state = new_state
    return state


# ---- Boltzmann-style probabilistic fill (marked uncertain) ----

def boltzmann_fill(partial: set[str], candidates: list[str], temp: float = 0.5,
                   seed: int = 0) -> tuple[set[str], float]:
    """Propose missing features. Returns (filled, confidence). Confidence < 1.0 means uncertain."""
    rng = random.Random(seed)
    filled = set(partial)
    missing = [c for c in candidates if c not in partial]
    added = 0
    for c in missing:
        if rng.random() < temp:
            filled.add(c)
            added += 1
    confidence = 1.0 - (added / max(len(missing), 1)) * 0.5
    return filled, confidence


# ---- State-machine validation (context / acceptance) ----

def validate(rebuilt: set[str], original: set[str], context: set[str]) -> str:
    """Decide accept / uncertain / reject."""
    overlap = len(rebuilt & original) / max(len(original), 1)
    ctx_conflict = len(rebuilt & context) == 0 and len(context) > 0
    if overlap >= 0.8 and not ctx_conflict:
        return "accept"
    if overlap >= 0.5:
        return "uncertain"
    return "reject"


# ---- Receipt ----

@dataclass
class RebuildReceipt:
    cue: set[str]
    mem_id: str
    neighborhood_traversed: list[tuple]
    mirrors_used: list[int]
    hopfield_contribution: set[str]
    boltzmann_fill: set[str]
    boltzmann_confidence: float
    validation: str
    invertible: bool = True


# ---- Engine ----

class MemoryEngine:
    def __init__(self):
        self.memories: dict[str, Memory] = {}
        self.context: set[str] = set()

    def store(self, mem: Memory):
        mem.build_neighborhood()
        self.memories[mem.mem_id] = mem

    def recall(self, cue: set[str], mem_id: Optional[str] = None) -> RebuildReceipt:
        # 1. constellation neighborhood
        if mem_id and mem_id in self.memories:
            target = self.memories[mem_id]
            patterns = [m.features for m in self.memories.values()]
        else:
            target = None
            patterns = [m.features for m in self.memories.values()]

        # 2. rabbit-hop route: traverse recorded neighborhood
        neighborhood_traversed = []
        mirrors_used = []
        if target:
            for p in target.neighborhood:
                neighborhood_traversed.append(p.as_tuple())
                if p.polarity < 0:
                    mirrors_used.append(p.polarity)

        # 3. Hopfield completion
        completed = hopfield_complete(cue, patterns)
        hop_contrib = completed - cue

        # 4. Boltzmann fill if ambiguity remains
        all_features = set()
        for m in self.memories.values():
            all_features |= m.features
        filled, conf = boltzmann_fill(completed, list(all_features))
        bolt_contrib = filled - completed

        # 5. validate
        original = target.features if target else set()
        validation = validate(filled, original, self.context)

        # 6. receipt — must be invertible via stored route metadata
        receipt = RebuildReceipt(
            cue=cue,
            mem_id=target.mem_id if target else "unknown",
            neighborhood_traversed=neighborhood_traversed,
            mirrors_used=mirrors_used,
            hopfield_contribution=hop_contrib,
            boltzmann_fill=bolt_contrib,
            boltzmann_confidence=conf,
            validation=validation,
            invertible=bool(target and target.neighborhood),
        )
        return receipt


# ---- Tests ----

def test_store_and_partial_cue_recall():
    eng = MemoryEngine()
    m1 = Memory("M1", {"red", "loud", "moving", "kitchen"}, "A")
    m2 = Memory("M2", {"blue", "quiet", "still", "kitchen"}, "B")  # overlaps on kitchen
    eng.store(m1)
    eng.store(m2)
    cue = {"red", "kitchen"}  # partial cue for M1
    r = eng.recall(cue, "M1")
    assert r.mem_id == "M1"
    assert "loud" in r.hopfield_contribution or "moving" in r.hopfield_contribution
    assert r.invertible is True
    assert len(r.neighborhood_traversed) == 2  # two wrapper packets


def test_no_collapse_of_similar_memories():
    eng = MemoryEngine()
    m1 = Memory("M1", {"red", "loud", "moving"}, "A")
    m2 = Memory("M2", {"red", "quiet", "still"}, "B")  # similar but distinct
    eng.store(m1)
    eng.store(m2)
    cue = {"red"}
    r1 = eng.recall(cue, "M1")
    r2 = eng.recall(cue, "M2")
    # they must not both claim the other's unique features as certain
    assert "loud" not in r2.hopfield_contribution or r2.validation != "accept"
    assert "quiet" not in r1.hopfield_contribution or r1.validation != "accept"


def test_receipt_inverts_route():
    eng = MemoryEngine()
    m = Memory("M1", {"alpha", "beta", "gamma"}, "A", route_family="A", K=2)
    eng.store(m)
    r = eng.recall({"alpha"}, "M1")
    # invert: from receipt neighborhood, recover source
    assert r.invertible
    # reconstruct N from first packet center using stored family/K
    first = r.neighborhood_traversed[0]
    N_rec = (first[1] - m.K) / 2   # family A: T = 2N + K
    assert N_rec == label_to_rank("A")


def test_boltzmann_marked_uncertain():
    eng = MemoryEngine()
    m = Memory("M1", {"x", "y"}, "A")
    eng.store(m)
    r = eng.recall(set(), "M1")  # empty cue -> heavy fill
    if r.boltzmann_fill:
        assert r.boltzmann_confidence < 1.0
        assert r.validation in ("uncertain", "reject")


def test_missing_branch_visible():
    # if neighborhood is empty, receipt flags non-invertible
    eng = MemoryEngine()
    m = Memory("M1", {"a"}, "A")
    m.neighborhood = []  # corrupted / missing branch
    eng.memories["M1"] = m
    r = eng.recall({"a"}, "M1")
    assert r.invertible is False


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS  {name}")
    print("All Memory Rebuild tests passed.")
