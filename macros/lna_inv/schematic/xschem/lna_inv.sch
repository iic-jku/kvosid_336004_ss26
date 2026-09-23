v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Inverter LNA with resistive feedback, current output into the passive mixer, no coil on chip} 90 -1350 0 0 1 1 {}
T {Every value is a parameter from lna_inv_sizes.inc, written by scripts/lna_inv_sizing.py.
MN and MP share gate and drain, so both transconductances work on one current, and RF biases the pair
at its own trip point while setting the input impedance against the load. The antenna pad is vin, shared
with the transmitter, and the off-chip shunt coil LSH resonates what hangs on it.
RFMODE is set by the bench: 1 for the PSP RF network, 0 for harmonic balance.} 90 -1290 0 0 0.5 0.5 {}
N 100 -640 200 -640 {lab=vin}
N 200 -640 300 -640 {lab=vin}
N 300 -640 370 -640 {lab=vin}
N 200 -640 200 -610 {lab=vin}
N 300 -640 300 -610 {lab=vin}
N 300 -550 300 -530 {lab=n_sh}
N 430 -640 460 -640 {lab=vg}
N 460 -640 500 -640 {lab=vg}
N 500 -740 500 -640 {lab=vg}
N 460 -640 460 -470 {lab=vg}
N 460 -470 680 -470 {lab=vg}
N 680 -610 680 -470 {lab=vg}
N 540 -690 540 -670 {lab=vd}
N 540 -690 680 -690 {lab=vd}
N 680 -690 680 -670 {lab=vd}
N 680 -690 710 -690 {lab=vd}
N 710 -690 710 -650 {lab=vd}
N 770 -690 840 -690 {lab=vout}
N 540 -610 540 -500 {lab=VSS}
N 540 -640 620 -640 {lab=VSS}
N 540 -860 540 -770 {lab=#net1}
N 540 -740 620 -740 {lab=VDD}
N 540 -710 540 -690 {lab=vd}
C {devices/title-3.sym} 0 0 0 0 {name=l1 author="Michael Koefinger" rev=0.1 lock=true}
C {devices/ipin.sym} 100 -640 0 0 {name=p1 lab=vin}
C {devices/iopin.sym} 840 -690 0 0 {name=p3 lab=vout}
C {devices/iopin.sym} 540 -860 3 0 {name=p4 lab=VDD}
C {devices/iopin.sym} 540 -500 1 0 {name=p5 lab=VSS}
C {devices/capa.sym} 200 -580 0 0 {name=Cpad
m=1
value=CPAD
footprint=1206
device="the shared antenna pad: pad, ESD, the PA's off-state output and the detune switch, assumed"}
C {devices/lab_pin.sym} 200 -550 0 0 {name=l2 sig_type=std_logic lab=VSS}
C {devices/ind.sym} 300 -580 0 0 {name=Lsh
m=1
value=LSH
footprint=1206
device="shunt coil off chip, resonates the pad for TX and RX"}
C {devices/res.sym} 300 -500 0 0 {name=Rlsh
value=RLSH
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 300 -470 0 0 {name=l3 sig_type=std_logic lab=VSS}
C {devices/capa.sym} 400 -640 3 0 {name=Cblk
m=1
value=CBLK
footprint=1206
device="dc block"}
C {sg13_lv_rf_nmos.sym} 520 -640 0 0 {name=MN
l=LNCH
w=WN
ng=NGN
m=1
rfmode=RFMODE
mm_ok=1
model=sg13_lv_nmos
lvs_model=rfnmos
spiceprefix=X
}
C {sg13_lv_rf_pmos.sym} 520 -740 0 0 {name=MP
l=LPCH
w=WP
ng=NGP
m=1
rfmode=RFMODE
mm_ok=1
model=sg13_lv_pmos
lvs_model=rfpmos
spiceprefix=X
}
C {devices/lab_pin.sym} 620 -640 0 1 {name=l4 sig_type=std_logic lab=VSS}
C {devices/lab_pin.sym} 620 -740 0 1 {name=l5 sig_type=std_logic lab=VDD}
C {devices/res.sym} 680 -640 0 0 {name=Rf
value=RF
footprint=1206
device="feedback, sets the match and the bias"
m=1}
C {devices/capa.sym} 740 -690 3 0 {name=Cc
m=1
value=CC
footprint=1206
device="dc block"}
C {devices/lab_wire.sym} 460 -640 0 0 {name=l10 sig_type=std_logic lab=vg}
C {devices/lab_wire.sym} 600 -690 0 0 {name=l11 sig_type=std_logic lab=vd}
C {devices/capa.sym} 710 -620 0 0 {name=Cd
m=1
value=CD
footprint=1206
device="mixer-side parasitic at the drain, 0 in the bench, moved by the robustness sweep"}
C {devices/lab_pin.sym} 710 -590 0 0 {name=l13 sig_type=std_logic lab=VSS}
C {devices/lab_wire.sym} 300 -540 0 0 {name=l12 sig_type=std_logic lab=n_sh}
