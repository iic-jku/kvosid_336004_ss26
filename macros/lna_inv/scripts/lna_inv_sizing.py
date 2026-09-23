#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: gm/Id sizing of the coil-free resistive-feedback inverter LNA, first cut

"""Size the inverter LNA and write the parameter include.

Topology: an NMOS and a PMOS sharing gate and drain, so both transconductances
act on the same current, with a feedback resistor from drain to gate that
sets the input impedance and biases the pair at its own trip point. No coil
anywhere: the input is broadband, which the level plan can live with since
the tuned LNA measured no selectivity either, and the antenna pad carries the
same shared-pad capacitance and off-chip shunt coil, vendored below.

The match depends on the load, which is the point to remember: with a load
RL at the drain and the pair's output resistance ro,

    Rin = (Rf + RL') / (1 + gm RL'),   RL' = RL || ro

so Rf is solved for 50 ohm against the bench's 200 ohm stand-in, and the real
mixer will read differently. The bench decides the noise, the estimate below
only ranks: 1 + RS/Rf + gamma_eff/(gm RS).

    python3 lna_inv_sizing.py            # print
    python3 lna_inv_sizing.py --write    # ../schematic/xschem/lna_inv_sizes.inc
"""

import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MACRO = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MACRO))
sys.path.insert(0, HERE)

import gmid_lut                      # noqa: E402

# The receiver level plan is not part of this repo. Without it the sizing still
# runs, only the target line is dropped.
try:
    import rx_level_plan as LP       # noqa: E402
except ImportError:
    LP = None

# Antenna pad and off-chip shunt coil, vendored from the common-source LNA so
# that this macro stands on its own.
C_PAD = 471e-15          # shared antenna pad capacitance
Q_LSH = 50.0             # wirewound 0402 shunt coil, Q at 2.44 GHz
C_RES = 100e-15          # residual the coil leaves, used as a matching element


def shunt_coil(cpad, lsh=None, q=Q_LSH, c_res=C_RES):
    """The off-chip shunt coil that resonates the pad down to c_res, and its series loss."""
    if lsh is None:
        lsh = 1.0 / (w0() ** 2 * (cpad - c_res)) if cpad > c_res else 0.0
    return lsh, (w0() * lsh / q if lsh else 0.0)

INC = os.path.join(MACRO, "schematic", "xschem", "lna_inv_sizes.inc")
CACE_YAML = os.path.join(MACRO, "verification", "cace", "lna_inv.yaml")

F0 = 2.44e9
RS = 50.0
VDD = 1.2
V_TRIP = VDD / 2.0       # self-biased: gate and drain sit at the same voltage
RL_BENCH = 200.0         # the bench's mixer stand-in at the drain


def w0():
    return 2 * math.pi * F0


def at_trip(dev, L, vgs=V_TRIP, vds=V_TRIP):
    """The LUT point where VGS is the trip voltage: gm/Id found by bisection on the table's VGS."""
    lo, hi = 3.0, 30.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if dev.at(mid, L, vds)["vgs"] > vgs:
            lo = mid           # more gm/Id means less VGS
        else:
            hi = mid
    p = dev.at(0.5 * (lo + hi), L, vds)
    p["gm_id"] = 0.5 * (lo + hi)
    return p


