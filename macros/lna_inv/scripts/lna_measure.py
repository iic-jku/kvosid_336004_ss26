#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Read an LNA macro's VACASK bench raws and score them against the level plan

"""Turn <top>_tb_sp, <top>_tb_hb and <top>_tb_chain raws into the level plan's rows.

    python3 scripts/lna_measure.py --macro .            # print
    python3 scripts/lna_measure.py --macro . --write    # splice doc/<top>_feasibility.md, write doc/<top>_results.json

The macro directory's basename is the cell and bench prefix. The bench load
resistor stands in for the mixer and the converter, so NF is quoted with its
noise removed and once with it in.
"""

import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# The receiver level plan is not part of this repo, so the scorecard is skipped
# when it cannot be imported and the raw measurements are printed on their own.
sys.path.insert(0, HERE)
try:
    import rx_level_plan as LP       # noqa: E402
except ImportError:
    LP = None

F0 = 2.44e9
F1 = 2.441e9
RS = 50.0
RL = 200.0


def dbm_avail(ampl):
    """Available power of a source amplitude behind RS, dBm."""
    return 10 * math.log10(ampl ** 2 / (8 * RS) / 1e-3)


class Macro:
    def __init__(self, path):
        self.dir = os.path.abspath(path)
        self.top = os.path.basename(self.dir)
        self.sim = os.path.join(self.dir, "testbenches", "xschem", "simulations")
        self.doc = os.path.join(self.dir, "doc", self.top + "_feasibility.md")
        self.json = os.path.join(self.dir, "doc", self.top + "_results.json")
        self.mixer_json = os.path.join(self.dir, "doc", "mixer_results.json")

    def raw(self, name, sweeps=0):
        from rawfile import rawread
        p = os.path.join(self.sim, name + ".raw")
        if not os.path.exists(p):
            return None
        return rawread(p).get(sweeps=sweeps)


