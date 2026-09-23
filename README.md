# KV Open Source IC Design (336.004) in SS26

(c) 2026 Harald Pretl (harald.pretl@jku.at), Michael Köfinger (michael.koefinger@jku.at) and Simon Dorrer (simon.dorrer@jku.at)

Institute for Integrated Circuits and Quantum Computing (IICQC), Johannes Kepler University (JKU) Linz, Austria

Course material for course 336.004 (KV Open Source IC Design) at the JKU Linz in the summer semester of 2026 is stored here.

## Contents

* Folder `doc`:
    - Documentation about filter design
* Folder `python`:
    - Python script for filter design
* Folder `macros`:
    - `inverter`: analog reference macro
    - `counter`: digital reference macro
    - `amp_cs`: common-source amplifier macro
    - `filter_sky130`: filter macro, SS26 filter under `ihp-sg13cmos5l` and a
      legacy SKY130 amplifier under `sky130A`, see its `README.md`
    - `make macro FROM=<macro> NAME=<name>` starts a new macro as a renamed
      copy of an existing one, see [macros/README.md](macros/README.md)
* Moodle:
    - Project documentation (PDF)