def design(id_a=4.0e-3, L=0.13, rl=RL_BENCH, cpad=C_PAD, lsh=None, lut_dir=None,
           cd=0.0, perturb=None):
    n = gmid_lut.Device("nmos", lut_dir)
    p = gmid_lut.Device("pmos", lut_dir)
    pn, pp = at_trip(n, L), at_trip(p, L)
    wn, wp = id_a / pn["id_w"], id_a / pp["id_w"]          # um, both carry id_a
    gm = pn["gm_w"] * wn + pp["gm_w"] * wp
    gds = pn["gds_w"] * wn + pp["gds_w"] * wp
    ro = 1.0 / gds
    rlp = rl * ro / (rl + ro)
    rf = RS * (1.0 + gm * rlp) - rlp
    if rf <= 0:
        raise ValueError("no feedback resistor matches at %.1f mA: gm %.1f mS into %.0f ohm" % (id_a * 1e3, gm * 1e3, rlp))
    av = (1.0 - gm * rf) * rlp / (rf + rlp)                  # drain over gate, matched input
    gm_eff = abs(av) / rl                                    # output current over the available source voltage
    cin = pn["cgg_w"] * wn + pp["cgg_w"] * wp
    gamma = (pn["gn_w"] * wn + pp["gn_w"] * wp) / gm
    f_est = 1 + RS / rf + gamma / (gm * RS)
    # the pair's gate capacitance sits on the pad node through the dc block,
    # so the shunt coil has to resonate it together with the pad
    lsh_v, rlsh = shunt_coil(cpad + cin, lsh, Q_LSH, c_res=0.0)
    # Robustness: the nominal design with one thing moved, the way a part
    # tolerance, the pad's spread, a width error or the mixer-side node's
    # parasitics would move it. The sizing above is not redone, so the coil
    # still resonates the nominal pad and Rf still matches the nominal load.
    pert = dict(perturb or {})
    if pert.get("w"):
        wn, wp = wn * pert["w"], wp * pert["w"]
    if pert.get("rf"):
        rf = rf * pert["rf"]
    if pert.get("cpad"):
        cpad = cpad * pert["cpad"]
    if pert.get("lsh"):
        lsh_v, rlsh = lsh_v * pert["lsh"], rlsh * pert["lsh"]
    cd = cd + pert.get("cd", 0.0)
    return dict(id=id_a, L=L, wn=wn, wp=wp, gm_id_n=pn["gm_id"], gm_id_p=pp["gm_id"], gm=gm, ro=ro,
                rl=rl, rf=rf, av=av, gm_eff=gm_eff, cin=cin, gamma=gamma,
                nf_est=10 * math.log10(f_est), cpad=cpad, lsh=lsh_v, rlsh=rlsh, cd=cd,
                perturb=pert, ft_n=pn["ft"], ft_p=pp["ft"])


def fingers(w_um, wf=2.0):
    return max(1, int(round(w_um / wf)))


# The channel lengths are LNCH/LPCH, not LN/LP: ngspice reads `l=LN` as its
# own natural-logarithm builtin, and the CACE deck dies inside the PSP card
# with "Undefined parameter [l]" pointing at the model file. VACASK does not
# care, so the VACASK benches ran for weeks on the colliding name.
def inc_text(d):
    return "\n".join([
        "// GENERATED by scripts/lna_inv_sizing.py, do not edit",
        "// Id %.2f mA, gm %.1f mS (n %.1f + p %.1f), Rf %.0f ohm for 50 ohm into the bench's %.0f, NF estimate %.2f dB"
        % (d["id"] * 1e3, d["gm"] * 1e3, d["gm_id_n"] * d["id"] * 1e3, d["gm_id_p"] * d["id"] * 1e3, d["rf"], d["rl"], d["nf_est"]),
        "parameters WN=%.3fu LNCH=%.2fu NGN=%d" % (d["wn"], d["L"], fingers(d["wn"])),
        "parameters WP=%.3fu LPCH=%.2fu NGP=%d" % (d["wp"], d["L"], fingers(d["wp"])),
        "parameters RF=%.4g" % d["rf"],
        "parameters CPAD=%.4gf LSH=%.4gn RLSH=%.4g" % (d["cpad"] * 1e15, d["lsh"] * 1e9, d["rlsh"]),
        "parameters CD=%.4gf" % (d["cd"] * 1e15),
        "parameters CC=10p CBLK=10p",
        "",
    ])


def sweep_points():
    """What scripts/lna_sweep.py runs: the current, and the load the match is solved against."""
    return [dict(id_a=i, rl=rl) for i in (1.5e-3, 2.5e-3, 4.0e-3, 6.0e-3, 8.0e-3) for rl in (RL_BENCH, 100.0)]


def sweep_columns(d):
    return {"Id mA": "%.1f" % (d["id"] * 1e3), "RL ohm": "%.0f" % d["rl"], "Wn um": "%.0f" % d["wn"], "Wp um": "%.0f" % d["wp"],
            "gm mS": "%.1f" % (d["gm"] * 1e3), "ro ohm": "%.0f" % d["ro"], "Rf ohm": "%.0f" % d["rf"],
            "Av dB": "%.1f" % (20 * math.log10(abs(d["av"]))), "NF est dB": "%.2f" % d["nf_est"]}