def measure(m):
    out = {"top": m.top}
    op = m.raw("op1")
    if op is not None:
        out["idd_ma"] = -float(np.real(op["vsup:flow(br)"][0])) * 1e3
    sp = m.raw("sp1")
    if sp is not None:
        f = np.real(sp["frequency"])
        k = np.argmin(abs(f - F0))
        s11 = abs(sp["s(1,1)"])
        out["s11_db"] = float(20 * np.log10(s11[k]))
        out["s11_min_db"] = float(20 * np.log10(s11.min()))
        out["s11_min_ghz"] = float(f[np.argmin(s11)] / 1e9)
        out["s21_db"] = float(20 * np.log10(abs(sp["s(2,1)"][k])))
    sp2 = m.raw("sp2")
    if sp2 is not None:
        # RF selectivity for the level plan: |S21| below its value at F0, per
        # offset, the weaker side of the two. The plan interpolates this in
        # log offset, so the grid is log too.
        f = np.real(sp2["frequency"])
        s21 = abs(sp2["s(2,1)"])
        g0 = s21[np.argmin(abs(f - F0))]
        sel = []
        for off in (10.0, 20.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 600.0, 1000.0,
                    1500.0, 2000.0, 2400.0, 3000.0, 5000.0, 8000.0, 10500.0):
            sides = [F0 - off * 1e6, F0 + off * 1e6]
            vals = []
            for fx in sides:
                if f[0] <= fx <= f[-1]:
                    i = np.argmin(abs(f - fx))
                    vals.append(-20 * np.log10(s21[i] / g0))
            if vals:
                sel.append([off, round(float(min(vals)), 2)])
        out["selectivity_db"] = sel
    ac = m.raw("ac1")
    if ac is not None:
        f = np.real(ac["frequency"])
        k = np.argmin(abs(f - F0))
        out["gm_eff_ms"] = float(abs(ac["vout"][k]) / RL / 0.5 * 1e3)
    nz = m.raw("n1")
    if nz is not None:
        f = np.real(nz["frequency"])
        k = np.argmin(abs(f - F0))
        tot, src, load = nz["onoise"][k], nz["n(rs)"][k], nz["n(rl)"][k]
        out["nf_db"] = float(10 * np.log10((tot - load) / src))
        out["nf_with_load_db"] = float(10 * np.log10(tot / src))
        shares = {}
        for n in nz.names:
            if n.startswith("n(") and "," not in n and n not in ("n(rs)", "n(rl)"):
                shares[n[2:-1]] = float(nz[n][k] / (tot - load) * 100)
        out["noise_shares_pct"] = dict(sorted(shares.items(), key=lambda x: -x[1])[:6])
    hb = m.raw("hb1", sweeps=1)
    if hb is not None:
        pts = []
        for ii in range(hb.sweepGroups):
            f = np.real(hb[ii, "frequency"])
            v = abs(hb[ii, "vout"][np.argmin(abs(f - F0))])
            a = float(np.real(hb.sweepData(ii)["pin"]))
            pts.append((dbm_avail(a), 20 * np.log10(v / RL / (a / 2))))
        g0 = pts[0][1]
        p1 = None
        for (pa, ga), (pb, gb) in zip(pts, pts[1:]):
            if gb < g0 - 1.0 <= ga:
                p1 = pa + (pb - pa) * (ga - (g0 - 1)) / (ga - gb)
                break
        out["hb_points"] = pts
        out["p1db_dbm"] = p1
    for name, key in (("hb2", "iip3_dbm_40"), ("hb3", "iip3_dbm_30")):
        h = m.raw(name)
        if h is None:
            continue
        f = np.real(h["frequency"])
        v = abs(h["vout"])
        fund = v[np.argmin(abs(f - F0))]
        im3 = v[np.argmin(abs(f - (2 * F0 - F1)))]
        pin = -40.0 if name == "hb2" else -30.0
        out[key] = float(pin + 0.5 * 20 * np.log10(fund / im3))
    for name, ampl, key in (("tran1", 6.325e-3, "chain_40"), ("tran2", 22.44e-3, "chain_29")):
        p = m.raw(name)
        if p is None or "ip" not in p.names:
            continue
        t = np.real(p["time"])
        i_if = np.real(p["ip"] - p["in"]) / 200.0
        # exactly 2 us after 0.4 us of settling: 5 cycles of the 2.5 MHz IF
        tu = np.arange(0.4e-6, 2.4e-6, 20e-12)
        x = np.interp(tu, t, i_if)
        n = tu.size
        X = np.fft.rfft(x) * 2.0 / n
        f = np.fft.rfftfreq(n, 20e-12)
        a = abs(X[np.argmin(abs(f - 2.5e6))])
        out[key + "_gm_ms"] = float(a / (ampl / 2) * 1e3)
        out[key + "_i_ua"] = float(a * 1e6)
    if os.path.exists(m.mixer_json) and "gm_eff_ms" in out:
        with open(m.mixer_json) as fh:
            mx = json.load(fh)
        if "iip3_ua" in mx:
            # The mixer's IIP3 is a current at the LNA output. Through the LNA's
            # transconductance it is an available voltage at the antenna.
            v_avail = mx["iip3_ua"] * 1e-6 / (out["gm_eff_ms"] * 1e-3)
            out["mixer_iip3_at_antenna_dbm"] = float(
                10 * math.log10((v_avail / math.sqrt(2)) ** 2 / RS / 1e-3))
    return out


def _dbv(x, floor=1e-15):
    return 20 * np.log10(np.maximum(np.abs(x), floor))


def steady_state(f, v, periods=2.0, n=801):
    """The periodic waveform behind a set of harmonic phasors.

    VACASK stores peak phasors (|V1| equals the amplitude the source was given),
    so the series is v(t) = V0 + sum |Vk| cos(2 pi fk t + arg Vk).
    """
    f = np.real(f)
    f0 = np.min(f[f > 0]) if np.any(f > 0) else 1.0
    t = np.linspace(0.0, periods / f0, n)
    out = np.zeros_like(t)
    for fk, vk in zip(f, v):
        if fk == 0:
            out += np.real(vk)
        else:
            out += np.abs(vk) * np.cos(2 * np.pi * fk * t + np.angle(vk))
    return t, out


