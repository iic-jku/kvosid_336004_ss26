v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Testbench for gain and noise under a blocker, hbac and hbnoise - LNA (VACASK)} 550 -1690 0 0 1 1 {}
T {Netlist type must be spectre, xschem's VACASK format. Port 1 is the 50 ohm antenna,
port 2 the 200 ohm load that stands in for the next stage.
lna_inv_sizes.inc comes from scripts/lna_inv_sizing.py, and make run-vacask puts schematic/xschem on VACASK's include path, so the bare name resolves.
RFMODE=0: the PSP RF network makes harmonic balance fail on a zero pivot, so HB runs the plain model.
hbnoise needs VACASK from hpretl/iic-osic-tools:2026.09 or later. vin1 is the blocker, vin2 the wanted tone.} 600 -1600 0 0 0.4 0.4 {}
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
parameters F0=2.44G FB=2.40G
parameters VSUP=1.2 RFMODE=0

include \\"sg13cmos5l_vacask_common.lib\\"
include \\"cornerMOSlv.lib\\" section=mos_tt
include \\"cornerRES.lib\\" section=res_typ
include \\"cornerCAP.lib\\" section=cap_typ
include \\"lna_inv_sizes.inc\\"

// netlist parameters are not visible inside control, so the analyses carry literals
control
  // stop at the first failure: vacask exits 1 and the postprocess never reads partial raws
  abort always
  options temp=27
  options rawfile=\\"binary\\"
  save full

  // bias and supply current
  analysis op1 op

  // no blocker: the wanted tone's gain and noise at F0, the reference for both sweeps.
  // Noise runs over F0 +- 30 MHz, the band scripts/lna_inv_hbcheck.py averages its transient noise over.
  analysis ac0 ac values=[2.44G]
  analysis nz0 noise out=[\\"vout\\"] in=\\"vin2\\" values=[2.41G, 2.42G, 2.43G, 2.44G, 2.45G, 2.46G, 2.47G]

  // Blocker at FB = 2.40 GHz, -50 to 0 dBm in 5 dB steps. The wanted tone at F0 is spur 1 of
  // the blocker plus 40 MHz, so both analyses run at the 40 MHz offset and read spur 1.
  // A sweep holds one analysis, hence two sweeps over the same levels.
  sweep pb instance=\\"vin1\\" parameter=\\"ampl\\" values=[2m, 3.557m, 6.325m, 11.25m, 20m, 35.57m, 63.25m, 112.5m, 200m, 355.7m, 632.5m]
    analysis bac hbac freq=[2.40G] nharm=7 outspur=[1] values=[40M]
  sweep pbn instance=\\"vin1\\" parameter=\\"ampl\\" values=[2m, 3.557m, 6.325m, 11.25m, 20m, 35.57m, 63.25m, 112.5m, 200m, 355.7m, 632.5m]
    analysis bnz hbnoise freq=[2.40G] nharm=7 in=\\"vin2\\" inspur=[1] outspur=[1] out=\\"vout\\" values=[10M, 20M, 30M, 40M, 50M, 60M, 70M]

  // plot once all analyses passed, vacask waits until the windows are closed.
  // Paths are relative to simulations/, where vacask starts. make runs it with -sp.
  postprocess(PYTHON, \\"../../../scripts/lna_inv_post.py\\", \\"--plot\\")

endc
"}
C {devices/launcher.sym} 1700 -1280 0 0 {name=h2
descr="netlist + simulate in VACASK"
tclcommand="
# the netlist type is what makes this a VACASK netlist, and the include path is set
# up by sim(spectre,0,cmd) in xschemrc, so plain Netlist/Simulate works too
xschem set netlist_type spectre
xschem save
xschem netlist
xschem simulate
"}
C {devices/launcher.sym} 1700 -1240 0 0 {name=h3
descr="replot without simulating (lna_inv_post.py)"
tclcommand="
# no braces here: xschem's schematic parser drops the record if the
# property value contains them
set macro [file normalize [file join [xschem get current_dirname] .. ..]]
exec >&@stdout python3 [file join $macro scripts lna_inv_post.py] --plot &
"}
C {devices/title-3.sym} 0 0 0 0 {name=l1 author="Michael Koefinger" rev=0.1 lock=true}
C {devices/vsource.sym} 300 -560 0 0 {name=vin1 value="type=\\"sine\\" sinedc=0 ampl=2m freq=FB dc=0 mag=0"}
C {devices/vsource.sym} 300 -460 0 0 {name=vin2 value="type=\\"sine\\" sinedc=0 ampl=0 freq=F0 dc=0 mag=1 spur=\{[1]\} smag=[1]"}
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
C {devices/lab_pin.sym} 680 -570 0 1 {name=l8 sig_type=std_logic lab=vout}
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
