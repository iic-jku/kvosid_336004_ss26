#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Evaluate the lna_inv VACASK benches, the postprocess both benches run

"""Read the raws of lna_inv_tb_sp, lna_inv_tb_hb and lna_inv_tb_blocker, report and plot what they measured.

    python3 scripts/lna_inv_post.py            # print the table
    python3 scripts/lna_inv_post.py --plot     # and open the plot windows
    python3 scripts/lna_inv_post.py --write    # splice doc/lna_inv_feasibility.md, write doc/lna_inv_results.json

Every bench ends its control block with this script as the VACASK postprocess.
The bench load resistor stands in for the stage after the LNA, so NF is quoted
with its noise removed and once with it in.
"""

import argparse
import json
import math
import os
import sys

import numpy as np

TOP = "lna_inv"
MACRO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM = os.path.join(MACRO, "testbenches", "xschem", "simulations")
DOC = os.path.join(MACRO, "doc", TOP + "_feasibility.md")
JSON = os.path.join(MACRO, "doc", TOP + "_results.json")

F0 = 2.44e9
F1 = 2.441e9
FB = 2.40e9                   # the blocker bench's blocker
RS = 50.0
RL = 200.0
KT = 1.380649e-23 * 300.15    # every bench runs at temp=27


def dbm_avail(ampl):
    """Available power of a source amplitude behind RS, dBm."""
    return 10 * math.log10(ampl ** 2 / (8 * RS) / 1e-3)


def dbm_out(v_peak):
    """Power a peak voltage delivers into RL, dBm."""
    return 10 * math.log10(v_peak ** 2 / (2 * RL) / 1e-3)


def transducer_gain_db(v_peak, ampl):
    """Power delivered to RL over power available from the source, dB.

    The earlier form, 20*log10(v/RL / (ampl/2)), is a current over a voltage,
    so it is a transconductance in dB relative to 1 S and not a gain at all:
    it reads -32.3 dB where this reads +7.7 dB, for 24.2 mS.
    """
    return dbm_out(v_peak) - dbm_avail(ampl)


class Raws:
    """The raw files in one directory, by analysis name. A missing one reads as None."""

    def __init__(self, directory=SIM):
        self.dir = directory

    def __call__(self, name, sweeps=0):
        from rawfile import rawread
        p = os.path.join(self.dir, name + ".raw")
        if not os.path.exists(p):
            return None
        return rawread(p).get(sweeps=sweeps)


def small_signal(raw):
    """Supply current, match, gain, selectivity and noise from the lna_inv_tb_sp raws.

    lna_inv_sweep.py runs this on every sweep point, so the sweep and the
    bench report the same numbers.
    """
    out = {}
    op = raw("op1")
    if op is not None:
        out["idd_ma"] = -float(np.real(op["vsup:flow(br)"][0])) * 1e3
    sp = raw("sp1")
    if sp is not None:
        f = np.real(sp["frequency"])
        k = np.argmin(abs(f - F0))
        s11 = abs(sp["s(1,1)"])
        out["s11_db"] = float(20 * np.log10(s11[k]))
        out["s11_min_db"] = float(20 * np.log10(s11.min()))
        out["s11_min_ghz"] = float(f[np.argmin(s11)] / 1e9)
        out["s21_db"] = float(20 * np.log10(abs(sp["s(2,1)"][k])))
    sp2 = raw("sp2")
    if sp2 is not None:
        # selectivity: |S21| below its value at F0 per offset, the weaker side of the two
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
    ac = raw("ac1")
    if ac is not None:
        f = np.real(ac["frequency"])
        k = np.argmin(abs(f - F0))
        out["gm_eff_ms"] = float(abs(ac["vout"][k]) / RL / 0.5 * 1e3)
    nz = raw("n1")
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
    return out


def large_signal(raw):
    """Compression and intermodulation from the lna_inv_tb_hb raws."""
    out = {}
    hb = raw("hb1", sweeps=1)
    if hb is not None:
        pts = []
        for ii in range(hb.sweepGroups):
            f = np.real(hb[ii, "frequency"])
            v = abs(hb[ii, "vout"][np.argmin(abs(f - F0))])
            a = float(np.real(hb.sweepData(ii)["pin"]))
            pts.append((dbm_avail(a), transducer_gain_db(v, a)))
        out["hb_points"] = pts
        out["p1db_dbm"] = first_below(pts, pts[0][1] - 1.0)
    for name, key in (("hb2", "iip3_dbm_40"), ("hb3", "iip3_dbm_30")):
        h = raw(name)
        if h is None:
            continue
        f = np.real(h["frequency"])
        v = abs(h["vout"])
        fund = v[np.argmin(abs(f - F0))]
        im3 = v[np.argmin(abs(f - (2 * F0 - F1)))]
        pin = -40.0 if name == "hb2" else -30.0
        out[key] = float(pin + 0.5 * 20 * np.log10(fund / im3))
    return out


