# CELL-0 — primitive mirror + magnetic hold

Body state first. One pair. One square-loop core. No extra steps.

## Law

- Asymmetry past the fence → move
- Balance inside the fence → hold
- D = DB − DC is the live state of the pair
- Packet agreement (N, family, polarity) is the receipt, not another IC
- Drive = volts available on 2N7000 / BS170
- Sense = millivolts on D (meter). Not a millivolt MOSFET (does not exist as a jellybean)

## Netlist

```
VCC (+5 V USB or 7805 from 4xAA). Never 12 V on these gates.

R1 10k : VCC — DB (Q1 drain)
R2 10k : VCC — DC (Q2 drain)
Q1, Q2 : 2N7000 or BS170
Q1 source + Q2 source = CENTER
Square-loop ferrite core on CENTER lead (memory/magamp core, NOT EMI bead)
Do NOT tie CENTER to GND until T3 is written.

R3 100k : Q1 gate (B) — GND   (anti-float)
R4 100k : Q2 gate (C) — GND
C1 100nF : VCC — GND at rail entry

Optional R27: 27Ω + 1k series from DC toward CENTER.
Omit if rest D is yanked out of the dead zone.
```

```
        VCC
       /   \
     R1     R2
      |     |
     DB     DC
      |     |
     Q1     Q2
      |     |
      +--+--+  CENTER ----[ square-loop core ]---- (header, not GND yet)
      |
   bleeds to GND on gates B and C
```

Q1 and Q2 are **mirror gates**: same part, sources on CENTER, one drain is the sign-flipped view of the other.

## BOM

| Ref | Part | Qty |
|-----|------|-----|
| Q1 Q2 | 2N7000 or BS170 | 2 |
| R1 R2 | 10 kΩ 1/4 W | 2 |
| R3 R4 | 100 kΩ | 2 |
| C1 | 100 nF ceramic | 1 |
| Core | square-loop memory/magamp toroid | 1 |
| Board | 400-point breadboard | 1 |
| Meter | DMM, mV range | 1 |
| Optional | 27 Ω + 1 kΩ (R27 path) | 1+1 |

Core must say square-loop / memory / magamp. Fair-Rite 43 / PSU yellow toroid / cable bead = reject. See FERRITE.md.
Example surplus: ~1.25 mm memory cores, flip ~0.3 A·turn. If pair current cannot beat Hc, the magnet is decoration.

## Forbidden on Cell-0

- LM393, 74HC74, op-amp gain, window ICs
- Tying CENTER to GND before T3
- 12 V on gates
- Second pair before T5
- Calling EMI ferrite "magnetic memory"
- Calling this ternary because you typed three words

## Tests (write numbers in LOG.md)

**T1** Power off. B–GND and C–GND are not open. Fail = floating gate. Stop.

**T2** Rails on, both gates low through bleeds. DB and DC sit near VCC. Either at 0 V → FET on or shorted. Stop.

**T3** Drive B with available voltage (~3–5 V), C low. DB must fall. Write DB, DC, D. If D does not move, no differential. Stop.

**T4** Swap: C high, B low. D must reverse sign. Fail = not a mirror.

**T5** While D has a clear sign, remove VCC. Check leftover field on the core (sense turn to scope, Hall, compass). Restore VCC. Remanence must match last D sign. This is magnetic hold. Fail = wrong ferrite or H < Hc.

T3 written = first hardware evidence.
T5 twice on two days = primitive cell.
Do not start M4 ring until T5 passes once.

## Ternary (only after T3)

Window on D, not a third MOSFET well:

- D > +T → up
- D < −T → down
- |D| ≤ T → stay / hold

Write T next to the first traces. Start T in **tens of mV**, not 1 mV. kT/q is ~26 mV.
