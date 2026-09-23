#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Sweep an LNA macro's sizing knobs through VACASK small-signal runs, NF and Gm per point

"""What the sizing knobs buy an LNA, measured rather than estimated.

    python3 scripts/lna_sweep.py --macro . [--write]

The macro's `scripts/<top>_sizing.py` supplies `design(**kw)`, `inc_text(d)`,
`sweep_points()` (a list of kwargs dicts) and `sweep_columns(d)` (an ordered
dict of label to value for the table). Every point re-sizes the LNA, writes
its include beside a small-signal-only copy of the netlisted `<top>_tb_sp`
bench, runs VACASK (op, acsp, ac, noise: milliseconds) and reads S11, Gm and
NF back. The netlist is parameterised, so `make netlist-vacask` netlists it
once and this never touches it.

NF is reported with the bench's own load resistor taken out of the output
noise, because that resistor stands in for the mixer and the converter.
"""

import argparse
import importlib
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

F0 = 2.44e9


def small_signal_deck(text):
    """Drop the HB analyses and the alters, keep op, acsp, ac and noise."""
    keep = [line for line in text.splitlines()
            if not line.strip().startswith(("analysis hb", "alter instance", "sweep "))]
    return "\n".join(keep) + "\n"


def run_point(deck_text, inc_text, inc_name, deck_name, workdir):
    from rawfile import rawread
    with open(os.path.join(workdir, deck_name), "w") as fh:
        fh.write(deck_text)
    with open(os.path.join(workdir, inc_name), "w") as fh:
        fh.write(inc_text)
    r = subprocess.run(["vacask", deck_name], cwd=workdir, capture_output=True, text=True)
    if re.search(r"aborted|failed|error", r.stdout + r.stderr, re.I) \
            or not os.path.exists(os.path.join(workdir, "n1.raw")):
        return None
    op = rawread(os.path.join(workdir, "op1.raw")).get()
    idd = -float(np.real(op["vsup:flow(br)"][0]))
    sp = rawread(os.path.join(workdir, "sp1.raw")).get()
    f = np.real(sp["frequency"])
    k = np.argmin(abs(f - F0))
    s11 = 20 * np.log10(abs(sp["s(1,1)"][k]))
    ac = rawread(os.path.join(workdir, "ac1.raw")).get()
    f = np.real(ac["frequency"])
    k = np.argmin(abs(f - F0))
    gm_eff = abs(ac["vout"][k]) / 200.0 / 0.5
    nz = rawread(os.path.join(workdir, "n1.raw")).get()
    f = np.real(nz["frequency"])
    k = np.argmin(abs(f - F0))
    tot, src, load = nz["onoise"][k], nz["n(rs)"][k], nz["n(rl)"][k]
    return dict(idd=idd, s11=s11, gm_eff=gm_eff,
                nf=10 * np.log10((tot - load) / src),
                nf_with_load=10 * np.log10(tot / src))


def sweep(macro, points="sweep"):
    top = os.path.basename(os.path.abspath(macro))
    sys.path.insert(0, os.path.join(macro, "scripts"))
    sz = importlib.import_module(top + "_sizing")
    deck_path = os.path.join(macro, "testbenches", "xschem", "simulations", top + "_tb_sp.spectre")
    with open(deck_path) as fh:
        deck = small_signal_deck(fh.read())
    pdk = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"])
    rows = []
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(pdk, "libs.tech", "vacask", ".vacaskrc.toml")) as fh:
            rc = fh.read()
        with open(os.path.join(d, ".vacaskrc.toml"), "w") as fh:
            fh.write(rc)
        pts = sz.robust_points() if points == "robust" else sz.sweep_points()
        cols = sz.robust_columns if points == "robust" else sz.sweep_columns
        for kw in pts:
            try:
                des = sz.design(**kw)
            except ValueError as e:
                # a point the sizing cannot match is a result, not a crash
                rows.append((sz.sweep_columns_unmatched(kw, str(e)), None))
                continue
            m = run_point(deck, sz.inc_text(des), top + "_sizes.inc", top + "_tb_sp.spectre", d)
            rows.append((cols(des), m))
    return top, rows


def table(rows):
    labels = list(rows[0][0].keys())
    out = ["| " + " | ".join(labels) + " | **NF dB** | NF with load dB | Gm,eff mS | S11 at F0 dB | Idd mA |",
           "|" + "---|" * (len(labels) + 5)]
    for cols, m in rows:
        head = " | ".join(str(v) for v in cols.values())
        if m is None:
            out.append("| %s | aborted | | | | |" % head)
            continue
        out.append("| %s | **%.2f** | %.2f | %.1f | %.1f | %.2f |"
                   % (head, m["nf"], m["nf_with_load"], m["gm_eff"] * 1e3, m["s11"], m["idd"] * 1e3))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--macro", required=True)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--points", choices=("sweep", "robust"), default="sweep",
                    help="robust: the nominal design with one thing moved at a time, from <top>_sizing.robust_points()")
    a = ap.parse_args()
    top, rows = sweep(a.macro, a.points)
    body = table(rows)
    print(body)
    if a.write:
        if a.points == "robust":
            doc = os.path.join(a.macro, "doc", top + "_robust.md")
            head = ("Description: %s robustness, the nominal design with one thing moved at a time, measured in VACASK\n-->\n\n"
                    "# %s robustness\n\nGenerated by `scripts/lna_sweep.py --macro macros/%s --points robust`, rebuild with "
                    "`make robust`. Small-signal VACASK at TT, 27 C, the nominal sizes throughout: each row moves one "
                    "thing the way a part tolerance, the pad's spread, a reference-current error or the load node's "
                    "parasitics would, see `robust_points()` in `scripts/%s_sizing.py`. NF excludes the bench load."
                    % (top, top, top, top))
        else:
            doc = os.path.join(a.macro, "doc", top + "_sweep.md")
            head = ("Description: %s sizing sweep, NF and Gm measured in VACASK per point\n-->\n\n"
                    "# %s sizing sweep\n\nGenerated by `scripts/lna_sweep.py --macro macros/%s`, rebuild with "
                    "`make sweep`. Small-signal VACASK at TT, 27 C, every point re-sized by "
                    "`scripts/%s_sizing.py`. NF excludes the bench load, which stands in for the "
                    "mixer and converter." % (top, top, top, top))
        with open(doc, "w") as fh:
            fh.write("<!--\nSPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University\n"
                     "SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1\n" + head + "\n\n" + body + "\n")
        print("wrote %s" % doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
