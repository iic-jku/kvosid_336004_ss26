#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Tabulate one CACE parameter set per run point and name the worst corner per variable

"""Read a CACE run directory before `make sim-cace` deletes it.

    python3 cace_table.py <_runs/RUN_x/parameters/<set>> <out.md> --vars idd_ma s11_db gm_ms nf_db

CACE's own summary keeps only min, typ and max per spec. This keeps every
point with its conditions, so the worst case has a corner name next to it.
The variables are the datasheet's `variables:` in order, echoed in base
units; a `_ma` or `_ms` suffix scales the display by 1e3, and the worst case
is the maximum unless the name says `gm`, where it is the minimum.
"""

import argparse
import glob
import os
import sys

import yaml


def scale(name):
    return 1e3 if name.endswith(("_ma", "_ms")) else 1.0


def worst(name):
    return min if "gm" in name else max


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rundir")
    ap.add_argument("out")
    ap.add_argument("--vars", nargs="+", required=True)
    a = ap.parse_args()
    rows = []
    for d in sorted(glob.glob(os.path.join(a.rundir, "run_*"))):
        with open(os.path.join(d, "conditions.yaml")) as fh:
            c = yaml.safe_load(fh)
        data = glob.glob(os.path.join(d, "*.data"))
        if not data:
            continue
        with open(data[0]) as fh:
            vals = [float(x) for x in fh.read().split()]
        if len(vals) != len(a.vars):
            continue
        cond = {k: (c[k]["value"] if isinstance(c[k], dict) else c[k])
                for k in ("corner_mos", "vdd", "temp") if k in c}
        rows.append((cond, dict(zip(a.vars, vals))))
    L = ["| MOS | VDD V | T C | " + " | ".join(a.vars) + " |", "|---|---|---|" + "---|" * len(a.vars)]
    for cond, v in rows:
        L.append("| %s | %s | %s | " % (cond.get("corner_mos"), cond.get("vdd"), cond.get("temp"))
                 + " | ".join("%.2f" % (v[k] * scale(k)) for k in a.vars) + " |")
    L.append("")
    for k in a.vars:
        pick = worst(k)(rows, key=lambda r: r[1][k])
        L.append("- worst %s: %.2f at %s, %s V, %s C" % (
            k, pick[1][k] * scale(k), pick[0].get("corner_mos"), pick[0].get("vdd"), pick[0].get("temp")))
    with open(a.out, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote %s (%d points)" % (a.out, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
