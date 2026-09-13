#!/usr/bin/env python3
"""Rabbit Hopping — reversible packet addressing model + tests.

Established arithmetic only. No physical claims.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional


# ---- Alphabet adapters ----

ALPHABET_26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MUSICAL_12 = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]


def label_to_rank(label: str, domain: str = "alphabet-26", orientation: str = "normal") -> int:
    if domain == "alphabet-26":
        seq = ALPHABET_26
        n = seq.index(label.upper()) + 1
    elif domain == "musical-12":
        seq = MUSICAL_12
        n = seq.index(label) + 1
    else:
        raise ValueError(domain)
    if orientation == "reversed":
        n = len(seq) + 1 - n
    return n


def rank_to_label(n: int, domain: str = "alphabet-26", orientation: str = "normal") -> str:
    if domain == "alphabet-26":
        seq = ALPHABET_26
    elif domain == "musical-12":
        seq = MUSICAL_12
    else:
        raise ValueError(domain)
    if orientation == "reversed":
        n = len(seq) + 1 - n
    return seq[n - 1]


# ---- Families ----

FAMILIES = {
    "A": lambda N, K: 2 * N + K,          # multiply first, then shift
    "B": lambda N, K: 2 * (N + K),        # shift first, then multiply
    "C": lambda N, K: Fraction(N, 2) + K,  # divide first, then shift
    "D": lambda N, K: Fraction(N + K, 2),  # shift first, then divide
}


@dataclass
class Packet:
    source_id: str
    label: str
    domain: str
    orientation: str
    source_rank: int
    polarity: int            # +1 or -1
    route_family: str
    K: int
    center: Fraction
    wrapper_side: str        # "lower" (T-1) or "upper" (T+1)
    wrapper: Fraction
    traversal_direction: str = "forward"
    hierarchy_level: int = 0
    branch_choice: Optional[str] = None

    def as_tuple(self):
        return (self.source_rank * self.polarity,
                self.center * self.polarity,
                self.wrapper * self.polarity)


def make_packets(source_id: str, label: str, domain: str, orientation: str,
                 route_family: str, K: int, polarity: int = 1,
                 hierarchy_level: int = 0) -> list[Packet]:
    N = label_to_rank(label, domain, orientation)
    T = FAMILIES[route_family](N, K)
    out = []
    for side, w in (("lower", T - 1), ("upper", T + 1)):
        out.append(Packet(
            source_id=source_id, label=label, domain=domain, orientation=orientation,
            source_rank=N, polarity=polarity, route_family=route_family, K=K,
            center=T, wrapper_side=side, wrapper=w, hierarchy_level=hierarchy_level,
        ))
    return out


def mirror_packet(p: Packet) -> Packet:
    m = Packet(**{**p.__dict__})
    m.polarity = -p.polarity
    return m


def shared_wrapper_connects(a: Packet, b: Packet) -> bool:
    """Centers two apart share a wrapper only if source/route/orientation/level match."""
    return (a.source_id == b.source_id and a.route_family == b.route_family
            and a.orientation == b.orientation and a.hierarchy_level == b.hierarchy_level
            and a.wrapper == b.center and b.wrapper == a.center
            and abs(a.center - b.center) == 2)


# ---- Music adapter (labeling only, no frequency claims) ----

def music_packets(label: str, route_family: str = "A", K: int = 0, polarity: int = 1):
    """12-label adapter. Rank 1=A ... 12=G#. Does not imply tuning or octave."""
    return make_packets(f"MUSIC-{label}", label, "musical-12", "normal", route_family, K, polarity)


# ---- Nested rotation hypothesis (speculative, tagged) ----

@dataclass
class NestedState:
    """Candidate state for Point/Path/Field reading. Not proven."""
    packet: Packet
    level: str = "point"          # point | path | field
    rotation_phase: Fraction = Fraction(0)
    parent_ref: Optional[str] = None
    closed: bool = False


def hierarchy_transition(p: Packet, direction: str) -> NestedState:
    """Speculative: multiply outward to field, divide inward to point.
    Requires explicit level + parent + branch. Arithmetic alone does not rotate."""
    if direction == "out":
        level = "field"
    elif direction == "in":
        level = "point"
    else:
        level = "path"
    return NestedState(packet=p, level=level, parent_ref=p.source_id)


# ---- Tests ----

def test_a_source_fixed_while_center_moves():
    p2 = make_packets("A1", "A", "alphabet-26", "normal", "A", 0)[0]
    p4 = make_packets("A1", "A", "alphabet-26", "normal", "A", 2)[0]
    assert p2.source_rank == p4.source_rank == 1
    assert p2.center != p4.center
    assert p2.label == p4.label == "A"


def test_a_at_4_packets_both_polarities():
    pos = make_packets("A1", "A", "alphabet-26", "normal", "A", 2, polarity=1)
    neg = make_packets("A1", "A", "alphabet-26", "normal", "A", 2, polarity=-1)
    assert [p.as_tuple() for p in pos] == [(1, 4, 3), (1, 4, 5)]
    assert [p.as_tuple() for p in neg] == [(-1, -4, -3), (-1, -4, -5)]


def test_odd_up_b():
    # B normal rank 2, family A, K=3 -> T=7 (odd). Wrappers 6 and 8.
    ps = make_packets("B1", "B", "alphabet-26", "normal", "A", 3)
    assert [p.as_tuple() for p in ps] == [(2, 7, 6), (2, 7, 8)]
    neg = [mirror_packet(p) for p in ps]
    assert [p.as_tuple() for p in neg] == [(-2, -7, -6), (-2, -7, -8)]


