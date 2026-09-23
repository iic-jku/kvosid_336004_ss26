#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Check hbac and hbnoise of the blocker bench against transient runs of the same circuit

"""hbac and hbnoise are new in VACASK, so check them against analyses that share no code with them.

    python3 scripts/lna_inv_hbcheck.py [--write]

- No blocker: hbac against ac, hbnoise against noise, both run by the bench itself.
- With the blocker: hbac against a two-tone transient, the wanted tone read off an FFT.
- With the blocker: hbnoise against transient noise, the output PSD around F0 from Welch averaging.

Every transient deck is the netlisted lna_inv_tb_blocker bench with its control block
replaced, so all of them simulate the same circuit. Run the bench first (`make hbcheck`
does both).
"""

import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np

import lna_inv_post as post
import vacask_rc

DECK = os.path.join(post.SIM, "lna_inv_tb_blocker.spectre")
DOC = os.path.join(post.MACRO, "doc", "lna_inv_hbcheck.md")
FB = 2.40e9
F0 = 2.44e9
AW = 2e-3                                   # wanted tone, -50 dBm available, linear at every blocker level
TWO_TONE_DBM = (-30.0, -20.0, -15.0, -10.0, -5.0, 0.0)
NOISE_DBM = (None, -10.0, -5.0, 0.0)        # None: no blocker, checked against the noise analysis
SEEDS = (1, 2, 3, 4, 5)                     # independent noise records per level, their spread is the error bar

# two-tone transient: 40 ns to settle, then 50 ns, which holds whole periods of FB, F0 and their difference
TT_SETTLE, TT_WIN, TT_STEP = 40e-9, 50e-9, 1e-12
# transient noise: Welch over 100 ns segments, the PSD averaged over F0 +- 30 MHz, which keeps
# the blocker line 10 MHz outside the band
TN_SETTLE, TN_REC, TN_STEP, TN_SEG, TN_BAND = 40e-9, 2e-6, 2e-12, 100e-9, 30e6
TN_FMAX = 20e9


def ampl(dbm):
    """Source amplitude behind RS for an available power, V peak."""
    return math.sqrt(8 * post.RS * 1e-3 * 10 ** (dbm / 10.0))


def with_control(text, control):
    """The netlisted bench with its control block replaced."""
    i, j = text.index("\ncontrol\n"), text.index("\nendc\n")
    return text[:i + 1] + control + text[j + len("\nendc\n"):]


def run(text, rc):
    """Run one deck in its own directory with the VACASK config rc, return the transient waveform of vout."""
    from rawfile import rawread
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(rc, d)
        with open(os.path.join(d, "deck.spectre"), "w") as fh:
            fh.write(text)
        r = subprocess.run(["vacask", "-sp", "-qp", "deck.spectre"], cwd=d, capture_output=True, text=True)
        raw = os.path.join(d, "tr.raw")
        if r.returncode or not os.path.exists(raw):
            raise RuntimeError("vacask failed:\n" + r.stdout[-2000:] + r.stderr[-2000:])
        p = rawread(raw).get()
        return np.real(p["time"]), np.real(p["vout"])


def two_tone_control(a_blk, a_want):
    stop = TT_SETTLE + TT_WIN
    return ("control\n  options temp=27\n  options rawfile=\"binary\"\n  save v(vout)\n"
            "  alter instance(\"vin1\") ampl=%.6g\n  alter instance(\"vin2\") ampl=%.6g\n"
            "  analysis tr tran stop=%.6g step=%.6g maxstep=%.6g\nendc\n"
            % (a_blk, a_want, stop, TT_STEP, TT_STEP))


def tone(t, v, t0, span, f):
    """Peak phasor magnitude of v at f over [t0, t0 + span), which holds a whole number of its periods."""
    n = int(round(span / TT_STEP))
    tu = t0 + np.arange(n) * TT_STEP
    x = np.interp(tu, t, v)
    return abs(np.sum(x * np.exp(-2j * np.pi * f * tu))) * 2.0 / n


def noise_control(a_blk, seed):
    stop = TN_SETTLE + TN_REC
    return ("control\n  options temp=27\n  options rawfile=\"binary\"\n  options tran_noiselte=1e6\n"
            "  save v(vout)\n  alter instance(\"vin1\") ampl=%.6g\n  alter instance(\"vin2\") ampl=0\n"
            "  analysis tr tran stop=%.6g step=%.6g maxstep=%.6g noisefmax=%.6g noisemode=\"sde\" noiseseed=%d\nendc\n"
            % (a_blk, stop, TN_STEP, TN_STEP, TN_FMAX, seed))


