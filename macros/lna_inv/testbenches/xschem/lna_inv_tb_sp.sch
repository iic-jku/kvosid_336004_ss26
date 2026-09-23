v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Testbench for S-parameter, AC and noise analysis - LNA (VACASK)} 600 -1730 0 0 1 1 {}
T {Netlist type must be spectre, xschem's VACASK format. Port 1 is the 50 ohm antenna,
port 2 the RF-frequency load the mixer presents, RBB per side through the switches.
lna_inv_sizes.inc comes from scripts/lna_inv_sizing.py; make run-vacask puts schematic/xschem on VACASK's include path, so the bare name resolves.} 600 -1690 0 0 0.4 0.4 {}
N 300 -590 370 -590 {lab=vsrc}
N 300 -530 300 -490 {lab=n_src}
N 300 -430 300 -400 {lab=GND}
N 430 -590 500 -590 {lab=vin}
N 440 -450 440 -420 {lab=GND}
N 580 -670 580 -630 {lab=VDD}
N 580 -510 580 -480 {lab=GND}
N 660 -570 720 -570 {lab=vout}
N 780 -570 840 -570 {lab=n_op}
N 840 -510 840 -480 {lab=GND}
N 1000 -1080 1000 -1040 {lab=VDD}
N 1000 -980 1000 -940 {lab=GND}
C {devices/code_shown.sym} 40 -1300 0 0 {name=VACASK only_toplevel=true
value="
parameters F0=2.44G F1=2.441G
parameters VSUP=1.2 RFMODE=1

include \\"sg13cmos5l_vacask_common.lib\\"
include \\"cornerMOSlv.lib\\" section=mos_tt
include \\"cornerRES.lib\\" section=res_typ
include \\"cornerCAP.lib\\" section=cap_typ
include \\"lna_inv_sizes.inc\\"

// netlist parameters are not visible inside control, so the analyses carry literals
control
  options temp=27
  options rawfile=\\"binary\\"
  save full

  // bias and supply current
  analysis op1 op

  // S11 at the antenna, S21 into the mixer-side load
  analysis sp1 acsp ports=[\\"vin1\\", \\"rs\\", \\"vop\\", \\"rl\\"] from=2.0G to=3.0G mode=\\"lin\\" points=201
  // the whole blocker range of the level plan, 30 MHz to 12.75 GHz: what the LNA rejects off band.
  // 3000 points per decade is 1.9 MHz of grid at the band centre, so the nearest sample to a
  // 10 MHz offset is that offset and not F0 itself: at 60 per decade the grid is 93 MHz there
  // and every offset the plan reads below 100 MHz came back as exactly 0 dB by construction.
  analysis sp2 acsp ports=[\\"vin1\\", \\"rs\\", \\"vop\\", \\"rl\\"] from=30M to=13G mode=\\"dec\\" points=3000

  // transconductance: output current in rl against the source, vin1 has mag=1
  analysis ac1 ac from=2.0G to=3.0G mode=\\"lin\\" points=201

  // noise figure: onoise over the source resistor's share n(rs)
  analysis n1 noise out=[\\"vout\\"] in=\\"vin1\\" from=2.3G to=2.6G mode=\\"lin\\" points=31

endc
"}
C {devices/launcher.sym} 1700 -1280 0 0 {name=h2
descr="netlist + simulate in VACASK"
tclcommand="
# the netlist type is what makes this a VACASK netlist; the include path is set
# up by sim(spectre,0,cmd) in xschemrc, so plain Netlist/Simulate works too
xschem set netlist_type spectre
xschem save
xschem netlist
xschem simulate
"}
C {devices/launcher.sym} 1700 -1240 0 0 {name=h3
descr="evaluate the raws (lna_measure.py)"
tclcommand="
# no braces here: xschem's schematic parser drops the record if the
# property value contains them
set macro [file normalize [file join [xschem get current_dirname] .. ..]]
exec >&@stdout python3 [file join $macro scripts lna_measure.py] --macro $macro --plot &
"
C {devices/title-3.sym} 0 0 0 0 {name=l1 author="Michael Koefinger" rev=0.1 lock=true}
C {devices/vsource.sym} 300 -560 0 0 {name=vin1 value="type=\\"sine\\" sinedc=0 ampl=2m freq=F0 dc=0 mag=1"}
C {devices/vsource.sym} 300 -460 0 0 {name=vin2 value="type=\\"sine\\" sinedc=0 ampl=0 freq=F1 dc=0 mag=0"}
C {devices/gnd.sym} 300 -400 0 0 {name=l2 lab=GND}
C {devices/res.sym} 400 -590 3 0 {name=rs
value=50
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 300 -590 0 0 {name=l3 sig_type=std_logic lab=vsrc}
C {devices/lab_pin.sym} 500 -590 0 1 {name=l4 sig_type=std_logic lab=vin}
C {devices/gnd.sym} 440 -420 0 0 {name=l5 lab=GND}
C {lna_inv.sym} 580 -570 0 0 {name=x1}
C {vdd.sym} 580 -670 0 0 {name=l6 lab=VDD}
C {devices/gnd.sym} 580 -480 0 0 {name=l7 lab=GND}
C {devices/lab_pin.sym} 720 -570 0 1 {name=l8 sig_type=std_logic lab=vout}
C {devices/res.sym} 750 -570 3 0 {name=rl
value=200
footprint=1206
device=resistor
m=1}
C {devices/vsource.sym} 840 -540 0 0 {name=vop value="dc=0 mag=0"}
C {devices/gnd.sym} 840 -480 0 0 {name=l9 lab=GND}
C {vdd.sym} 1000 -1080 0 0 {name=l10 lab=VDD}
C {devices/vsource.sym} 1000 -1010 0 0 {name=vsup value="dc=VSUP"}
C {devices/gnd.sym} 1000 -940 0 0 {name=l11 lab=GND}
C {devices/lab_wire.sym} 300 -530 0 0 {name=l20 sig_type=std_logic lab=n_src}
C {devices/lab_wire.sym} 780 -570 0 0 {name=l22 sig_type=std_logic lab=n_op}
