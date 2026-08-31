# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Michael Koefinger
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: AC and noise plots for the SS26 anti-aliasing filter, from the text exports
#              written by filter_cl_ideal_tb.sch (wrdata into plot_simulations/data).
# ============================================

# Imports
import os
import numpy as np
import matplotlib.pyplot as plt
import ngspice2python as ng
from pathlib import Path
# ============================================

# Specifications, see the lecture slides (section "Specifications")
F_PASS = 1.0e6          # -3 dB corner, Hz
F_STOP = 9.0e6          # f_s - f_pass, Hz (5e6 if the full Nyquist band is used)
A_PASS_DB = 20.0        # pass-band gain, dB
ATT_MIN_DB = 49.9       # stop-band attenuation at f_stop, dB
V_ON_MAX = 113e-6       # integrated output-referred noise, Vrms
F_N_MIN, F_N_MAX = 100.0, F_STOP    # noise integration band, Hz

plt.close("all")
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.size": 14,
})
# =========================================================================


def _fmt_hz(f):
    for prefix, scale in (('G', 1e9), ('M', 1e6), ('k', 1e3)):
        if f >= scale:
            return rf"{f/scale:.3f}\,\mathrm{{{prefix}Hz}}"
    return rf"{f:.2f}\,\mathrm{{Hz}}"


def plot_ac(data_dir, figures_dir):
    """Bode plot of the closed-loop filter response, annotated against the specification."""
    f = data_dir / "filter_cl_ideal_tb_ac.txt"
    if not f.exists():
        print(f"missing {f} - run: make sim-xschem TB=filter_cl_ideal_tb")
        return None

    frequency = ng.loadngspicecol(str(f), "frequency")
    mag_dB = ng.loadngspicecol(str(f), "Amag_dB")
    phase_deg = ng.loadngspicecol(str(f), "Aarg")

    # pass-band gain well below the corner, then the -3 dB point and the stop-band
    a_pass = float(np.interp(10e3, frequency, mag_dB))
    mag_asc, freq_desc = mag_dB[::-1], frequency[::-1]
    f_3db = float(np.interp(a_pass - 3.0, mag_asc, freq_desc))
    a_stop = float(np.interp(F_STOP, frequency, mag_dB))
    att = a_pass - a_stop

    fig, axs = plt.subplots(2, figsize=(10, 7))
    fig.suptitle('SS26 anti-aliasing filter - closed-loop AC response')

    axs[0].set_xscale('log')
    axs[0].plot(frequency, mag_dB, color='#0c5da5', linewidth=2.4)
    axs[0].set_xlabel('$f$ (Hz)')
    axs[0].set_ylabel(r'$|H(f)|$ (dB)')
    axs[0].grid(visible=True, which='both', linestyle='--', alpha=0.5)

    marker = '#444444'
    line_kw = dict(color=marker, linestyle=':', linewidth=1.2, alpha=0.85)
    pt_kw = dict(marker='o', color=marker, linestyle='None', markersize=6, zorder=5)
    box_kw = dict(boxstyle='round,pad=0.4', fc='white', ec=marker, alpha=0.9)

    axs[0].axhline(a_pass, **line_kw)
    axs[0].axvline(f_3db, **line_kw)
    axs[0].axvline(F_STOP, **line_kw)
    axs[0].plot([f_3db], [a_pass - 3.0], **pt_kw)
    axs[0].plot([F_STOP], [a_stop], **pt_kw)
    # the specification limit, so a failing design is visible at a glance
    axs[0].plot([F_STOP], [a_pass - ATT_MIN_DB], marker='_', color='#c0392b',
                markersize=18, markeredgewidth=2.5, linestyle='None', zorder=6)

    ok = 'OK' if att >= ATT_MIN_DB else 'FAIL'
    axs[0].text(0.02, 0.05, '\n'.join((
        rf'$A_\mathrm{{pass}} = {a_pass:.2f}\,\mathrm{{dB}}$ (spec ${A_PASS_DB:.0f}$)',
        rf'$f_\mathrm{{pass}} = {_fmt_hz(f_3db)}$ (spec ${_fmt_hz(F_PASS)}$)',
        rf'$a_\mathrm{{stop}} = {att:.1f}\,\mathrm{{dB}}$ @ ${_fmt_hz(F_STOP)}$ '
        rf'(spec $\geq {ATT_MIN_DB}$) {ok}',
    )), transform=axs[0].transAxes, ha='left', va='bottom', color=marker,
        bbox=box_kw, zorder=6)

    axs[1].set_xscale('log')
    axs[1].plot(frequency, phase_deg, color='#ff6b35', linewidth=2.4)
    axs[1].set_xlabel('$f$ (Hz)')
    axs[1].set_ylabel(r'$\angle H(f)$ ($^\circ$)')
    axs[1].axvline(f_3db, **line_kw)
    axs[1].grid(visible=True, which='both', linestyle='--', alpha=0.5)

    plt.tight_layout()
    for ext in ('svg', 'pdf'):
        fig.savefig(str(figures_dir / f"filter_cl_ideal_tb_ac.{ext}"), bbox_inches='tight')
    np.savetxt(str(figures_dir / "filter_cl_ideal_tb_ac.csv"),
               np.column_stack((frequency, mag_dB, phase_deg)), comments="",
               header="frequency,Amag_dB,Aarg", delimiter=",")
    return fig