def robust_points():
    """What scripts/lna_sweep.py --points robust runs: the nominal design with one thing moved at a time.

    The inverter has no bias knob, so where the common source moves its
    reference current this moves the device width, which is what the current
    follows. CD is the mixer-side parasitic at the drain, zero in the nominal
    bench, so only the upward side of it means anything.
    """
    cases = [("nominal", {}),
             ("shunt part +5 %", dict(lsh=1.05)), ("shunt part -5 %", dict(lsh=0.95)),
             ("pad +20 %", dict(cpad=1.2)), ("pad -20 %", dict(cpad=0.8)),
             ("width +20 %", dict(w=1.2)), ("width -20 %", dict(w=0.8)),
             ("feedback R +20 %", dict(rf=1.2)), ("feedback R -20 %", dict(rf=0.8)),
             ("load node +100 fF", dict(cd=100e-15)), ("load node +200 fF", dict(cd=200e-15))]
    return [dict(perturb=dict(pt, label=lbl)) for lbl, pt in cases]


def robust_columns(d):
    return {"case": d["perturb"].get("label", "nominal"),
            "Wn um": "%.0f" % d["wn"], "Wp um": "%.0f" % d["wp"],
            "RF ohm": "%.0f" % d["rf"], "CPAD fF": "%.0f" % (d["cpad"] * 1e15),
            "LSH nH": "%.2f" % (d["lsh"] * 1e9), "CD fF": "%.0f" % (d["cd"] * 1e15)}


def sweep_columns_unmatched(kw, why):
    return {"Id mA": "%.1f" % (kw["id_a"] * 1e3), "RL ohm": "%.0f" % kw.get("rl", RL_BENCH), "Wn um": "", "Wp um": "", "gm mS": "", "ro ohm": "",
            "Rf ohm": "no match", "Av dB": "", "NF est dB": ""}


def cace_conditions(d):
    """The same sizes as CACE datasheet conditions, plain SI numbers.

    CACE substitutes a condition's value as text into the template, and
    `unit:` is display only, so every value here is in base units.
    """
    vals = [("WN", d["wn"] * 1e-6, "m"), ("LNCH", d["L"] * 1e-6, "m"), ("NGN", fingers(d["wn"]), ""),
            ("WP", d["wp"] * 1e-6, "m"), ("LPCH", d["L"] * 1e-6, "m"), ("NGP", fingers(d["wp"]), ""),
            ("RF", d["rf"], "ohm"), ("CPAD", d["cpad"], "F"), ("LSH", d["lsh"], "H"),
            ("RLSH", d["rlsh"], "ohm"), ("CD", d["cd"], "F"),
            ("CC", 10e-12, "F"), ("CBLK", 10e-12, "F")]
    out = ["  # <sizes> written by scripts/lna_inv_sizing.py --write, do not edit"]
    for name, v, unit in vals:
        out.append("  %s:" % name)
        out.append("    description: LNA size from lna_inv_sizing.py")
        out.append("    display: %s" % name)
        if unit:
            out.append("    unit: %s" % unit)
        out.append("    typical: %s" % ("%d" % v if isinstance(v, int) else "%.6g" % v))
    out.append("  # </sizes>")
    return "\n".join(out) + "\n"


def patch_cace(d):
    with open(CACE_YAML) as fh:
        text = fh.read()
    o, c = "  # <sizes>", "  # </sizes>\n"
    i, j = text.index(o), text.index(c) + len(c)
    with open(CACE_YAML, "w") as fh:
        fh.write(text[:i] + cace_conditions(d) + text[j:])


def _st():
    """The level plan's first state set, when the plan is available."""
    return dict(zip(("name", "gain", "nf", "iip3"), LP.STATE_SETS["one"][0]))


def report(d):
    return "\n".join([
        "pair at the trip point %.2f V: NMOS %.1f um at gm/Id %.1f, PMOS %.1f um at gm/Id %.1f, %.2f mA, gm %.1f mS, ro %.0f ohm"
        % (V_TRIP, d["wn"], d["gm_id_n"], d["wp"], d["gm_id_p"], d["id"] * 1e3, d["gm"] * 1e3, d["ro"]),
        "feedback %.0f ohm for 50 ohm into %.0f ohm: Av %.1f dB, Gm,eff %.1f mS, input capacitance %.0f fF, gamma_eff %.2f"
        % (d["rf"], d["rl"], 20 * math.log10(abs(d["av"])), d["gm_eff"] * 1e3, d["cin"] * 1e15, d["gamma"]),
        "shared antenna pad %.0f fF, shunt coil %.2f nH (%.2f ohm) off chip" % (d["cpad"] * 1e15, d["lsh"] * 1e9, d["rlsh"]),
        "NF estimate %.2f dB, 1 + RS/Rf is %.2f dB of it" % (d["nf_est"], 10 * math.log10(1 + RS / d["rf"])),
    ] + ([] if LP is None else [
        "Level plan asks: LNA NF %.1f dB, gain %+.0f dB, IIP3 %.1f dBm, P1dB %.1f dBm."
        % (_st()["nf"], _st()["gain"], _st()["iip3"], _st()["iip3"] - LP.P1DB_BELOW_IIP3),
    ]))