def first_below(pts, y):
    """Where the curve [(x, value), ...] first drops below y, linearly interpolated. None if it never does."""
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if yb < y <= ya:
            return xa + (xb - xa) * (ya - y) / (ya - yb)
    return None


def nf_ssb_db(p, i=None, f=F0):
    """Single-sideband noise figure at output frequency f from a noise or hbnoise result, bench load excluded.

    The denominator is 4kT RS gain, the source noise that reaches the output from the
    signal frequency alone. Under a blocker the folded n(rs) also carries source noise
    converted from the other sidebands, and dividing by it would hide that degradation.
    """
    get = (lambda n: p[n]) if i is None else (lambda n: p[i, n])
    k = np.argmin(abs(np.real(get("frequency")) - (f if i is None else f - FB)))
    tot, rl, g = (float(np.real(get(n)[k])) for n in ("onoise", "n(rl)", "gain"))
    return 10 * math.log10((tot - rl) / (4 * KT * RS * g))


def blocker(raw):
    """Wanted-tone gain and noise figure under the 2.40 GHz blocker, from the lna_inv_tb_blocker raws.

    The bench runs RFMODE=0 like the HB bench, so the unblocked numbers are the plain
    model's, and the change with the blocker is what to read.
    """
    out = {}
    ac0, nz0 = raw("ac0"), raw("nz0")
    bac, bnz = raw("bac", sweeps=1), raw("bnz", sweeps=1)
    if ac0 is not None and bac is not None:
        g0 = abs(ac0["vout"][0])
        pts = [[dbm_avail(float(np.real(bac.sweepData(i)["pb"]))),
                float(20 * np.log10(abs(bac[i, "vout;1"][0]) / g0))] for i in range(bac.sweepGroups)]
        out["blocker_gain_db"] = pts
        out["blocker_1db_dbm"] = first_below(pts, -1.0)
    if nz0 is not None:
        out["nf_rfmode0_db"] = nf_ssb_db(nz0)
    if bnz is not None:
        out["blocker_nf_db"] = [[dbm_avail(float(np.real(bnz.sweepData(i)["pbn"]))), nf_ssb_db(bnz, i)]
                                for i in range(bnz.sweepGroups)]
    return out


def measure(raw):
    return dict({"top": TOP}, **small_signal(raw), **large_signal(raw), **blocker(raw))


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