def plot_noise(data_dir, figures_dir):
    """Output-referred noise density, with the integrated value over the spec band."""
    f = data_dir / "filter_cl_ideal_tb_noise.txt"
    if not f.exists():
        print(f"missing {f} - run: make sim-xschem TB=filter_cl_ideal_tb")
        return None

    frequency = ng.loadngspicecol(str(f), "frequency")
    # ngspice reports onoise_spectrum in V/sqrt(Hz) unless "set sqrnoise" is active,
    # which this testbench leaves off - so it is already a voltage density
    density = np.abs(ng.loadngspicecol(str(f), "onoise_spectrum"))

    band = (frequency >= F_N_MIN) & (frequency <= F_N_MAX)
    # np.trapezoid is numpy >= 2.0; trapz is the older spelling
    _integrate = getattr(np, 'trapezoid', None) or np.trapz
    v_on = float(np.sqrt(_integrate(density[band] ** 2, frequency[band]))) \
        if band.any() else float('nan')

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle('SS26 anti-aliasing filter - output-referred noise')
    ax.loglog(frequency, density * 1e9, color='#0c5da5', linewidth=2.4)
    ax.set_xlabel('$f$ (Hz)')
    ax.set_ylabel(r'$\sqrt{S_\mathrm{o}(f)}$ (nV$/\sqrt{\mathrm{Hz}}$)')
    ax.grid(visible=True, which='both', linestyle='--', alpha=0.5)
    ax.axvline(F_N_MAX, color='#444444', linestyle=':', linewidth=1.2, alpha=0.85)

    ok = 'OK' if v_on <= V_ON_MAX else 'FAIL'
    ax.text(0.02, 0.05, '\n'.join((
        rf'$V_\mathrm{{o,n}} = {v_on*1e6:.0f}\,\mathrm{{\mu V_{{rms}}}}$ '
        rf'(${F_N_MIN:.0f}\,\mathrm{{Hz}}$ to ${_fmt_hz(F_N_MAX)}$)',
        rf'spec $\leq {V_ON_MAX*1e6:.0f}\,\mathrm{{\mu V_{{rms}}}}$  {ok}',
    )), transform=ax.transAxes, ha='left', va='bottom', color='#444444',
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='#444444', alpha=0.9))

    plt.tight_layout()
    for ext in ('svg', 'pdf'):
        fig.savefig(str(figures_dir / f"filter_cl_ideal_tb_noise.{ext}"), bbox_inches='tight')
    np.savetxt(str(figures_dir / "filter_cl_ideal_tb_noise.csv"),
               np.column_stack((frequency, density)), comments="",
               header="frequency,onoise_density", delimiter=",")
    return fig


def main():
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    figs = [plot_ac(data_dir, figures_dir), plot_noise(data_dir, figures_dir)]

    # SHOW_PLOTS is set by "make sim-view-xschem"; without it the run stays batch-friendly
    if any(f is not None for f in figs) and os.environ.get('SHOW_PLOTS'):
        plt.show()
# =========================================================================


if __name__ == '__main__':
    main()
