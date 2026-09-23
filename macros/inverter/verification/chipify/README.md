# Chipify setup for a new schematic

Chipify renders an xschem testbench through Jinja2, sweeps it over a parameter grid and checks each run against specs.
This folder is a working example for the inverter macro. What follows is what it takes to point it at a different schematic, assuming the measurements and their limits are entered by hand in the GUI.

The container ships chipify 0.2.2.

## 1. Directory layout

Chipify resolves everything from the directory it is started in, so the project root is the contract.

```
<macro>/verification/chipify/
├─ settings.json      in_dir, out_dir, work_dir, tb_dir, sim_timeout_sec
├─ xschemrc           read by xschem, which chipify runs from this directory
├─ datasheets/        the YAML files, one per run
├─ tb/
│  ├─ <bench>.sch     the testbench
│  └─ xschemrc        one line, sources ../xschemrc
├─ work/              model files staged for the simulator, included by bare name
└─ out/               results
```

`xschemrc` has to add the macro's `schematic/xschem` to `XSCHEM_LIBRARY_PATH`, otherwise the DUT symbol does not resolve.
`tb/xschemrc` is never read by chipify, it is there so the bench also opens correctly when you start xschem from `tb/`.

## 2. Testbench changes

Start from the interactive bench and change four things.

- **Parameters become Jinja placeholders.** Braces are xschem delimiters, so escape them in the `.sch` source: `.temp \{\{ temp \}\}`, `.param VDD=\{\{ vdd \}\}`, `.lib cornerMOSlv.lib mos_\{\{ corner_mos \}\}`. A placeholder with no matching `parameters:` key fails that bench with `TEMPLATE_RENDER_ERROR`, and comments are rendered too, so a brace pair in a comment is enough to break it.
- **Remove everything that writes results.** No `save all`, no `write ....raw`, no `wrdata`, no `plot`, and no `echo MY_DATA:`. Chipify injects its own capture line.
- **Keep a `quit`** in the `.control` block. The capture line is spliced in before it.
- **Drop anything the GUI provides.** The `.include <bench>.save` block is written by the Simulate launcher and nothing writes it here. A relative `.include` of a netlist elsewhere in the macro also breaks, because the simulator runs in a scratch directory. Put such a file in `work/` and include it by bare filename.

Every quantity you want to measure has to be a **bare vector**. `.meas` results already are. A raw node needs an alias, `let vout_dc = v(vout)`, because the ngspice name of that vector is literally `v(vout)`.

Check the bench the way chipify netlists it, from the project root:

```sh
xschem -n --spice -q -x -o /tmp/x tb/<bench>.sch
grep -c "^.subckt <dut>" /tmp/x/<bench>.spice
```

A missing symbol is silent: xschem exits 0 and leaves the instance out.

## 3. Datasheet

The measurements are added in the GUI, so the YAML only has to carry the sweep and name the bench.
The key under `tests:` is the schematic filename without `.sch`.

```yaml
parameters:
  vdd: [1.5]
  temp: [27]
  corner_mos: ['tt', 'ss', 'ff']

tests:
  <bench>:
    engine: ngspice      # or vacask
    source: xschem       # or netlist, to use an existing tb/<bench>.spice
```

`parameters:` is a full Cartesian product, so a parameter no bench uses still multiplies the run count.
Only `range(...)`, `linspace(...)` and `logspace(...)` are available as sequences.

## 4. Run

```sh
cd <macro>/verification/chipify
chipify                                   # GUI
chipify-cli -c <name>.yaml --json         # same thing headless
```

Results land in `out/simulation_results.csv`, one row per case, with each measurement and its `_pass` column.
`out/chipify.log` carries the full trace.

## 5. Traps

- `sim_timeout_sec` defaults to 10 s per case. Raise it before any real transient, otherwise a slow bench returns `TIMEOUT` while the rest of the row looks healthy.
- Only `min` and `max` decide pass or fail. `typ` and `unit` are documentation, so carry the scale in the value.
- Top-level `equations:` are applied by the GUI only. They never reach the CSV or the CLI summary, so anything you want recorded belongs in the bench as a `let`.
- For Monte Carlo, `seed: range(N)` only works if it reaches a `.option SEED=\{\{ seed \}\}` in the bench, otherwise every case repeats one draw. Local mismatch additionally needs `mm_ok=1` on the instances, and a `*_stat` corner section is global process variation, not mismatch.

## Failure messages

| Message | Cause |
|---|---|
| `TEMPLATE_RENDER_ERROR` | a placeholder with no `parameters:` key |
| `NO_MY_DATA_FOUND` | the run produced no capture line, often a missing `quit` |
| `INVALID_OUTPUT(...)` | a measurement key that is not a bare vector |
| `TIMEOUT` | the case exceeded `sim_timeout_sec` |
| `ENGINE_ERROR` / `CRASH` | the simulator exited non-zero, tail in the message |
