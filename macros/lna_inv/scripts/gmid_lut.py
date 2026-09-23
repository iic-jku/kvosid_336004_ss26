#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: gm/Id lookups on the SG13 LV MOS tables

"""gm/Id sizing on the pygmid tables the container ships.

The tables are the analog-course ones (`sg13_lv_nmos.mat`, `sg13_lv_pmos.mat`,
IHP SG13G2 PSP at 27 C, W = 5 um, L = 0.13 to 10 um, VSB 0 to 1.2 V). SG13CMOS5L
shares the LV PSP cards with SG13G2, and `--check` proves it: one VACASK
operating point on the CMOS5L PDK against the same bias in the table.

    python3 gmid_lut.py --check      # needs the container (vacask, the PDK)
    python3 gmid_lut.py --selftest   # table-only invariants

Every per-width number is per micron of drawn width, so a device of width W
scales linearly from it. Nothing here knows about a circuit.
"""

import argparse
import math
import os
import subprocess
import sys
import tempfile

import numpy as np

K_B = 1.380649e-23
T_LUT = 300.15          # the tables are extracted at 27 C
LUT_W_UM = 5.0

# Where the tables live. The container ships them with the analog course, and
# the template repo carries the same files under macros/inverter/scripts/sizing.
DEFAULT_DIR = os.environ.get("GMID_LUT_DIR",
                             "/foss/examples/analog-course/gmid")
FILES = {"nmos": "sg13_lv_nmos.mat", "pmos": "sg13_lv_pmos.mat"}


def load(dev="nmos", lut_dir=None):
    from pygmid import Lookup
    path = os.path.join(lut_dir or DEFAULT_DIR, FILES[dev])
    if not os.path.exists(path):
        raise FileNotFoundError("%s: set GMID_LUT_DIR" % path)
    return Lookup(path)


class Device:
    """One table, queried at a bias, everything per micron of width."""

    def __init__(self, dev="nmos", lut_dir=None):
        self.dev = dev
        self.lk = load(dev, lut_dir)

    def _v(self, var, **bias):
        return float(np.asarray(self.lk.lookup(var, **bias)).ravel()[0])

    def at(self, gm_id, L, VDS, VSB=0.0):
        """Small-signal quantities at a gm/Id, per um of width."""
        b = dict(GM_ID=gm_id, L=L, VDS=VDS, VSB=VSB)
        id_w = self._v("ID_W", **b)                 # A/um
        gm_w = gm_id * id_w
        cgg = self._v("CGG_W", **b)                 # F/um
        cgs = self._v("CGS_W", **b)
        cgd = self._v("CGD_W", **b)
        cgb = self._v("CGB_W", **b)
        gds_w = self._v("GDS_W", **b)
        # The table's CGG carries the overlap capacitances (it is what fT is
        # computed from), CGS/CGD/CGB do not, so the overlap per side is what
        # is left over. A gate-source capacitance for a resonant input needs
        # the overlap in it.
        c_ov = max(cgg - cgs - cgd - cgb, 0.0) / 2.0
        vgs = float(np.asarray(self.lk.lookupVGS(GM_ID=gm_id, L=L, VDS=VDS,
                                                 VSB=VSB)).ravel()[0])
        # Thermal drain noise PSD, A^2/Hz for the table's 5 um, so per um it
        # scales like gm. g_n = STH/(4kT) is gamma*gd0 in one number, which
        # is what a noise-figure estimate wants and what no gamma guess gives.
        try:
            sth_w = self._v("STH_W", **b)
        except Exception:
            sth_w = float("nan")
        return dict(gm_id=gm_id, L=L, VDS=VDS, VSB=VSB, vgs=vgs, id_w=id_w,
                    gm_w=gm_w, cgg_w=cgg, cgs_w=cgs, cgd_w=cgd, cgb_w=cgb,
                    c_ov_w=c_ov, cgs_tot_w=cgs + c_ov, cgd_tot_w=cgd + c_ov,
                    gds_w=gds_w,
                    ft=gm_w / (2 * math.pi * cgg),
                    gn_w=sth_w / (4 * K_B * T_LUT),
                    gamma_eff=sth_w / (4 * K_B * T_LUT * gm_w))

    def size_for_gm(self, gm, gm_id, L, VDS, VSB=0.0):
        """Width and current for a target transconductance."""
        p = self.at(gm_id, L, VDS, VSB)
        w = gm / p["gm_w"]
        out = dict(p, W=w, ID=p["id_w"] * w, gm=gm, cgg=p["cgg_w"] * w,
                   cgs=p["cgs_w"] * w, cgd=p["cgd_w"] * w,
                   gds=p["gds_w"] * w, gn=p["gn_w"] * w)
        return out

    def ron_w(self, VGS, L, VSB=0.0):
        """On-resistance times width of a switch, ohm*um, from the triode edge.

        The table's VDS grid starts at 0, so GDS there is the linear-region
        conductance. Read at 25 mV rather than at 0, where PSP's gds is exact
        but the table's interpolation is not.
        """
        gds_w = self._v("GDS_W", VGS=VGS, VDS=0.025, L=L, VSB=VSB)
        return 1.0 / gds_w

    def cgg_w_at(self, VGS, VDS, L, VSB=0.0):
        return self._v("CGG_W", VGS=VGS, VDS=VDS, L=L, VSB=VSB)


