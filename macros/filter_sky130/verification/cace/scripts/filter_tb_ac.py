# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 Michael Koefinger
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Collect the AC/noise results of the SS26 anti-aliasing filter into
#              filter_tb_ac.csv, one row per CACE run, with the swept conditions alongside.
# ============================================

from typing import Any
from pathlib import Path

# The seven measurements filter_tb_ac.sch reports, in the order of its .data line.
VARIABLES = ['a_pass_db', 'f_pass', 'att_db', 'peak_db', 'eps_g', 'v_on', 'snr_db']

# Conditions worth recording next to each result.
CONDITIONS = ['gm', 'ro', 'co', 'i0', 'vdd', 'vcm', 'temp', 'corner_mos', 'corner_r',
              'rload', 'cload']


def _as_list(value: Any) -> list:
    return list(value) if isinstance(value, (list, tuple)) else [value]


def postprocess(results: dict[str, list], conditions: dict[str, Any]) -> dict[str, list]:
    """Append this run's results to cace/scripts/filter_tb_ac.csv.

    CACE invokes this once per run, so the file is APPENDED to and the header is written
    only when the file does not yet exist. `make sim-cace` deletes the .csv beforehand, so
    a full sweep starts clean; running `cace` by hand repeatedly will accumulate rows.

    Do NOT print from this hook: CACE 2.11.0 redirects stdout into its rich logger while
    the script runs and the logger writes back to stdout, so any print recurses forever.
    """
    cond_cols = [(n, _as_list(conditions[n])) for n in CONDITIONS if n in conditions]
    res_cols = [(n, _as_list(results.get(n, []))) for n in VARIABLES]

    cols = cond_cols + [c for c in res_cols if c[1]]
    arrays = {f'{n}_arr': v for n, v in res_cols}

    if cols:
        n_rows = min(len(v) for _, v in cols)
        path = Path('cace/scripts') / Path(__file__).with_suffix('.csv').name
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        if not path.exists():
            lines.append(','.join(n for n, _ in cols))
        for i in range(n_rows):
            lines.append(','.join(str(v[i] if len(v) > 1 else v[0]) for _, v in cols))
        with path.open('a') as fh:
            fh.write('\n'.join(lines) + '\n')

    return arrays
