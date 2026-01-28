# KV Open Source IC Design (336.004) in SS26

Institute for Integrated Circuits and Quantum Computing (IICQC), Johannes Kepler University (JKU) Linz, Austria

(c) 2026 Harald Pretl ([harald.pretl@jku.at](mailto:harald.pretl@jku.at)), IICQC, JKU

(c) 2026 Simon Dorrer ([simon.dorrer@jku.at](mailto:simon.dorrer@jku.at)), IICQC, JKU

(c) 2026 Michael Köfinger ([michael.köfinger@jku.at](mailto:michael.köfinger@jku.at)), IICQC, JKU

Course material for course 336.004 (KV Open Source IC Design) at the JKU Linz in the summer semester of 2026 is stored here.

## Contents

* Folder `doc`:
    - Documentation about filter design and layout automation with `IIC-RALF` (optional).
* Folder `layout`:
    - Files for `IIC-RALF`
* Folder `python`:
    - Python script for filter design
* Folder `xschem`:
    - Analog simulation testbenches for reference filter design.
* Moodle:
    - Project documentation (PDF)

## Brainstorming:

- Timeline: 29.09. - 02.10.2026, 8:30 - 12:00
- Room: SCP3 058
- IHP130 instead of SKY130
- CACE instead of RALF
- Filter Topology stays the same
- Circuit Starting Point stays the same
- Grade depending on power consumption
- Tasks:
    - Port the SKY130 circuits & testbenches to IHP130
    - Script for Filter Design (consider load of ADC)
    - Improve the starting point circuit for the given specifications for a lower power consumption
    - Transistor sizing with gm/ID in Python
    - Mismatch simulation with CACE
    - Extension for 3ECTS Seminar Integrierte Schaltungen
        - Layout
        - Tapeout
        - PCB Design (optional)

