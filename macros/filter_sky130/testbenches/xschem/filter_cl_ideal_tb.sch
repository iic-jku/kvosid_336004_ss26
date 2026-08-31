v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 1000 -240 1000 -220 {
lab=vout1}
N 80 -580 80 -540 {
lab=vid}
N 80 -580 200 -580 {
lab=vid}
N 80 -480 80 -410 {
lab=GND}
N 570 -610 610 -610 {
lab=vinn}
N 570 -530 610 -530 {
lab=vipp}
N 610 -620 610 -610 {
lab=vinn}
N 610 -620 630 -620 {
lab=vinn}
N 610 -530 610 -520 {
lab=vipp}
N 610 -520 630 -520 {
lab=vipp}
N 740 -750 740 -720 {
lab=voutp1}
N 880 -750 880 -720 {
lab=voutp1}
N 840 -620 880 -620 {
lab=vi_ota_n}
N 880 -630 880 -620 {
lab=vi_ota_n}
N 840 -520 880 -520 {
lab=vi_ota_p}
N 880 -510 880 -480 {
lab=vi_ota_p}
N 740 -420 740 -390 {
lab=voutn1}
N 880 -390 1330 -390 {
lab=voutn1}
N 880 -420 880 -390 {
lab=voutn1}
N 880 -750 1330 -750 {
lab=voutp1}
N 1540 -610 1620 -610 {
lab=voutn2}
N 1540 -530 1620 -530 {
lab=voutp2}
N 1620 -660 1620 -610 {
lab=voutn2}
N 1620 -530 1620 -480 {
lab=voutp2}
N 930 -210 960 -210 {
lab=voutp1}
N 930 -170 960 -170 {
lab=voutn1}
N 1230 -240 1230 -220 {
lab=vout}
N 1160 -210 1190 -210 {
lab=voutp2}
N 1160 -170 1190 -170 {
lab=voutn2}
N 460 -530 510 -530 {
lab=vip}
N 460 -610 510 -610 {
lab=vin}
N 1000 -160 1000 -130 {
lab=GND}
N 1230 -160 1230 -130 {
lab=GND}
N 880 -630 890 -620 {
lab=vi_ota_n}
N 890 -620 970 -620 {
lab=vi_ota_n}
N 880 -510 890 -520 {
lab=vi_ota_p}
N 890 -520 970 -520 {
lab=vi_ota_p}
N 740 -510 740 -480 {
lab=#net1}
N 740 -610 740 -600 {
lab=#net2}
N 690 -620 730 -620 {
lab=#net2}
N 730 -620 740 -630 {
lab=#net2}
N 740 -610 750 -620 {
lab=#net2}
N 750 -620 780 -620 {
lab=#net2}
N 690 -520 730 -520 {
lab=#net1}
N 730 -520 740 -530 {
lab=#net1}
N 740 -510 750 -520 {
lab=#net1}
N 750 -520 780 -520 {
lab=#net1}
N 1330 -750 1330 -610 {
lab=voutp1}
N 1300 -610 1330 -610 {
lab=voutp1}
N 1330 -530 1330 -390 {
lab=voutn1}
N 1300 -530 1330 -530 {
lab=voutn1}
N 440 -150 440 -120 {
lab=GND}
N 440 -250 440 -210 {
lab=VDD}
N 1330 -610 1360 -610 {
lab=voutp1}
N 1360 -610 1390 -530 {
lab=voutp1}
N 1390 -530 1440 -530 {
lab=voutp1}
N 1330 -530 1360 -530 {
lab=voutn1}
N 1360 -530 1390 -610 {
lab=voutn1}
N 1390 -610 1440 -610 {
lab=voutn1}
N 1540 -610 1540 -600 {
lab=voutn2}
N 1540 -540 1540 -530 {
lab=voutp2}
N 740 -750 880 -750 {
lab=voutp1}
N 740 -390 880 -390 {
lab=voutn1}
N 880 -660 880 -630 {
lab=vi_ota_n}
N 880 -520 880 -510 {
lab=vi_ota_p}
N 740 -660 740 -630 {
lab=#net2}
N 740 -630 740 -610 {
lab=#net2}
N 740 -540 740 -530 {
lab=#net1}
N 740 -530 740 -510 {
lab=#net1}
N 1500 -610 1540 -610 {
lab=voutn2}
N 1500 -530 1540 -530 {
lab=voutp2}
N 250 -500 250 -410 {lab=GND}
N 360 -610 370 -610 {lab=vip}
N 370 -530 370 -490 {lab=vin}
N 360 -530 370 -530 {lab=vin}
N 370 -490 440 -490 {lab=vin}
N 370 -650 370 -610 {lab=vip}
N 370 -650 440 -650 {lab=vip}
N 360 -570 420 -570 {lab=vcmi}
N 590 -150 590 -120 {
lab=GND}
N 590 -250 590 -210 {lab=vcmi}
N 1190 -610 1190 -590 {lab=vo_ota_p}
N 1190 -610 1240 -610 {lab=vo_ota_p}
N 1190 -550 1190 -530 {lab=vo_ota_n}
N 1190 -530 1240 -530 {lab=vo_ota_n}
C {devices/vsource.sym} 80 -510 0 0 {name=VIN value="0 AC 1"
}
C {devices/lab_pin.sym} 80 -580 1 0 {name=l1 sig_type=std_logic lab=vid}
C {devices/lab_pin.sym} 1000 -240 0 1 {name=l1 sig_type=std_logic lab=vout1}
C {devices/gnd.sym} 80 -410 0 0 {name=l1 lab=GND}
C {devices/code_shown.sym} -820 -1740 0 0 {name=STIMULI
only_toplevel=false
value="
.options savecurrents
.options method=gear reltol=.005 
.options sparse
.control
save all

let f_min = 10
let f_max = 100Meg
let f_stop = 9Meg
let f_nmin = 100
let f_nmax = 5Meg

let n_bits = 8
let Adc = 10
let v_fs = 1.0
let v_lsb = v_fs/2^n_bits
let v_qn = v_lsb/sqrt(12)
let err_gain_spec = v_lsb/v_fs
let vo_n_max = 113e-6

let v_step_o = v_fs
let v_step_i = v_step_o/Adc

let t_rf = 0.1u
let t_step = 50u
let t_delay = 0
let t_per = 2*t_step

let tstep = 0.1*t_rf
let tstop = 2*t_per
let tstart = t_delay

*alter @VIN[SIN] = [ 0 0.01 $&f_sig 0 0 0 ]
alter @VIN[DC] = 0.0

set wr_singlescale
set wr_vecnames
option numdgt=3

set opSimOnly = 0


** Main Simulations
if $opSimOnly eq 0
	op
	ac dec 100 $&const.f_min $&const.f_max
	*set sqrnoise
	noise v(vout) VIN dec 100 $&const.f_min $&const.f_max 1
	noise v(vout) VIN dec 10 $&const.f_nmin $&const.f_nmax
	alter @VIN[PULSE] = [ 0 $&v_step_i $&t_delay $&t_rf $&t_rf $&t_step $&t_per 0 ]
	** Check power on by ramping Vdd, tie di_pon to VDD net!
	*alter @V1[PULSE] = [ 0 1.8 0 10u $&t_rf 0 0 0 ]
	tran $&tstep $&tstop $&tstart
		
	setplot ac1
	let A1 = v(vout1)/v(vid)
	let A2 = v(vout)/v(vid)

	let Amag_dB = vdb(A2)
	settype decibel Amag_dB
	let Aarg = 180/PI*cphase(A2)

	let fdc = const.f_min+1
	meas ac Adc_ol_dB find Amag_dB when frequency = fdc
	let Amag_fc = Adc_ol_dB-3
	meas ac fc find frequency when Amag_dB = Amag_fc
	meas ac Amin min_at Amag_dB from=const.f_min to=fc
	meas ac Amax max Amag_dB
	meas ac Astop find Amag_dB when frequency = const.f_stop
	let att_db = Adc_ol_dB-Astop
	
	meas ac fug find frequency when Amag_dB=0
	let err_gain_act = 1-10^(Adc_ol_dB/20)/Adc
	let Adc_ol_min = (1+Adc)*(1-err_gain_spec)/err_gain_spec
	let Adc_ol_min_dB = vdb(Adc_ol_min)
	print err_gain_act*100
	print Adc_ol_min_dB
	print att_db
	wrdata ../plot_simulations/data/filter_cl_ideal_tb_ac.txt Amag_dB Aarg
	plot Amag_dB Aarg ylabel 'Magnitude, Phase'
	
	setplot noise3
	wrdata ../plot_simulations/data/filter_cl_ideal_tb_noise.txt onoise_spectrum

	setplot noise4
	let p_noise_q = const.v_qn^2
	let p_noise_o = onoise_total^2
	let p_sig_o = (v_step_o/(2*sqrt(2)))^2
	let snr = p_sig_o/(p_noise_o+p_noise_q)
	let snr_dB = 10*log10(snr)
	print snr_dB
	
	setplot tran4
	let vid = v(vid)
	let iop = viop#branch
	let ion = vion#branch
	let vcmo = (voutp1+voutn1)/2

	*plot iop ion

	*plot vid vout1 vout vcmo
	*plot v(vip) v(vin) v(voutp1) v(voutn1) vcmo
end

alter @VIN[DC] = 0
op

remzerovec
write filter_cl_ideal_tb.raw
.endc"}
C {devices/lab_pin.sym} 1620 -480 3 0 {name=l16 sig_type=std_logic lab=voutp2
}
C {devices/lab_pin.sym} 1620 -660 3 1 {name=l17 sig_type=std_logic lab=voutn2
}
C {devices/vcvs.sym} 1000 -190 0 0 {name=E4 value=1}
C {devices/gnd.sym} 1000 -130 0 0 {name=l18 lab=GND}
C {devices/title.sym} 160 -40 0 0 {name=l22 author="Michael Koefinger"}
C {devices/lab_pin.sym} 590 -530 1 1 {name=p3 sig_type=std_logic lab=vipp}
C {devices/lab_pin.sym} 590 -610 1 0 {name=p4 sig_type=std_logic lab=vinn}
C {devices/vsource.sym} 540 -610 3 0 {name=VIINP value=0
}
C {devices/vsource.sym} 540 -530 3 0 {name=VIINN value=0
}
C {devices/res.sym} 660 -620 3 0 {name=R1
value=10.82k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 930 -170 2 1 {name=l5 sig_type=std_logic lab=voutn1}
C {devices/lab_pin.sym} 930 -210 0 0 {name=l6 sig_type=std_logic lab=voutp1
}
C {devices/res.sym} 740 -690 0 0 {name=R2
value=108.23k
footprint=1206
device=resistor
m=1}
C {devices/res.sym} 810 -620 3 0 {name=R3
value=4.62k
footprint=1206
device=resistor
m=1}
C {devices/capa.sym} 740 -570 0 0 {name=C1
m=1
value=25.30p
footprint=1206
device="ceramic capacitor"}
C {devices/capa.sym} 1540 -570 0 0 {name=C3
m=1
value=0.5p
footprint=1206
device="ceramic capacitor"}
C {devices/res.sym} 660 -520 3 0 {name=R11
value=10.82k
footprint=1206
device=resistor
m=1}
C {devices/res.sym} 740 -450 0 0 {name=R21
value=108.23k
footprint=1206
device=resistor
m=1}
C {devices/res.sym} 810 -520 3 0 {name=R31
value=4.62k
footprint=1206
device=resistor
m=1}
C {devices/capa.sym} 880 -450 0 0 {name=C21
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/res.sym} 1470 -610 3 0 {name=R4
value=159k
footprint=1206
device=resistor
m=1}
C {devices/res.sym} 1470 -530 3 0 {name=R41
value=159k
footprint=1206
device=resistor
m=1}
C {devices/capa.sym} 880 -690 0 0 {name=C2
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 1330 -680 2 0 {name=l10 sig_type=std_logic lab=voutp1
}
C {devices/lab_pin.sym} 1330 -460 0 1 {name=l11 sig_type=std_logic lab=voutn1
}
C {devices/lab_pin.sym} 1230 -240 0 1 {name=l12 sig_type=std_logic lab=vout}
C {devices/vcvs.sym} 1230 -190 0 0 {name=E5 value=1}
C {devices/gnd.sym} 1230 -130 0 0 {name=l13 lab=GND}
C {devices/lab_pin.sym} 1160 -170 2 1 {name=l19 sig_type=std_logic lab=voutn2
}
C {devices/lab_pin.sym} 1160 -210 0 0 {name=l23 sig_type=std_logic lab=voutp2
}
C {devices/vsource.sym} 1270 -610 3 0 {name=VIOP value=0
}
C {devices/vsource.sym} 1270 -530 3 1 {name=VION value=0
}
C {devices/vsource.sym} 440 -180 0 0 {name=V1 value=1.5
}
C {devices/gnd.sym} 440 -120 0 0 {name=l4 lab=GND}
C {devices/vdd.sym} 440 -250 0 0 {name=l2 lab=VDD}
C {devices/lab_pin.sym} 940 -520 3 0 {name=p7 sig_type=std_logic lab=vi_ota_p}
C {devices/lab_pin.sym} 940 -620 3 1 {name=p8 sig_type=std_logic lab=vi_ota_n}
C {devices/lab_pin.sym} 1210 -530 3 0 {name=p9 sig_type=std_logic lab=vo_ota_n}
C {devices/lab_pin.sym} 1210 -610 1 0 {name=p10 sig_type=std_logic lab=vo_ota_p}
C {devices/lab_wire.sym} 420 -650 0 0 {name=l3 sig_type=std_logic lab=vip}
C {devices/lab_wire.sym} 420 -490 0 0 {name=l14 sig_type=std_logic lab=vin
}
C {devices/gnd.sym} 250 -410 0 0 {name=l15 lab=GND}
C {single2dm.sym} 280 -570 0 0 {name=x2 gain=1}
C {devices/lab_wire.sym} 420 -570 0 0 {name=l9 sig_type=std_logic lab=vcmi}
C {devices/lab_wire.sym} 490 -530 0 0 {name=l20 sig_type=std_logic lab=vip}
C {devices/lab_wire.sym} 490 -610 0 0 {name=l21 sig_type=std_logic lab=vin
}
C {devices/vsource.sym} 590 -180 0 0 {name=V2 value=0.75
}
C {devices/gnd.sym} 590 -120 0 0 {name=l24 lab=GND}
C {devices/lab_wire.sym} 590 -250 1 0 {name=l31 sig_type=std_logic lab=vcmi}
C {devices/launcher.sym} 130 -790 0 0 {name=h2
descr="Annotate OP"
tclcommand="set show_hidden_texts 1; xschem annotate_op"}
C {ota_fd_2pole.sym} 970 -670 0 0 {name=xota1 GM=25.1m RO=2Meg CO=12.1p RP=0 CP=0.1p VCMO=0.75 I0=100u}
C {devices/lab_wire.sym} 970 -570 0 0 {name=l25 sig_type=std_logic lab=vcmi}
