# CELL-0 — primitive mirror + magnetic hold

Body state first. One pair. One square-loop core. No extra steps.

**Voltage: whatever the parts already take.** Right now that is a rechargeable 9 V and 2N7000 / BS170. Millivolt gates are future/funding. Do not design Cell-0 around them.

## Law

- Asymmetry past the fence → move
- Balance inside the fence → hold
- D = DB − DC is the live state of the pair
- Packet agreement is the receipt, not another IC
- Drive a gate from the same 9 V pack, or leave it on the bleed to GND

## Netlist

```
VCC = one rechargeable 9 V battery +
GND = that battery −

R1 10k : VCC — DB (Q1 drain)
R2 10k : VCC — DC (Q2 drain)
Q1, Q2 : 2N7000 or BS170
Q1 source + Q2 source = CENTER
Square-loop ferrite on CENTER (memory/magamp, NOT EMI bead)
Do NOT tie CENTER to battery − until T3 is written.

R3 100k : Q1 gate (B) — GND
R4 100k : Q2 gate (C) — GND
C1 100nF : VCC — GND at the battery clip
```

```
        9V+
       /   \
     R1     R2
      |     |
     DB     DC     meter here
      |     |
     Q1     Q2
      |     |
      +--+--+  CENTER ----[ square-loop core ]---- header
                         (not battery minus)
```

## BOM

| Ref | Part | Qty |
|-----|------|-----|
| Q1 Q2 | 2N7000 or BS170 | 2 |
| R1 R2 | 10 kΩ | 2 |
| R3 R4 | 100 kΩ | 2 |
| C1 | 100 nF | 1 |
| Core | square-loop memory/magamp toroid | 1 |
| Power | one rechargeable 9 V | 1 |
| Board | 400-point breadboard | 1 |
| Meter | DMM, ordinary volts is enough | 1 |

## Tests — LOG.md

T1 gates not floating.
T2 both gates low: DB and DC near 9 V.
T3 gate B to 9 V, C low: DB falls. Write DB, DC, D. Any volts the meter shows.
T4 swap gates: D reverses sign.
T5 rails off: leftover field on the core matches last D sign.

No extra chips. No millivolt hunt. Parts that exist.