# ---------------------------------------------------------------------------
# --check: the table against the PDK, one operating point in VACASK
# ---------------------------------------------------------------------------

CHECK_DECK = """// gm/Id table check, one operating point
include "sg13cmos5l_vacask_common.lib"
include "cornerMOSlv.lib" section=mos_tt
ground 0
model vsource vsource
vg (g 0) vsource dc={vgs}
vd (d 0) vsource dc={vds}
xm1 (d g 0 0) sg13_lv_nmos w={w}u l={l}u ng=1 m=1
control
  options temp=27
  save {saves}
  analysis op1 op
endc
"""


def vacask_op(vgs, vds, w=LUT_W_UM, l=0.13):
    """Run one VACASK OP on the PDK and return ids, gm, cgg, gds."""
    from rawfile import rawread
    pdk = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"])
    path = "xm1:%s" % os.environ.get("GMID_CHECK_INST",
                                     "nsg13_lv_nmos")
    keys = ("ids", "gm", "cgg", "gds", "cgsol", "cgdol")
    saves = " ".join("p('%s',%s)" % (path, k) for k in keys)
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "check.sim"), "w") as fh:
            fh.write(CHECK_DECK.format(vgs=vgs, vds=vds, w=w, l=l, saves=saves))
        with open(os.path.join(pdk, "libs.tech", "vacask", ".vacaskrc.toml")) as fh:
            rc = fh.read()
        with open(os.path.join(d, ".vacaskrc.toml"), "w") as fh:
            fh.write(rc)
        r = subprocess.run(["vacask", "check.sim"], cwd=d, capture_output=True,
                           text=True)
        raw = os.path.join(d, "op1.raw")
        if not os.path.exists(raw):
            raise RuntimeError("vacask wrote no op1.raw:\n" + r.stdout + r.stderr)
        p = rawread(raw).get()
        out = {}
        for n in p.names:
            for k in sorted(keys, key=len, reverse=True):
                if n.endswith(k) and k not in out:
                    out[k] = float(np.real(p[n][0]))
                    break
        missing = [k for k in keys if k not in out]
        if missing:
            raise RuntimeError("no %s in %s" % (missing, list(p.names)))
        # PSP reports the intrinsic cgg and the overlaps apart, the table sums
        # them, so compare the sum.
        out["cgg_tot"] = out["cgg"] + out["cgsol"] + out["cgdol"]
        return out


def check(lut_dir=None, vgs=0.6, vds=0.6, tol=0.02):
    lk = load("nmos", lut_dir)
    ref = {k: float(np.asarray(lk.lookup(k.upper(), VGS=vgs, VDS=vds, L=0.13)).ravel()[0])
           for k in ("id", "gm", "cgg", "gds")}
    sim = vacask_op(vgs, vds)
    ok = True
    print("  %-5s %12s %12s %8s" % ("", "table", "vacask", "delta"))
    for k, kk in (("id", "ids"), ("gm", "gm"), ("cgg", "cgg_tot"), ("gds", "gds")):
        a, b = ref[k], sim[kk]
        d = (b - a) / a
        ok = ok and abs(d) < tol
        print("  %-5s %12.5g %12.5g %+7.2f%%" % (k, a, b, 100 * d))
    print("check: %s (tolerance %.0f%%)" % ("ok" if ok else "FAIL", 100 * tol))
    return 0 if ok else 1


def selftest(lut_dir=None):
    n = Device("nmos", lut_dir)
    # gm/Id falls with VGS, so the current per width has to rise with a lower
    # gm/Id at fixed L and VDS.
    a, b = n.at(15.0, 0.13, 0.6), n.at(8.0, 0.13, 0.6)
    assert b["id_w"] > a["id_w"] and b["vgs"] > a["vgs"], (a, b)
    # fT rises towards strong inversion at short L.
    assert b["ft"] > a["ft"], (a["ft"], b["ft"])
    # And a longer device has more capacitance per micron.
    c = n.at(15.0, 0.5, 0.6)
    assert c["cgg_w"] > a["cgg_w"], (a["cgg_w"], c["cgg_w"])
    # The noise column resolves to a gamma near unity, not to nan or 100.
    assert 0.5 < a["gamma_eff"] < 3.0, a["gamma_eff"]
    # A switch: more gate drive, less on-resistance.
    assert n.ron_w(1.2, 0.13) < n.ron_w(0.8, 0.13)
    # size_for_gm scales linearly.
    s1, s2 = n.size_for_gm(10e-3, 12.0, 0.13, 0.5), n.size_for_gm(20e-3, 12.0, 0.13, 0.5)
    assert abs(s2["W"] / s1["W"] - 2.0) < 1e-9 and abs(s2["ID"] / s1["ID"] - 2.0) < 1e-9
    print("selftest: ok  (nmos at gm/Id 15, L 0.13, VDS 0.6: fT %.1f GHz, "
          "gamma_eff %.2f, Id/W %.1f uA/um)"
          % (a["ft"] / 1e9, a["gamma_eff"], a["id_w"] * 1e6))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lut-dir", default=None)
    ap.add_argument("--check", action="store_true",
                    help="one VACASK operating point on the PDK against the table")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.lut_dir)
    if a.check:
        return check(a.lut_dir)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