def plots(raw, outdir=None, show=False):
    """Draw what the benches measured, grouped into five windows.

    show=True opens the windows and blocks until they are closed.
    outdir writes a PNG per window. Both together do both.
    """
    plt = _pyplot(show)
    if plt is None:
        print("  plotting skipped: matplotlib not available")
        return []
    windows = show and plt.get_backend().lower() != "agg"
    if outdir is None and not windows:
        outdir = os.path.join(MACRO, "doc")
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir)
    written = []

    def save(fig, name):
        fig.tight_layout()
        if outdir:
            path = os.path.join(outdir, "%s_%s.png" % (TOP, name))
            fig.savefig(path, dpi=150)
            written.append(path)
        if not windows:
            plt.close(fig)

    sp, sp2 = raw("sp1"), raw("sp2")
    ac, nz = raw("ac1"), raw("n1")
    hb = raw("hb1", sweeps=1)

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
        save(_grid(plt, panels, "%s: small signal" % TOP), "smallsignal")

    # ---- window 2: how it behaves as the drive rises ---------------------
    if hb is not None and hb.sweepGroups:
        pin_ax, gain, rel, absl = [], [], {2: [], 3: []}, {1: [], 2: [], 3: []}
        for i in range(hb.sweepGroups):
            f = np.real(hb[i, "frequency"])
            v = abs(hb[i, "vout"])
            a = float(np.real(hb.sweepData(i)["pin"]))
            fund = v[np.argmin(abs(f - F0))]
            pin_ax.append(dbm_avail(a))
            gain.append(transducer_gain_db(fund, a))
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
                   ylabel="transducer power gain (dB)", title="gain compression")
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

        save(_grid(plt, [p_comp, p_abs, p_rel], "%s: large signal" % TOP), "largesignal")

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

        save(_grid(plt, [p_spec, p_wave], "%s: harmonic balance, raw" % TOP),
             "hb_raw")

    # ---- window 4: the two-tone benches ----------------------------------
    panels, tone_pts = [], []
    for name, pin_dbm in (("hb2", -40.0), ("hb3", -30.0)):
        h = raw(name)
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
            ax.set_ylim(floor, lev.max() + 28)
            for fx, lab in ((F0, "F0"), (F1, "F1"),
                            (2 * F0 - F1, "2F0-F1"), (2 * F1 - F0, "2F1-F0")):
                ax.axvline((fx - F0) / 1e6, color="0.6", ls=":", lw=1)
                ax.annotate(lab, ((fx - F0) / 1e6, ax.get_ylim()[1]), fontsize=7,
                            ha="center", va="top")

            # the number a designer reads off this panel: how far the IM3
            # products sit below the carrier, and how far the empty bins sit
            # below the IM3, which is what says the product is real
            fund = _dbv(v[np.argmin(abs(f - F0))])
            for fx in (2 * F0 - F1, 2 * F1 - F0):
                lv = _dbv(v[np.argmin(abs(f - fx))])
                ax.annotate("%.1f dBc" % (lv - fund), ((fx - F0) / 1e6, lv),
                            textcoords="offset points", xytext=(0, 7),
                            ha="center", fontsize=8, color="C3")
            im3 = _dbv(v[np.argmin(abs(f - (2 * F0 - F1)))])
            empty = [_dbv(v[k]) for k, fr in enumerate(f)
                     if band[k] and min(abs(fr - fx) for fx in
                                        (F0, F1, 2 * F0 - F1, 2 * F1 - F0,
                                         3 * F0 - 2 * F1, 3 * F1 - 2 * F0)) > 1e3]
            note = "IM3 %.1f dBV" % im3
            if empty:
                note += "\nfloor %.0f dBV, %.0f dB below" % (max(empty), im3 - max(empty))
            ax.text(0.02, 0.88, note, transform=ax.transAxes, ha="left",
                    va="top", fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7"))
            ax.set(xlabel="offset from F0 (MHz)", ylabel="output (dBV)",
                   title="two tones at %.0f dBm each" % pin_dbm)
        panels.append(p_tt)
        tone_pts.append((pin_dbm, dbm_out(v[np.argmin(abs(f - F0))]),
                         dbm_out(v[np.argmin(abs(f - (2 * F0 - F1)))])))

    # the classic IP3 construction: slope 1 through the fundamental, slope 3
    # through the IM3, and the intercept where the extrapolations meet
    if len(tone_pts) >= 1:
        def p_ip3(ax):
            pin = np.array([q[0] for q in tone_pts])
            fun = np.array([q[1] for q in tone_pts])
            im3 = np.array([q[2] for q in tone_pts])
            iip3 = (im3[0] - fun[0]) / (1 - 3) + pin[0]
            oip3 = fun[0] + (iip3 - pin[0])
            x = np.array([pin.min() - 5, iip3 + 3])
            ax.plot(x, fun[0] + 1 * (x - pin[0]), "--", color="C0", lw=1,
                    label="slope 1")
            ax.plot(x, im3[0] + 3 * (x - pin[0]), "--", color="C1", lw=1,
                    label="slope 3")
            ax.plot(pin, fun, "o", color="C0", label="fundamental")
            ax.plot(pin, im3, "s", color="C1", label="IM3")
            ax.plot([iip3], [oip3], "*", color="k", ms=12)
            ax.text(0.97, 0.04, "IIP3 %.1f dBm\nOIP3 %.1f dBm" % (iip3, oip3),
                    transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.7"))
            ax.axvline(iip3, color="0.7", ls=":", lw=1)
            if len(tone_pts) > 1:
                sf = (fun[-1] - fun[0]) / (pin[-1] - pin[0])
                si = (im3[-1] - im3[0]) / (pin[-1] - pin[0])
                ax.set_title("third-order intercept (measured slopes %.2f and %.2f)"
                             % (sf, si))
            else:
                ax.set_title("third-order intercept")
            ax.set(xlabel="available input power per tone (dBm)",
                   ylabel="output power (dBm)")
            ax.legend(fontsize=7, loc="upper left")
        panels.append(p_ip3)

    if panels:
        save(_grid(plt, panels, "%s: intermodulation" % TOP), "twotone")

    # ---- window 5: the wanted tone under the blocker ---------------------
    b = blocker(raw)
    xlab = "blocker at %.2f GHz, available power (dBm)" % (FB / 1e9)
    panels = []
    if "blocker_gain_db" in b:
        def p_desense(ax):
            x, y = zip(*b["blocker_gain_db"])
            ax.plot(x, y, "o-")
            ax.axhline(-1.0, color="0.6", ls=":", lw=1, label="-1 dB")
            ax.set(xlabel=xlab, ylabel="wanted gain change (dB)",
                   title="gain at %.2f GHz (hbac)" % (F0 / 1e9))
            ax.legend(fontsize=8)
        panels.append(p_desense)
    if "blocker_nf_db" in b:
        def p_bnf(ax):
            x, y = zip(*b["blocker_nf_db"])
            ax.plot(x, y, "o-", label="under the blocker (hbnoise)")
            if "nf_rfmode0_db" in b:
                ax.axhline(b["nf_rfmode0_db"], color="0.6", ls=":", lw=1, label="no blocker (noise)")
            ax.set(xlabel=xlab, ylabel="SSB noise figure (dB)",
                   title="noise figure at %.2f GHz, RFMODE=0" % (F0 / 1e9))
            ax.legend(fontsize=8)
        panels.append(p_bnf)
    if panels:
        save(_grid(plt, panels, "%s: under a blocker" % TOP), "blocker")

    for path in written:
        print("  wrote %s" % path)
    if windows:
        print("  close the %d plot windows to continue" % len(plt.get_fignums()))
        plt.show()
    return written


def report(r):
    """The measurements as a Markdown table. A bench that has not run shows as such."""
    def val(key, fmt):
        return fmt % r[key] if key in r else "not run"

    s11 = val("s11_db", "%.1f dB")
    if "s11_db" in r:
        s11 += " (best %.1f dB at %.3f GHz)" % (r["s11_min_db"], r["s11_min_ghz"])
    p1 = "not run"
    if "hb_points" in r:
        p1 = "not reached in the sweep" if r["p1db_dbm"] is None else "%.1f dBm" % r["p1db_dbm"]
    rows = [
        ("noise figure, bench load excluded", val("nf_db", "%.2f dB")),
        ("noise figure, bench load counted", val("nf_with_load_db", "%.2f dB")),
        ("transconductance into %.0f ohm, source available voltage to output current" % RL,
         val("gm_eff_ms", "%.1f mS")),
        ("S11 at 2.44 GHz", s11),
        ("S21 at 2.44 GHz", val("s21_db", "%.1f dB")),
        ("input P1dB", p1),
        ("IIP3, two tones at -40 dBm", val("iip3_dbm_40", "%.1f dBm")),
        ("IIP3, two tones at -30 dBm", val("iip3_dbm_30", "%.1f dBm")),
        ("supply current", val("idd_ma", "%.2f mA at 1.2 V")),
    ]
    if "blocker_gain_db" in r:
        x = r["blocker_1db_dbm"]
        rows.append(("2.40 GHz blocker that costs the wanted tone 1 dB (hbac, RFMODE=0)",
                     "not reached" if x is None else "%.1f dBm" % x))
    if "blocker_nf_db" in r and "nf_rfmode0_db" in r:
        nf = {round(x): y for x, y in r["blocker_nf_db"]}
        rows.append(("noise figure under a 2.40 GHz blocker (hbnoise, RFMODE=0)",
                     "%.2f dB without, %.2f dB at -10 dBm, %.2f dB at 0 dBm"
                     % (r["nf_rfmode0_db"], nf.get(-10, float("nan")), nf.get(0, float("nan")))))
    L = ["| | measured |", "|---|---|"]
    L += ["| %s | %s |" % row for row in rows]
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
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--plot", action="store_true",
                    help="open the plot windows (falls back to files without a DISPLAY)")
    ap.add_argument("--plotdir", default=None,
                    help="also write the figures as PNG into this directory")
    a = ap.parse_args()
    raw = Raws()
    r = measure(raw)
    body = report(r)
    print(body)
    if a.plot or a.write or a.plotdir:
        plots(raw, a.plotdir or (os.path.join(MACRO, "doc") if a.write else None),
              show=a.plot)
    if a.write:
        splice(DOC, "RESULTS", body)
        with open(JSON, "w") as fh:
            json.dump(r, fh, indent=2)
        print("updated %s" % DOC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
