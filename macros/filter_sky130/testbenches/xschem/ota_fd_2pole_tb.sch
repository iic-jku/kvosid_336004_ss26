v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {OTA Macro Model:
A0 = Gm*Ro = 4mS*2MOhm/2 = 4000
GBW=fug = Gm/(Co+CL)/2/PI = 4mS/(1pF+5pF)/2/PI = 106MHz
BW = fug/A0 = 26.5kHz} 840 -180 0 1 0.3 0.3 {}
N 1120 -210 1120 -190 {
lab=vcmi}
N 1120 -130 1120 -110 {
lab=GND}
N 290 -490 290 -450 {
lab=vid}
N 290 -390 290 -320 {
lab=GND}
N 660 -530 740 -530 {
lab=vipp}
N 660 -430 740 -430 {
lab=vinn}
N 1030 -220 1030 -200 {
lab=vout}
N 1030 -140 1030 -110 {
lab=GND}
N 990 -610 990 -590 {
lab=GND}
N 990 -360 990 -340 {
lab=GND}
N 990 -500 1030 -500 {
lab=#net1}
N 990 -460 1030 -460 {
lab=#net2}
N 990 -460 990 -420 {
lab=#net2}
N 990 -530 990 -500 {
lab=#net1}
N 1090 -500 1190 -500 {
lab=voutn1}
N 1090 -460 1190 -460 {
lab=voutp1}
N 950 -150 990 -150 {
lab=voutn1}
N 950 -190 990 -190 {
lab=voutp1}
N 960 -460 990 -460 {
lab=#net2}
N 960 -500 990 -500 {
lab=#net1}
N 390 -410 390 -320 {lab=GND}
N 510 -530 510 -520 {lab=vip}
N 500 -520 510 -520 {lab=vip}
N 510 -440 510 -430 {lab=vin}
N 500 -440 510 -440 {lab=vin}
N 510 -430 600 -430 {lab=vin}
N 500 -480 740 -480 {lab=vcmi}
N 510 -530 600 -530 {lab=vip}
N 290 -490 340 -490 {lab=vid}
C {devices/vsource.sym} 1120 -160 0 0 {name=V2 value=0.9
}
C {devices/vsource.sym} 290 -420 0 0 {name=VIN value="0 AC 1"
}
C {devices/lab_wire.sym} 560 -530 0 0 {name=l1 sig_type=std_logic lab=vip}
C {devices/lab_wire.sym} 560 -430 0 0 {name=l1 sig_type=std_logic lab=vin
}
C {devices/launcher.sym} 130 -120 0 0 {name=h1
descr="Annotate OP"
tclcommand="set show_hidden_texts 1; xschem annotate_op"}
C {devices/lab_wire.sym} 290 -490 1 0 {name=l1 sig_type=std_logic lab=vid}
C {devices/gnd.sym} 290 -320 0 0 {name=l1 lab=GND}
C {devices/code.sym} 40 -260 0 0 {name=STIMULI
only_toplevel=false
value="
.options savecurrents
.options method=gear reltol=.005 
.options sparse
.control
save all

let f_sig = 100
let f_min = 10
let f_max = 1000Meg
let f_stop = 5Meg
let tper_sig = 1/f_sig
let tfr_sig = tper_sig/2
let Adc = 4000
let v_step_o = 0.9
let v_step_i = v_step_o/Adc

let t_rf = 0.1u
let t_step = 50u
let t_delay = 0
let t_per = 2*t_step

let tstep = 0.1*t_rf
let tstop = 2*t_per
let tstart = t_delay

alter @VIN[PULSE] = [ 0 $&v_step_i $&t_delay $&t_rf $&t_rf $&t_step $&t_per 0 ]

set wr_singlescale
set wr_vecnames
option numdgt=3


** Main Simulations
	op
	ac dec 100 $&const.f_min $&const.f_max
	tran $&tstep $&tstop $&tstart
		
	setplot ac1
	let A = v(vout)/v(vid)

	let Amag_dB = vdb(A)
	settype decibel Amag_dB
	let Aarg = 180/PI*cphase(A)

	let fdc = const.f_min+1
	meas ac Adc find Amag_dB when frequency = fdc
	let Amag_fc = Adc-3
	meas ac fc find frequency when Amag_dB = Amag_fc
	meas ac Amax max Amag_dB
	meas ac fug find frequency when Amag_dB=0
	
	let Adc_lin = 10^(Adc/20)
	let GBW = Adc_lin*fc
	print Adc_lin
	print GBW

	plot Amag_dB Aarg ylabel 'Magnitude, Phase'

	setplot tran1
	let vid = v(vid)
	let iop = viop#branch
	let ion = vion#branch
	let vcmo = (voutp1+voutn1)/2

	*plot iop ion
	plot vid vout vcmo
	plot v(vip) v(vin) v(voutp1) v(voutn1) vcmo


alter @VIN[DC] = 0
op

remzerovec
write ota_fd_2pole_tb.raw
.endc"}
C {devices/gnd.sym} 1120 -110 0 0 {name=l14 lab=GND}
C {devices/gnd.sym} 390 -320 0 0 {name=l15 lab=GND}
C {devices/title.sym} 160 -40 0 0 {name=l22 author="Michael Koefinger"}
C {devices/lab_wire.sym} 710 -530 0 0 {name=p3 sig_type=std_logic lab=vipp}
C {devices/lab_wire.sym} 710 -430 0 0 {name=p4 sig_type=std_logic lab=vinn}
C {devices/vsource.sym} 630 -530 3 0 {name=VIINP value=0
}
C {devices/vsource.sym} 630 -430 3 1 {name=VIINN value=0
}
C {devices/lab_wire.sym} 1120 -460 2 0 {name=l10 sig_type=std_logic lab=voutp1
}
C {devices/lab_wire.sym} 1120 -500 0 1 {name=l11 sig_type=std_logic lab=voutn1
}
C {devices/lab_pin.sym} 1030 -220 0 1 {name=l12 sig_type=std_logic lab=vout}
C {devices/vcvs.sym} 1030 -170 0 0 {name=E5 value=1}
C {devices/gnd.sym} 1030 -110 0 0 {name=l13 lab=GND}
C {devices/vsource.sym} 1060 -500 3 0 {name=VIOP value=0
}
C {devices/vsource.sym} 1060 -460 3 1 {name=VION value=0
}
C {devices/capa.sym} 990 -390 0 0 {name=C4
m=1
value=5p
footprint=1206
device="ceramic capacitor"}
C {devices/capa.sym} 990 -560 0 0 {name=C6
m=1
value=5p
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 990 -340 0 0 {name=l26 lab=GND}
C {devices/gnd.sym} 990 -610 2 0 {name=l27 lab=GND}
C {devices/lab_pin.sym} 950 -150 2 1 {name=l2 sig_type=std_logic lab=voutn1
}
C {devices/lab_pin.sym} 950 -190 0 0 {name=l4 sig_type=std_logic lab=voutp1
}
C {ota_fd_2pole.sym} 740 -580 0 0 {name=xota1 GM=4m RO=2Meg CO=1p RP=0 CP=0.1p VCMO=0.9 I0=100u}
C {single2dm.sym} 420 -480 0 0 {name=x1 gain=1}
C {devices/lab_wire.sym} 560 -480 0 0 {name=l5 sig_type=std_logic lab=vcmi}
C {devices/lab_wire.sym} 1120 -200 1 0 {name=l6 sig_type=std_logic lab=vcmi}
