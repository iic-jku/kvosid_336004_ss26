# Filter Macro (KV 336.004, SS26)

Template macro for the anti-aliasing filter of the course project. It holds two things, and neither is a finished design:

1. **The original SKY130 example**: the transistor-level amplifier [`schematic/xschem/amp.sch`](schematic/xschem/amp.sch) with the testbenches `filter_cl_tb.sch`, `filter_loopgain_tb.sch` and `amp_ol_tb.sch`. These instantiate SKY130 devices (`sky130_fd_pr__nfet_01v8`, `sky130_fd_pr__pfet_01v8`) and have **not** been ported to SG13CMOS5L. That is where the folder name comes from. Run them with `sak-pdk sky130A`.
2. **The updated SS26 filter**: [`schematic/xschem/filter.sch`](schematic/xschem/filter.sch), a 3rd-order MFB low-pass (biquad plus a unity-gain output stage) whose amplifiers are the behavioural single-stage `ota_fd_2pole` macro model. It carries no PDK devices and runs under `ihp-sg13cmos5l`, which is what the `xschemrc` files and the CACE datasheets select.

Because the amplifier of the SS26 filter is behavioural, supply current, process corners and mismatch are declared in the CACE datasheet but inert until a transistor OTA replaces the macro model.

There is **no layout**. The build, DRC, LVS and PEX targets are in the Makefile for when one exists, but they cannot run today, and the cell names `filter` and `filter_top` are placeholders. `make all` therefore fails at its first step; use `make sim-all`.


## Directory Structure

```text
📁 filter_sky130/
├─ 📁 schematic/xschem/
│  ├─ amp.sch              SKY130 transistor amplifier (legacy example)
│  ├─ cmfb_ideal.sch       ideal common-mode feedback
│  ├─ filter.sch           SS26 3rd-order MFB low-pass
│  ├─ ota_fd_2pole.sch     behavioural fully-differential OTA macro model
│  ├─ rstring_cm.sch       common-mode resistor string (SKY130 devices)
│  └─ xschemrc
├─ 📁 scripts/
│  ├─ check_boundary.py    PR boundary check, for a future layout
│  ├─ check_pex_ports.py   PEX port check, for a future layout
│  └─ 📁 sizing/           gm/ID template, notebooks and .mat data are SG13CMOS5L
├─ 📁 testbenches/xschem/
│  ├─ amp_ol_tb.sch            open loop, SKY130 amp
│  ├─ filter_cl_ideal_tb.sch   closed loop, behavioural OTA (default TB)
│  ├─ filter_cl_tb.sch         closed loop, SKY130 amp
│  ├─ filter_loopgain_tb.sch   loop gain
│  ├─ ota_fd_2pole_tb.sch      the OTA macro model on its own
│  ├─ 📁 plot_simulations/     plot_filter.py, plot_filter_top.py, ngspice2python.py
│  ├─ 📁 simulations/          ngspice output, build artifacts
│  └─ xschemrc
├─ 📁 verification/cace/
│  ├─ filter.yaml          CACE datasheet of the filter
│  ├─ filter_gbw.yaml      GBW sweep, checks f_n against the rule of thumb
│  ├─ 📁 scripts/          filter_tb_ac.py and its limits
│  └─ 📁 templates/        CACE testbench templates and xschemrc
├─ Makefile
└─ README.md
```


## PDK

The two halves of this macro do not share a PDK:

| Part | PDK | Set with |
| --- | --- | --- |
| `filter.sch`, `ota_fd_2pole.sch`, both CACE datasheets | `ihp-sg13cmos5l` | `sak-pdk ihp-sg13cmos5l` |
| `amp.sch`, `rstring_cm.sch`, `filter_cl_tb.sch`, `amp_ol_tb.sch` | `sky130A` | `sak-pdk sky130A` |

The `xschemrc` files set `ihp-sg13cmos5l` only as a fallback for when `$PDK` is unset; the value in the shell wins. Switch the PDK before running a testbench from the other half.


## Makefile Targets

### Show Available Targets

```sh
make help
```


### Simulate with Xschem

```sh
make sim-xschem                            # default TB, filter_cl_ideal_tb
make sim-xschem TB=ota_fd_2pole_tb
make sim-xschem TB=filter_loopgain_tb
make sim-xschem TB=amp_ol_tb               # needs sak-pdk sky130A
make sim-xschem TB=filter_cl_tb            # needs sak-pdk sky130A
```

Results land in `testbenches/xschem/simulations/`. Plot them with:

```sh
make sim-view-xschem SCRIPT=plot_filter
```

`SCRIPT` defaults to `plot_$(CELL)`, and `CELL` defaults to the placeholder `filter_top`, so pass `SCRIPT=plot_filter` explicitly.


### CACE Characterization

```sh
make sim-cace        # verification/cace/filter.yaml
make sim-cace-gbw    # verification/cace/filter_gbw.yaml
```

`sim-cace-gbw` sweeps the GBW of the `ota_fd_2pole` macro model and checks the measured biquad `f_n` against the closed-form rule of thumb derived in the lecture appendix:

```text
|df_n/f_n| = (Q * f_n / f_ug) * (1/beta_0 + R2/R3) / 2
```

Result plots are copied to `verification/cace/results/`, and the temporary `_runs`, `_docs` and `netlist` folders under `verification/cace/` are removed at the end.


### Simulate Everything

```sh
make sim-all         # sim-xschem with the default TB, then sim-cace
```


### Clean

```sh
make clean
```


### Targets That Cannot Run Yet

`all`, `build-top`, `check-boundary`, `lef`, `lib`, `verilog`, `copy-gds`, `render-gds`, `klayout-drc`, `magic-drc`, `klayout-lvs`, `magic-lvs`, `klayout-pex`, `magic-pex`, `symbol-pex` and the `*-verify*` targets all need a `layout/` folder. They are kept so that the macro is complete once a layout exists.


## What Is Left to Do

1. Replace the behavioural `ota_fd_2pole` macro model with a transistor-level OTA in the target PDK. The supply current, corner and mismatch entries of `verification/cace/filter.yaml` become meaningful at that point.
2. Port or delete the SKY130 half: `amp.sch`, `rstring_cm.sch`, `filter_cl_tb.sch` and `amp_ol_tb.sch`.
3. Draw the layout in `layout/`, then the build, DRC, LVS and PEX targets apply and the `filter`/`filter_top` cell names become real.
4. `scripts/sizing/` is a gm/ID template carried over from the inverter macro: the notebook `sizing_inverter.ipynb`, the figures in `figures/` and the `sg13cmos5l_*.mat` lookup data. Adapt or delete them.

> [!NOTE]
> To start a new macro from this one, use `make macro FROM=filter_sky130 NAME=<name>` in [`macros/`](../README.md) rather than copying by hand.