def _pyplot(interactive):
    """pyplot, with a backend that suits the job. None when matplotlib is missing."""
    try:
        import matplotlib
    except ImportError:
        return None
    # Only force the file backend when there is nothing to show the window on,
    # otherwise leave matplotlib's own choice (TkAgg/QtAgg) alone.
    if not interactive or not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        if interactive:
            print("  no DISPLAY: drawing to files instead of windows")
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _grid(plt, panels, title, ncols=2):
    """One window holding the panels, laid out and labelled."""
    n = len(panels)
    ncols = min(ncols, n)
    nrows = int(np.ceil(n / float(ncols)))
    fig, axes = plt.subplots(nrows, ncols, squeeze=False,
                             figsize=(5.6 * ncols, 3.3 * nrows))
    flat = axes.ravel()
    for ax, draw in zip(flat, panels):
        draw(ax)
        ax.grid(alpha=0.3)
    for ax in flat[n:]:
        ax.axis("off")
    fig.suptitle(title)
    return fig


def plots(m, outdir=None, show=False):
    """Draw what the benches measured, grouped into four windows.

    show=True opens the windows and blocks until they are closed.
    outdir writes a PNG per window. Both together do both.
    """
    plt = _pyplot(show)
    if plt is None:
        print("  plotting skipped: matplotlib not available")
        return []
    windows = show and plt.get_backend().lower() != "agg"
    if outdir is None and not windows:
        outdir = os.path.join(m.dir, "doc")
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir)
    written = []

    def save(fig, name):
        fig.tight_layout()
        if outdir:
            path = os.path.join(outdir, "%s_%s.png" % (m.top, name))
            fig.savefig(path, dpi=150)
            written.append(path)
        if not windows:
            plt.close(fig)

    sp, sp2 = m.raw("sp1"), m.raw("sp2")
    ac, nz = m.raw("ac1"), m.raw("n1")
    hb = m.raw("hb1", sweeps=1)

    # ---- window 1: the small-signal bench --------------------------------
    panels = []
    if sp is not None:
        def p_sparam(ax):
            f = np.real(sp["frequency"]) / 1e9
            ax.plot(f, _dbv(sp["s(1,1)"]), label="S11")
            ax.plot(f, _dbv(sp["s(2,1)"]), label="S21")
            ax.axvline(F0 / 1e9, color="0.6", ls=":", lw=1)
            ax.set(xlabel="frequency (GHz)", ylabel="magnitude (dB)", title="match and gain")
            ax.legend(fontsize=8)
        panels.append(p_sparam)
    if ac is not None:
        def p_gm(ax):
            f = np.real(ac["frequency"]) / 1e9
            ax.plot(f, abs(ac["vout"]) / RL / 0.5 * 1e3)
            ax.axvline(F0 / 1e9, color="0.6", ls=":", lw=1)
            ax.set(xlabel="frequency (GHz)", ylabel="Gm,eff (mS)",
                   title="transconductance into %.0f ohm" % RL)
        panels.append(p_gm)
    if nz is not None:
        def p_nf(ax):
            f = np.real(nz["frequency"]) / 1e9
            tot, src, load = nz["onoise"], nz["n(rs)"], nz["n(rl)"]
            ax.plot(f, 10 * np.log10((tot - load) / src), label="device noise only")
            ax.plot(f, 10 * np.log10(tot / src), label="with the bench load")
            ax.set(xlabel="frequency (GHz)", ylabel="NF (dB)", title="noise figure")
            ax.legend(fontsize=8)
        panels.append(p_nf)
    if sp2 is not None:
        def p_sel(ax):
            f = np.real(sp2["frequency"])
            s21 = abs(sp2["s(2,1)"])
            g0 = s21[np.argmin(abs(f - F0))]
            ax.semilogx(f / 1e9, -20 * np.log10(s21 / g0))
            ax.axvline(F0 / 1e9, color="0.6", ls=":", lw=1)
            ax.set(xlabel="frequency (GHz)", ylabel="rejection below F0 (dB)",
                   title="out of band")
        panels.append(p_sel)
    if panels:
        save(_grid(plt, panels, "%s: small signal" % m.top), "smallsignal")

    # ---- window 2: how it behaves as the drive rises ---------------------
    if hb is not None and hb.sweepGroups:
        pin_ax, gain, rel, absl = [], [], {2: [], 3: []}, {1: [], 2: [], 3: []}
        for i in range(hb.sweepGroups):
            f = np.real(hb[i, "frequency"])
            v = abs(hb[i, "vout"])
            a = float(np.real(hb.sweepData(i)["pin"]))
            fund = v[np.argmin(abs(f - F0))]
            pin_ax.append(dbm_avail(a))
            gain.append(20 * np.log10(fund / RL / (a / 2)))
            for k in (1, 2, 3):
                j2 = np.argmin(abs(f - k * F0))
                ok = abs(f[j2] - k * F0) < F0 / 2
                absl[k].append(_dbv(v[j2]) if ok else np.nan)
                if k > 1:
                    rel[k].append(20 * np.log10(v[j2] / fund) if ok else np.nan)

        def p_comp(ax):
            ax.plot(pin_ax, gain, "o-")
            ax.axhline(gain[0] - 1.0, color="0.6", ls=":", lw=1, label="-1 dB")
            ax.set(xlabel="available input power (dBm)",
                   ylabel="transducer gain (dB)", title="gain compression")
            ax.legend(fontsize=8)

        def p_abs(ax):
            for k, mk in ((1, "o-"), (2, "s-"), (3, "^-")):
                ax.plot(pin_ax, absl[k], mk, label="harmonic %d" % k)
            ax.set(xlabel="available input power (dBm)",
                   ylabel="V(vout) (dBV, peak)", title="harmonic levels")
            ax.legend(fontsize=8)

        def p_rel(ax):
            ax.plot(pin_ax, rel[2], "s-", label="HD2")
            ax.plot(pin_ax, rel[3], "^-", label="HD3")
            ax.set(xlabel="available input power (dBm)",
                   ylabel="relative to the fundamental (dBc)", title="harmonic distortion")
            ax.legend(fontsize=8)

        save(_grid(plt, [p_comp, p_abs, p_rel], "%s: large signal" % m.top), "largesignal")

        # ---- window 3: the phasors themselves ----------------------------
        hi, lo = hb.sweepGroups - 1, 0
        f_hi, v_hi = np.real(hb[hi, "frequency"]), hb[hi, "vout"]
        a_hi, a_lo = (float(np.real(hb.sweepData(x)["pin"])) for x in (hi, lo))

        def p_spec(ax):
            lev = _dbv(v_hi)
            # 100 dB of range below the strongest line: a numerically zero dc
            # term sits at -300 dBV and would otherwise set the scale
            floor = 10 * np.floor((lev.max() - 100) / 10)
            ax.stem(f_hi / 1e9, np.maximum(lev, floor), bottom=floor, basefmt=" ",
                    label="%.0f dBm in" % dbm_avail(a_hi))
            lo_lev = _dbv(hb[lo, "vout"])
            vis = lo_lev > floor
            ax.plot(np.real(hb[lo, "frequency"])[vis] / 1e9, lo_lev[vis], "x",
                    color="C1", label="%.0f dBm in" % dbm_avail(a_lo))
            for k, fk in enumerate(f_hi):
                if lev[k] > floor + 5:
                    ax.annotate("%d" % round(fk / F0), (fk / 1e9, lev[k]),
                                textcoords="offset points", xytext=(0, 4),
                                ha="center", fontsize=7)
            ax.set_ylim(floor, lev.max() + 12)
            ax.set(xlabel="frequency (GHz)", ylabel="V(vout) (dBV, peak)",
                   title="harmonic spectrum")
            ax.legend(fontsize=8)

        def p_wave(ax):
            t, wo = steady_state(f_hi, v_hi)
            ax.plot(t * 1e12, wo, label="vout")
            if "vin" in hb.names:
                _, wi = steady_state(f_hi, hb[hi, "vin"])
                ax.plot(t * 1e12, wi, "--", label="vin")
            ax.set(xlabel="time (ps)", ylabel="voltage (V)",
                   title="steady state at %.0f dBm in" % dbm_avail(a_hi))
            ax.legend(fontsize=8)

        save(_grid(plt, [p_spec, p_wave], "%s: harmonic balance, raw" % m.top),
             "hb_raw")

    # ---- window 4: the two-tone benches ----------------------------------
    panels = []
    for name, pin_dbm in (("hb2", -40.0), ("hb3", -30.0)):
        h = m.raw(name)
        if h is None:
            continue
        f, v = np.real(h["frequency"]), abs(h["vout"])
        band = (f > F0 - 6e6) & (f < F0 + 6e6) & (v > 0)
        if not band.any():
            continue

        def p_tt(ax, f=f, v=v, band=band, pin_dbm=pin_dbm):
            lev = _dbv(v[band])
            floor = 10 * np.floor((lev.min() - 10) / 10)
            ax.stem((f[band] - F0) / 1e6, lev, bottom=floor, basefmt=" ")
            ax.set_ylim(floor, lev.max() + 15)
            for fx, lab in ((F0, "F0"), (F1, "F1"),
                            (2 * F0 - F1, "2F0-F1"), (2 * F1 - F0, "2F1-F0")):
                ax.axvline((fx - F0) / 1e6, color="0.6", ls=":", lw=1)
                ax.annotate(lab, ((fx - F0) / 1e6, ax.get_ylim()[1]), fontsize=7,
                            ha="center", va="top")
            ax.set(xlabel="offset from F0 (MHz)", ylabel="output (dBV)",
                   title="two tones at %.0f dBm each" % pin_dbm)
        panels.append(p_tt)
    if panels:
        save(_grid(plt, panels, "%s: intermodulation" % m.top), "twotone")

    # ---- window 5: the chain bench, IF current out of the mixer ----------
    panels = []
    for name, ampl, label in (("tran1", 6.325e-3, "-40 dBm"),
                              ("tran2", 22.44e-3, "-29 dBm")):
        pr = m.raw(name)
        if pr is None or "ip" not in pr.names:
            continue
        t = np.real(pr["time"])
        i_if = np.real(pr["ip"] - pr["in"]) / RL
        # the same window measure() integrates: 5 cycles of the 2.5 MHz IF
        tu = np.arange(0.4e-6, 2.4e-6, 20e-12)
        x = np.interp(tu, t, i_if)

        def p_wave(ax, tu=tu, x=x, label=label):
            ax.plot(tu * 1e6, x * 1e6)
            ax.set(xlabel="time (us)", ylabel="IF current (uA)",
                   title="chain at %s" % label)

        def p_spec(ax, x=x, label=label):
            n = x.size
            X = np.abs(np.fft.rfft(x) * 2.0 / n)
            f = np.fft.rfftfreq(n, 20e-12)
            band = f < 20e6
            ax.plot(f[band] / 1e6, _dbv(X[band] * 1e6))
            ax.axvline(2.5, color="0.6", ls=":", lw=1)
            ax.set(xlabel="frequency (MHz)", ylabel="IF current (dBuA)",
                   title="chain spectrum at %s" % label)
        panels += [p_wave, p_spec]
    if panels:
        save(_grid(plt, panels, "%s: chain bench" % m.top), "chain")

    for path in written:
        print("  wrote %s" % path)
    if windows:
        print("  close the %d plot windows to continue" % len(plt.get_fignums()))
        plt.show()
    return written


