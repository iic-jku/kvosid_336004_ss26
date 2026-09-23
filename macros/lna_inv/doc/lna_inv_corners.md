<!--
SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
Description: Inverter LNA over process, supply and temperature, and against part and parasitic spread
-->

# Inverter LNA over corners

Corner set: [`../verification/cace/lna_inv.yaml`](../verification/cace/lna_inv.yaml), rebuild with `make sim-cace` (`make sim-cace-all` runs every set). Robustness: [`lna_inv_robust.md`](lna_inv_robust.md), rebuild with `make robust`.
ngspice-47 for the corners and VACASK a9d8860 for the robustness rows, both in `hpretl/iic-osic-tools:2026.08` (`cbd5fcd93335`), schematic level. The sizes reach the CACE template as datasheet conditions that `scripts/lna_inv_sizing.py --write` keeps in step with `schematic/xschem/lna_inv_sizes.inc`, so the corner set and the VACASK benches run the same device.

## The set

45 points: MOS `ss`/`sf`/`tt`/`fs`/`ff` against VDD 1.08/1.20/1.32 V against -40/27/125 C, resistor and capacitor corners at `typ`.

**One set.** The pair self-biases at its own trip point through `RF`, so there is no bias node to drive and no second bias variant to put beside the first. The resistor corner would be the nearest thing to one, since `RF` sets the bias and the match together, but [`../scripts/cace_table.py`](../scripts/cace_table.py) reports a point by MOS corner, VDD and temperature only, so a set that varied `corner_r` would come out with three indistinguishable rows per condition. `RF` spread is covered in the robustness table instead.

Small signal only: supply current, S11 from the ac input impedance, transconductance into the 200 ohm mixer-side stand-in, and noise figure with that load noiseless. **IIP3 and P1dB are not in the set.** They need harmonic balance, which this ngspice flow does not run, so they stay at TT in [`lna_inv_feasibility.md`](lna_inv_feasibility.md).

## Worst case

Full table, all 45 points: [`../verification/cace/results/lna_inv/corners.md`](../verification/cace/results/lna_inv/corners.md).

| | nominal, `tt` 1.20 V 27 C | worst | at | asked |
|---|---|---|---|---|
| noise figure | 4.39 dB | **7.82 dB** | `ss`, 1.08 V, -40 C | 2.5 dB, missed at every point |
| S11 at 2.44 GHz | -25.96 dB | **-8.21 dB** | `ss`, 1.08 V, -40 C | < -10 dB, missed at 1 of 45 |
| transconductance | 17.93 mS | **7.80 mS** | `ss`, 1.08 V, -40 C | frame set by the chain |
| supply current | 3.63 mA | **12.53 mA** | `ff`, 1.32 V, 125 C | 5.0 mA, and 0.32 mA at the other end |
| IIP3, P1dB | +5.3, -9.1 dBm at TT | not in the set | | harmonic balance only |

The `tt`, 1.20 V, 27 C point of the corner set reads 4.39 dB, -25.96 dB, 17.93 mS and 3.63 mA against the VACASK bench's 4.36 dB, -28.0 dB, 18.2 mS and 3.63 mA, so the two decks agree on the nominal device to within the S11 null's own sharpness.

## Robustness

[`lna_inv_robust.md`](lna_inv_robust.md), eleven rows at TT and 27 C on the nominal sizes, one thing moved per row: shunt part +-5 %, pad +-20 %, device width +-20 %, feedback resistor +-20 %, and the mixer-side load node at +100 and +200 fF. `robust_points()` in [`../scripts/lna_inv_sizing.py`](../scripts/lna_inv_sizing.py) is the source of the rows. The width row is what the current follows, since the inverter has no reference current to move.

Nothing there moves the block far: NF spans 4.14 to 4.70 dB, S11 stays below -19.8 dB, and Gm stays between 16.7 and 19.3 mS. The load node is the mildest of them, -1.1 mS of Gm for 200 fF, which is the shunt-feedback stage's low output impedance absorbing it.

## What the numbers say

**The spread is the current, and nothing in this topology holds it.** The pair sits wherever the trip point lands, so the current is a threshold-and-supply function with no feedback around it: 0.32 mA at `ss`, 1.08 V, -40 C against 12.53 mA at `ff`, 1.32 V, 125 C, a factor of 39, and 3.9x from the supply alone at fixed process and temperature. Everything else tracks it monotonically: the starved corner is the same one that puts noise figure at 7.82 dB and the match at -8.21 dB, the only point of 45 that misses -10 dB, while the rich corner buys 3.87 dB of noise figure for 12.5 mA. The part and parasitic spread, by contrast, is a non-issue, which says the design is not fragile, it is unregulated. That is the item to close before this candidate is comparable to the common source on anything but area: the block needs its current set rather than inherited, and until it is, the numbers to carry into the level plan are the corner column and not the TT one.
