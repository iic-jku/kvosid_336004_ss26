#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Michael Koefinger, Johannes Kepler University
# SPDX-License-Identifier: Apache-2.0 WITH SHL-2.1
# Description: Audit an xschem-written VACASK (spectre-format) netlist for the silent failures

"""Fail on what xschem lets through without a word.

A missing symbol writes `IS MISSING` and exits 0, a wire one grid unit off a
pin makes a `net<N>` node, a pin nothing reaches appears exactly once, and a
symbol without `spectre_format` vanishes from the netlist entirely. This reads
the emitted netlist and turns each of those into an exit code.

    python3 vacask_netlist_audit.py <netlist.spectre> [--expect NAME ...]

`--expect` names instance masters that must appear at least once (the DUT
subcircuit, the PDK device), which is the only check that catches a vanished
symbol.
"""

import argparse
import collections
import re
import sys


def parse(text):
    """Yield (scope, instance name, nodes, master) for every instance line."""
    scope = "top"
    ports = {"top": []}
    inst = []
    in_ctrl = False
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("//"):
            continue
        if s.startswith("control"):
            in_ctrl = True
            continue
        if s.startswith("endc"):
            in_ctrl = False
            continue
        if in_ctrl:
            continue
        m = re.match(r"subckt\s+(\S+)\s*\((.*?)\)", s)
        if m:
            scope = m.group(1)
            ports[scope] = m.group(2).split()
            continue
        if s.startswith("ends"):
            scope = "top"
            continue
        m = re.match(r"([A-Za-z_][\w:]*)\s*\(([^)]*)\)\s*(\S+)", s)
        if m and not s.startswith(("include", "parameters", "model", "ground",
                                   "load", "save", "options", "analysis")):
            inst.append((scope, m.group(1), m.group(2).split(), m.group(3)))
    return ports, inst


def audit(text, expect=()):
    problems = []
    if "IS MISSING" in text:
        problems.append("a symbol IS MISSING (unresolved library path)")
    ports, inst = parse(text)
    masters = {i[3] for i in inst}
    for e in expect:
        if e not in masters:
            problems.append("expected master %r never instantiated (vanished symbol?)" % e)
    by_scope = collections.defaultdict(collections.Counter)
    for scope, _, nodes, _ in inst:
        for n in nodes:
            by_scope[scope][n] += 1
    for scope, cnt in by_scope.items():
        hdr = ports.get(scope, [])
        dangling = [n for n, c in cnt.items() if c < 2 and n not in hdr
                    and n not in ("0", "GND")]
        auto = [n for n in cnt if re.match(r"net\d", n)]
        unused = [p for p in hdr if p not in cnt]
        if dangling:
            problems.append("%s: node(s) touched once: %s" % (scope, dangling))
        if auto:
            problems.append("%s: autonamed node(s), a wire missed a pin: %s" % (scope, auto))
        if unused:
            problems.append("%s: declared port(s) unused: %s" % (scope, unused))
    return problems


def selftest():
    good = """subckt lna ( vin vout VSS )
r1 ( vin vout ) resistor r=1
r2 ( vout VSS ) resistor r=1
ends
x1 ( a b GND ) lna
v1 ( a GND ) vsource dc=1
r3 ( b GND ) resistor r=1
"""
    assert audit(good, expect=["lna"]) == []
    assert any("vanished" in p for p in audit(good, expect=["mixer"]))
    bad = good.replace("r2 ( vout VSS )", "r2 ( vout net1 )")
    p = audit(bad)
    assert any("autonamed" in x for x in p) and any("unused" in x for x in p), p
    once = good.replace("r3 ( b GND ) resistor r=1\n", "")
    assert any("touched once" in x for x in audit(once)), audit(once)
    assert any("IS MISSING" in x for x in audit(good + "x9 IS MISSING !!!!\n"))
    print("selftest: ok")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("netlist", nargs="?")
    ap.add_argument("--expect", nargs="*", default=[])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.netlist:
        ap.error("netlist required")
    with open(a.netlist) as fh:
        problems = audit(fh.read(), a.expect)
    for p in problems:
        print("AUDIT: " + p)
    print("%s: %s" % (a.netlist, "clean" if not problems else "%d problem(s)" % len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