def plain(r):
    """The measurements without the level-plan comparison."""
    out = []
    for k, v in r.items():
        if isinstance(v, float):
            out.append("  %-34s %.4g" % (k, v))
        elif isinstance(v, dict):
            out.append("  %s:" % k)
            out += ["    %-32s %.4g" % (kk, vv) for kk, vv in v.items()]
        elif isinstance(v, list):
            out.append("  %s:" % k)
            out += ["    %10.2f %10.3f" % tuple(pt) for pt in v]
        else:
            out.append("  %-34s %s" % (k, v))
    return "\n".join(out)


def scorecard(m, r):
    st = dict(zip(("name", "gain", "nf", "iip3"), LP.STATE_SETS["one"][0]))
    p1_ask = st["iip3"] - LP.P1DB_BELOW_IIP3
    nan = float("nan")
    rows = [
        ("noise figure, bench load excluded", "%.2f dB" % r.get("nf_db", nan),
         "%.1f dB" % st["nf"], r.get("nf_db", 99) <= st["nf"]),
        ("noise figure, bench load counted", "%.2f dB" % r.get("nf_with_load_db", nan), "", None),
        ("transconductance into %.0f ohm, antenna available voltage to output current" % RL,
         "%.1f mS" % r.get("gm_eff_ms", nan),
         "%+.0f dB of LNA gain in the plan, a frame the chain rows below resolve" % st["gain"], None),
        ("S11 at 2.44 GHz", "%.1f dB (best %.1f dB at %.3f GHz)"
         % (r.get("s11_db", 0), r.get("s11_min_db", 0), r.get("s11_min_ghz", 0)),
         "< -10 dB", r.get("s11_db", 0) < -10),
        ("input P1dB", "%s" % ("%.1f dBm" % r["p1db_dbm"] if r.get("p1db_dbm") is not None else "not reached in the sweep"),
         "%.1f dBm" % p1_ask, (r.get("p1db_dbm") or 99) >= p1_ask if r.get("hb_points") else None),
        ("IIP3, two tones at -40 dBm", "%s" % ("%.1f dBm" % r["iip3_dbm_40"] if "iip3_dbm_40" in r else "not run"),
         "%.1f dBm" % st["iip3"], r.get("iip3_dbm_40", -99) >= st["iip3"] if "iip3_dbm_40" in r else None),
        ("IIP3, two tones at -30 dBm", "%s" % ("%.1f dBm" % r["iip3_dbm_30"] if "iip3_dbm_30" in r else "not run"), "", None),
        ("supply current", "%.2f mA at 1.2 V" % r.get("idd_ma", nan), "", None),
    ]
    if "chain_40_gm_ms" in r:
        # The converter's full scale is a current into its virtual ground, and
        # the plan states it as -14 dBm at the converter input in a 50 ohm
        # frame. Both frames are quoted.
        v50 = math.sqrt(1e-3 * 10 ** (-14.0 / 10) * 50)
        i400 = math.sqrt(1e-3 * 10 ** (-14.0 / 10) / 400)
        rows += [
            ("chain, antenna to IF current, -40 dBm in", "%.1f mS, %.1f uA differential at 2.5 MHz"
             % (r["chain_40_gm_ms"], r["chain_40_i_ua"]), "", None),
            ("chain at the plan's -29 dBm full scale", "%.1f mS, %.1f uA differential"
             % (r.get("chain_29_gm_ms", nan), r.get("chain_29_i_ua", nan)),
             "%.0f uA rms if -14 dBm is read in 400 ohm, %.0f uA rms if read in 50 ohm"
             % (i400 * 1e6, v50 / 400 * 1e6), None),
            ("chain compression -40 to -29 dBm", "%.2f dB"
             % (20 * math.log10(r.get("chain_29_gm_ms", 1) / r["chain_40_gm_ms"])), "", None),
        ]
    if "mixer_iip3_at_antenna_dbm" in r:
        need = LP.analyse("1M")["iip3_req"]
        rows.append(("mixer IIP3 referred to the antenna", "%.1f dBm" % r["mixer_iip3_at_antenna_dbm"],
                     "chain needs %.1f dBm input referred" % need, r["mixer_iip3_at_antenna_dbm"] >= need))
    L = ["| | measured | level plan asks | |", "|---|---|---|---|"]
    for lab, val, ask, ok in rows:
        v = "" if ok is None else ("ok" if ok else "**short**")
        L.append("| %s | %s | %s | %s |" % (lab, val, ask, v))
    if "noise_shares_pct" in r:
        L.append("")
        L.append("Output noise at 2.44 GHz by contributor, bench load excluded: "
                 + ", ".join("%s %.0f%%" % (k, v) for k, v in r["noise_shares_pct"].items()) + ".")
    return "\n".join(L)


def splice(path, marker, body):
    with open(path) as fh:
        text = fh.read()
    o, c = "<!-- %s -->" % marker, "<!-- /%s -->" % marker
    i, j = text.index(o), text.index(c)
    with open(path, "w") as fh:
        fh.write(text[:i] + o + "\n\n" + body + "\n\n" + text[j:])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--macro", required=True, help="the LNA macro directory")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--plot", action="store_true",
                    help="open a plot window per bench (falls back to files without a DISPLAY)")
    ap.add_argument("--plotdir", default=None,
                    help="also write the figures as PNG into this directory")
    a = ap.parse_args()
    m = Macro(a.macro)
    r = measure(m)
    body = scorecard(m, r) if LP is not None else plain(r)
    print(body)
    if a.plot or a.write or a.plotdir:
        plots(m, a.plotdir or (os.path.join(m.dir, "doc") if a.write else None),
              show=a.plot)
    if a.write:
        splice(m.doc, "RESULTS", body)
        with open(m.json, "w") as fh:
            json.dump(r, fh, indent=2)
        print("updated %s" % m.doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