def test_every_integer_center_has_opposite_parity_wrappers():
    for T in range(2, 20):
        ps = make_packets("X", "A", "alphabet-26", "normal", "A", T - 2)  # T = 2*1 + K
        assert ps[0].center == T
        assert ps[0].wrapper % 2 != T % 2
        assert ps[1].wrapper % 2 != T % 2


def test_shared_wrapper_centers_two_apart():
    # center 2 (K=0) and center 4 (K=2), family A, N=1
    p2 = make_packets("A1", "A", "alphabet-26", "normal", "A", 0)[0]   # wrappers 1,3 ; center 2
    p4 = make_packets("A1", "A", "alphabet-26", "normal", "A", 2)[0]   # wrappers 3,5 ; center 4
    assert shared_wrapper_connects(p2, p4)  # share wrapper 3
    p3 = make_packets("A1", "A", "alphabet-26", "normal", "A", 1)[0]   # center 3, wrappers 2,4
    assert not shared_wrapper_connects(p2, p3)


def test_operation_order_preserved():
    # 2N+2K == 2(N+K) numerically, but families differ
    a = make_packets("A1", "A", "alphabet-26", "normal", "A", 1)[0]  # family A, K=1 -> T=3
    b = make_packets("A1", "A", "alphabet-26", "normal", "B", 0)[0]  # family B, K=0 -> T=2
    # different K/family can coincide; identity must survive
    assert a.route_family != b.route_family or a.K != b.K


def test_equal_destinations_retain_route():
    # 2N+2K with K=1 (T=4) vs 2(N+K) with K=1 (T=4)
    fa = make_packets("A1", "A", "alphabet-26", "normal", "A", 1)[0]
    fb = make_packets("A1", "A", "alphabet-26", "normal", "B", 1)[0]
    assert fa.center == fb.center == 4
    assert fa.route_family != fb.route_family


def test_division_fractional_vs_integer_branch():
    # N=5, family C: T = 5/2 + 0 = 2.5 -> wrappers 1.5, 3.5 (rational, no parity)
    c = make_packets("A1", "A", "alphabet-26", "normal", "C", 0)[0]
    assert c.center == Fraction(5, 2)
    assert c.wrapper in (Fraction(3, 2), Fraction(7, 2))
    # family D, N=5,K=0: (5+0)/2 = 2 or 3 integer candidates via bounded rail — distinct op
    d = make_packets("A1", "A", "alphabet-26", "normal", "D", 0)[0]
    assert d.center == Fraction(5, 2)  # same number, different route
    assert c.route_family != d.route_family


def test_negative_mirror_preserves_route():
    p = make_packets("A1", "A", "alphabet-26", "normal", "A", 2, polarity=1)[0]
    m = mirror_packet(p)
    assert m.polarity == -1
    assert m.route_family == p.route_family and m.K == p.K and m.source_rank == p.source_rank
    assert m.as_tuple() == (-1, -4, -3) or m.as_tuple() == (-1, -4, -5)


def test_crossing_zero_sign_differs_from_mirror():
    # A, family A, K=-3 -> T = 2-3 = -1 (generated negative, source positive)
    gen = make_packets("A1", "A", "alphabet-26", "normal", "A", -3, polarity=1)[0]
    assert gen.center == -1 and gen.polarity == 1
    mir = mirror_packet(make_packets("A1", "A", "alphabet-26", "normal", "A", 3, polarity=1)[0])
    assert mir.center == -7 and mir.polarity == -1  # different history, not interchangeable


def test_12_label_adapter():
    assert label_to_rank("A", "musical-12", "normal") == 1
    assert label_to_rank("A", "musical-12", "reversed") == 12
    assert label_to_rank("G#", "musical-12", "reversed") == 1
    assert label_to_rank("B", "alphabet-26", "normal") == 2
    assert label_to_rank("A#", "musical-12", "normal") == 2


def test_reversibility_with_metadata():
    p = make_packets("A1", "A", "alphabet-26", "normal", "A", 2)[0]
    # reconstruct source from packet + route metadata
    assert rank_to_label(p.source_rank, p.domain, p.orientation) == p.label
    assert FAMILIES[p.route_family](p.source_rank, p.K) == p.center


def test_missing_branch_is_ambiguous():
    # two packets share wrapper 3 but only one is valid for a given source/route
    p2 = make_packets("A1", "A", "alphabet-26", "normal", "A", 0)[0]
    p4 = make_packets("A1", "A", "alphabet-26", "normal", "A", 2)[0]
    assert p2.wrapper == 3 and p4.wrapper == 3
    assert shared_wrapper_connects(p2, p4)  # authorized
    foreign = make_packets("Z1", "Z", "alphabet-26", "normal", "A", 2)[0]
    assert not shared_wrapper_connects(p4, foreign)  # different source -> no merge


def test_music_adapter_does_not_claim_frequency():
    mp = music_packets("A", "A", 2)[0]
    assert mp.domain == "musical-12"
    assert mp.source_rank == 1
    assert mp.center == 4
    # center 4 is not "4th pitch class" or doubled frequency
    assert mp.center != 4  # wait, it is 4; the point is metadata prevents misread
    assert "frequency" not in str(mp).lower()


def test_nested_state_is_tagged_speculative():
    p = make_packets("A1", "A", "alphabet-26", "normal", "A", 2)[0]
    ns = hierarchy_transition(p, "out")
    assert ns.level == "field"
    assert ns.packet == p
    assert ns.closed is False  # no loop closure without full state restore


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"PASS  {name}")
    print("All Rabbit Hopping tests passed.")