def psd_at_f0(t, v):
    """One-sided output PSD averaged over the band around F0.

    The blocker and its harmonics are periodic in 1/FB, so the synchronous average over
    all blocker periods is removed first. What is left is the noise, which Welch then
    averages over 100 ns Hann segments with half overlap.
    """
    per = 240                                   # samples per blocker period
    dt = 1.0 / (FB * per)
    k = int(TN_REC * FB)                        # whole blocker periods in the record
    tu = TN_SETTLE + np.arange(k * per) * dt
    x = np.interp(tu, t, v).reshape(k, per)
    x = (x - x.mean(axis=0)).ravel()
    nseg = int(round(TN_SEG / dt))
    w = np.hanning(nseg)
    f = np.fft.rfftfreq(nseg, dt)
    band = abs(f - F0) <= TN_BAND + 1.0
    seg = [np.mean(2.0 * abs(np.fft.rfft(x[s:s + nseg] * w)[band]) ** 2 / (np.sum(w ** 2) / dt))
           for s in range(0, x.size - nseg + 1, nseg // 2)]
    return float(np.mean(seg))


def reference():
    """What the bench itself computed: ac, noise, and hbac/hbnoise per blocker level."""
    raw = post.Raws()
    ac0, nz0 = raw("ac0"), raw("nz0")
    bac, bnz = raw("bac", sweeps=1), raw("bnz", sweeps=1)
    if ac0 is None or bac is None:
        sys.exit("no ac0/bac raws in %s: run the blocker bench first" % post.SIM)
    # the noise analyses run over the same F0 +- 30 MHz bins the transient PSD is averaged over
    ref = {"ac0": float(abs(ac0["vout"][0])), "hbac": {}, "hbnoise": {}}
    if nz0 is not None:
        ref["nz0"] = float(np.mean(np.real(nz0["onoise"])))
    for i in range(bac.sweepGroups):
        a = float(np.real(bac.sweepData(i)["pb"]))
        ref["hbac"][round(post.dbm_avail(a), 1)] = float(abs(bac[i, "vout;1"][0]))
    if bnz is not None:
        for i in range(bnz.sweepGroups):
            a = float(np.real(bnz.sweepData(i)["pbn"]))
            ref["hbnoise"][round(post.dbm_avail(a), 1)] = float(np.mean(np.real(bnz[i, "onoise"])))
    return ref


def check(jobs):
    with open(DECK) as fh:
        text = fh.read()
    pdk_rc = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], "libs.tech", "vacask", ".vacaskrc.toml")
    ref = reference()
    rcdir = tempfile.mkdtemp()
    rc = vacask_rc.write_rc(pdk_rc, rcdir, [os.path.join(post.MACRO, "schematic", "xschem")])
    decks = {("tt", p): with_control(text, two_tone_control(ampl(p), AW)) for p in TWO_TONE_DBM}
    # the numerical floor at the F0 bin: the strongest blocker and no wanted tone
    decks[("floor", TWO_TONE_DBM[-1])] = with_control(text, two_tone_control(ampl(TWO_TONE_DBM[-1]), 0.0))
    for p in NOISE_DBM:
        for seed in SEEDS:
            decks[("tn", (p, seed))] = with_control(text, noise_control(0.0 if p is None else ampl(p), seed))
    try:
        with ThreadPoolExecutor(jobs) as ex:
            waves = dict(zip(decks, ex.map(lambda k: run(decks[k], rc), decks)))
    finally:
        shutil.rmtree(rcdir)

    out = {"ref": ref, "tt": {}, "floor": {}, "tn": {}}
    per_seed = {}
    for (kind, p), (t, v) in waves.items():
        if kind == "tn":
            per_seed.setdefault(p[0], []).append(psd_at_f0(t, v))
            continue
        a = AW if kind == "tt" else 1.0
        g = tone(t, v, TT_SETTLE, TT_WIN, F0) / a
        # the two halves of the window, which say whether 40 ns was enough to settle
        h = [tone(t, v, TT_SETTLE + i * TT_WIN / 2, TT_WIN / 2, F0) / a for i in (0, 1)]
        out[kind][p] = (g, 20 * math.log10(h[1] / h[0]))
    # the seeds are independent records, so their spread is an honest standard error
    for p, vals in per_seed.items():
        vals = np.array(vals)
        out["tn"][p] = (float(vals.mean()), float(vals.std(ddof=1) / math.sqrt(vals.size) / vals.mean()))
    return out