def selftest():
    d = design()
    assert abs(d["gm"] * 0 + 0) == 0
    assert 10.0 < d["wn"] < 1000.0 and 10.0 < d["wp"] < 2000.0, (d["wn"], d["wp"])
    assert d["wp"] > d["wn"], "the PMOS carries the same current at the same VGS, so it is wider"
    rlp = d["rl"] * d["ro"] / (d["rl"] + d["ro"])
    assert abs((d["rf"] + rlp) / (1 + d["gm"] * rlp) - RS) < 1e-9
    d2 = design(id_a=6e-3)
    assert d2["gm"] > d["gm"] and d2["rf"] > d["rf"]
    txt = inc_text(d)
    assert "parameters RF=" in txt and "LSH=" in txt and "parameters CD=" in txt
    # every robustness point sizes, and each one moves exactly its own quantity
    pts = robust_points()
    labels = [pt["perturb"]["label"] for pt in pts]
    assert labels[0] == "nominal" and len(set(labels)) == len(labels), labels
    runs = {lbl: design(**pt) for lbl, pt in zip(labels, pts)}
    base = runs["nominal"]
    # the nominal row is the design itself, so the sweep has something to move against
    for key in ("wn", "wp", "rf", "cpad", "lsh", "rlsh", "cd"):
        assert base[key] == d[key], (key, base[key], d[key])
    assert abs(runs["width +20 %"]["wn"] / base["wn"] - 1.2) < 1e-9
    assert abs(runs["width -20 %"]["wp"] / base["wp"] - 0.8) < 1e-9
    assert abs(runs["feedback R +20 %"]["rf"] / base["rf"] - 1.2) < 1e-9
    assert abs(runs["pad -20 %"]["cpad"] / base["cpad"] - 0.8) < 1e-9
    assert abs(runs["shunt part +5 %"]["lsh"] / base["lsh"] - 1.05) < 1e-9
    assert abs(runs["shunt part +5 %"]["rlsh"] / base["rlsh"] - 1.05) < 1e-9
    assert abs(runs["load node +100 fF"]["cd"] - 100e-15) < 1e-30
    # a moved part does not re-size the pair, which is the point of the sweep
    for lbl in ("pad +20 %", "shunt part -5 %", "load node +200 fF", "feedback R -20 %"):
        assert runs[lbl]["wn"] == base["wn"] and runs[lbl]["wp"] == base["wp"], lbl
    assert robust_columns(runs["pad +20 %"])["case"] == "pad +20 %"
    assert set(robust_columns(base)) == set(robust_columns(runs["width +20 %"]))
    assert "parameters CD=100f" in inc_text(runs["load node +100 fF"])
    cy = cace_conditions(d)
    assert "  WN:\n" in cy and "typical: %.6g" % (d["wn"] * 1e-6) in cy and "  NGP:\n" in cy, cy[:200]
    print("selftest: ok  (%.1f mA: gm %.1f mS, Rf %.0f ohm, NF est %.2f dB, %d robustness points)"
          % (d["id"] * 1e3, d["gm"] * 1e3, d["rf"], d["nf_est"], len(pts)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", type=float, default=4.0e-3, help="current through the pair, A")
    ap.add_argument("--l", type=float, default=0.13, help="um")
    ap.add_argument("--rl", type=float, default=RL_BENCH, help="load the match is solved against, ohm")
    ap.add_argument("--cpad", type=float, default=C_PAD)
    ap.add_argument("--lsh", type=float, default=None)
    ap.add_argument("--lut-dir", default=None)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    d = design(a.id, a.l, a.rl, a.cpad, a.lsh, lut_dir=a.lut_dir)
    print(report(d))
    if a.write:
        with open(INC, "w") as fh:
            fh.write(inc_text(d))
        print("wrote %s" % INC)
        if os.path.exists(CACE_YAML):
            patch_cace(d)
            print("updated %s" % CACE_YAML)
    return 0


if __name__ == "__main__":
    sys.exit(main())
