v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Testbench for harmonic balance analysis - LNA (VACASK)} 550 -1690 0 0 1 1 {}
T {Netlist type must be spectre, xschem's VACASK format. Port 1 is the 50 ohm antenna,
port 2 the 200 ohm load that stands in for the next stage.
lna_inv_sizes.inc comes from scripts/lna_inv_sizing.py, and make run-vacask puts schematic/xschem on VACASK's include path, so the bare name resolves.
RFMODE=0: the PSP RF network makes harmonic balance fail on a zero pivot, so HB runs the plain model.} 600 -1600 0 0 0.4 0.4 {}
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

  // single tone, input power -50 to 0 dBm in 5 dB steps: gain compression
  sweep pin instance=\\"vin1\\" parameter=\\"ampl\\" values=[2m, 3.557m, 6.325m, 11.25m, 20m, 35.57m, 63.25m, 112.5m, 200m, 355.7m, 632.5m]
    analysis hb1 hb freq=[2.44G] nharm=7

  // Two tones 1 MHz apart at -40 and -30 dBm per tone: IM3 at 2*F0-F1.
  // The second fundamental is the 0.5 MHz offset, not the second tone, so the
  // grid is half the tone spacing: F0 is (1,0), F1 is (1,2), IM3 is (1,-2), and
  // (1,+-1) carry no product. Those empty bins read -182 to -197 dBV against
  // IM3 at -127 dBV, which is what shows the product is real and not numerical
  // floor. Costs nothing: 46 points instead of 25, same tone and IM3 levels.
  alter instance(\\"vin1\\") ampl=6.325m
  alter instance(\\"vin2\\") ampl=6.325m
  analysis hb2 hb freq=[2.44G, 0.5M] truncate=\\"box\\" nharm=[3, 6]
  alter instance(\\"vin1\\") ampl=20m
  alter instance(\\"vin2\\") ampl=20m
  analysis hb3 hb freq=[2.44G, 0.5M] truncate=\\"box\\" nharm=[3, 6]

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