def db(x):
    return 10 * math.log10(x)


def table(r):
    ref = r["ref"]
    L = ["## No blocker", "",
         "| | reference | periodic small-signal at -50 dBm blocker | difference |", "|---|---|---|---|"]
    low = min(ref["hbac"])
    L.append("| gain to vout at F0 | ac %.5f V/V | hbac %.5f V/V | %+.4f dB |"
             % (ref["ac0"], ref["hbac"][low], 20 * math.log10(ref["hbac"][low] / ref["ac0"])))
    if "nz0" in ref and ref["hbnoise"]:
        lowb = min(ref["hbnoise"])
        L.append("| output noise at F0 | noise %.4g V^2/Hz | hbnoise %.4g V^2/Hz | %+.3f dB |"
                 % (ref["nz0"], ref["hbnoise"][lowb], db(ref["hbnoise"][lowb] / ref["nz0"])))
    L += ["", "## hbac against a two-tone transient", "",
          "Blocker at 2.40 GHz, wanted tone %.0f dBm at 2.44 GHz. The transient gain is the F0 line of the output over %.0f ns after %.0f ns of settling, divided by the wanted amplitude. "
          "The settling column is the gain in the second half of the window against the first."
          % (post.dbm_avail(AW), TT_WIN * 1e9, TT_SETTLE * 1e9), "",
          "| blocker dBm | hbac V/V | transient V/V | transient - hbac | settling |", "|---|---|---|---|---|"]
    for p, (g, drift) in sorted(r["tt"].items()):
        h = ref["hbac"].get(round(p, 1))
        L.append("| %.0f | %.5f | %.5f | %+.3f dB | %+.4f dB |"
                 % (p, h, g, 20 * math.log10(g / h), drift))
    for p, (g, _) in r.get("floor", {}).items():
        L += ["", "Numerical floor: with the %.0f dBm blocker and no wanted tone the F0 line reads %.3g V, %.0f dB below the %.0f dBm tone's output."
              % (p, g, 20 * math.log10(g / (AW * ref["hbac"][round(p, 1)])), post.dbm_avail(AW))]
    L += ["", "## hbnoise against transient noise", "",
          "`noisemode=\"sde\"`, `noisefmax` %.0f GHz, `maxstep` %.0f ps, %d seeds of %.0f us each after %.0f ns of settling. The blocker's periodic part is removed by synchronous averaging, "
          "then Welch over %.0f ns Hann segments, the PSD averaged over the bins within %.0f MHz of F0. The spread is one standard error across the seeds."
          % (TN_FMAX / 1e9, TN_STEP * 1e12, len(SEEDS), TN_REC * 1e6, TN_SETTLE * 1e9, TN_SEG * 1e9, TN_BAND / 1e6), "",
          "| blocker dBm | periodic small-signal V^2/Hz | transient noise V^2/Hz | transient - periodic |", "|---|---|---|---|"]
    for p, (s, rel) in sorted(r["tn"].items(), key=lambda kv: -999 if kv[0] is None else kv[0]):
        if p is None:
            h, lab, name = ref.get("nz0"), "none", "noise"
        else:
            h, lab, name = ref["hbnoise"].get(round(p, 1)), "%.0f" % p, "hbnoise"
        hs = "%s %.4g" % (name, h) if h else "not run"
        d = "%+.2f dB (%+.2f / %+.2f)" % (db(s / h), db(s * (1 - rel) / h), db(s * (1 + rel) / h)) if h else ""
        L.append("| %s | %s | %.4g +- %.0f %% | %s |" % (lab, hs, s, rel * 100, d))
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4, help="transient runs in parallel")
    a = ap.parse_args()
    body = table(check(a.jobs))
    print(body)
    # "This is vacask 89e888d." is the first line of its help
    ver = subprocess.run(["vacask", "-h"], capture_output=True, text=True).stdout.split("\n")[0]
    ver = ver.replace("This is vacask", "").strip(" .")
    if a.write:
        with open(DOC, "w") as fh:
            fh.write("<!--\nSPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University\n"
                     "SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1\n"
                     "Description: hbac and hbnoise of the lna_inv blocker bench checked against ac, noise and transient runs\n-->\n\n"
                     "# lna_inv: hbac and hbnoise checked\n\n"
                     "Generated by `scripts/lna_inv_hbcheck.py`, rebuild with `make hbcheck`. "
                     "VACASK %s, same circuit as `lna_inv_tb_blocker`, TT, 27 C, `RFMODE=0`.\n\n" % ver + body + "\n")
        print("wrote %s" % DOC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
