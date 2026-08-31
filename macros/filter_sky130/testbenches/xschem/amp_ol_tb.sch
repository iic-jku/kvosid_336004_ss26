v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 440 -200 440 -170 {
lab=GND}
N 440 -300 440 -260 {
lab=VDD}
N 210 -590 210 -550 {
lab=vid}
N 210 -490 210 -420 {
lab=GND}
N 630 -660 720 -660 {
lab=vi_p}
N 630 -500 720 -500 {
lab=vi_n}
N 520 -200 520 -170 {
lab=GND}
N 920 -470 920 -440 {
lab=GND}
N 920 -710 920 -680 {
lab=VDD}
N 810 -230 810 -200 {
lab=GND}
N 720 -660 720 -620 {
lab=vi_p}
N 720 -620 780 -620 {
lab=vi_p}
N 720 -540 720 -500 {
lab=vi_n}
N 720 -540 780 -540 {
lab=vi_n}
N 1050 -620 1140 -620 {
lab=voutn}
N 1050 -540 1140 -540 {
lab=voutp}
N 520 -300 520 -260 {
lab=di_pon}
N 880 -710 880 -680 {
lab=di_pon}
N 1140 -440 1140 -420 {
lab=GND}
N 1140 -740 1140 -720 {
lab=GND}
N 1140 -540 1180 -540 {
lab=voutp}
N 1140 -540 1140 -500 {
lab=voutp}
N 1140 -620 1180 -620 {
lab=voutn}
N 1140 -660 1140 -620 {
lab=voutn}
N 740 -240 770 -240 {
lab=voutn}
N 740 -280 770 -280 {
lab=voutp}
N 810 -330 810 -290 {
lab=vout}
N 810 -330 860 -330 {
lab=vout}
N 340 -510 340 -420 {lab=GND}
N 450 -620 460 -620 {lab=vip}
N 460 -540 460 -500 {lab=vin}
N 450 -540 460 -540 {lab=vin}
N 210 -590 290 -590 {lab=vid}
N 460 -500 570 -500 {lab=vin}
N 460 -660 460 -620 {lab=vip}
N 460 -660 570 -660 {lab=vip}
N 450 -580 510 -580 {lab=vcmi}
N 590 -200 590 -170 {
lab=GND}
N 590 -300 590 -260 {lab=vcmi}
C {devices/vsource.sym} 440 -230 0 0 {name=V3 value=1.8
}
C {devices/gnd.sym} 440 -170 0 0 {name=l4 lab=GND}
C {devices/code_shown.sym} -890 -1580 0 0 {name=STIMULI
only_toplevel=false
value="
.options savecurrents

.save all
.control
set doAmpSim = 1

if $doAmpSim eq 1
	setplot const
	let f_min = 10
	let f_max = 1G
	let f_stop = 500k

	let Adc = 220
	let v_step_o = 0.9
	let v_step_i = -v_step_o/Adc

	let t_rf = 0.01u
	let t_step = 5u
	let t_delay = 0
	let t_per = 2*t_step

	let tstep = 0.001*t_step
	let tstop = 2*t_per
	let tstart = t_delay

	alter @VIN[DC] = 0.0
	alter @VIN[PULSE] = [ 0 $&v_step_i $&t_delay $&t_rf $&t_rf $&t_step $&t_per 0 ]

	ac dec 100 $&const.f_min $&const.f_max

	noise v(vout) vin dec 100 $&const.f_min $&const.f_max

	tran $&tstep $&tstop $&tstart

	setplot ac1
	let Atot = v(vout)/v(vid)		

	let Amag_ol_dB = vdb(Atot)
	let Aarg_ol = 180/PI*cphase(Atot)

	**let Amag_ol_dB_1 = vdb(A1)
	**let Aarg_ol_1 = 180/PI*cphase(A1)

	**let Amag_ol_dB_2 = vdb(A2)
	**let Aarg_ol_2 = 180/PI*cphase(A2)

	meas ac Adc_ol_dB max Amag_ol_dB
	let Amag_fc = Adc_ol_dB-3

	meas ac fc find frequency when Amag_ol_dB = Amag_fc
	meas ac fug_ol find frequency when Amag_ol_dB=0
	meas ac pm find Aarg_ol when frequency=fug_ol
	let pm = 180 + pm
	print pm

	let Adc_ol_lin = 10^(Adc_ol_dB/20)
	let err_gain = 1-Adc_ol_lin/(1+Adc_ol_lin)
	print err_gain*100

	plot Amag_ol_dB Aarg_ol ylabel 'Open Loop Magnitude, Phase'

	setplot noise1
	let acgain = onoise_spectrum/inoise_spectrum
	plot onoise_spectrum ylog xlog ylabel 'Output Noise'
	*plot acgain

	setplot noise2
	print onoise_total

	setplot tran2
	let vcmo = (v(voutp)+v(voutn))/2
	plot v(vin_p) v(vin_n) v(voutp) v(voutn) vcmo
end

reset
op


*rm /foss/designs/filter/dc.txt
*show >> /foss/designs/filter/dc.txt
remzerovec
write amp_ol_tb.raw
.endc"}
C {devices/vdd.sym} 440 -300 0 0 {name=l2 lab=VDD}
C {devices/vsource.sym} 210 -520 0 0 {name=VIN value="0 AC 1"
}
C {devices/lab_pin.sym} 210 -590 1 0 {name=l16 sig_type=std_logic lab=vid}
C {devices/gnd.sym} 210 -420 0 0 {name=l17 lab=GND}
C {devices/vsource.sym} 600 -660 3 0 {name=VIINP value=0
}
C {devices/vsource.sym} 600 -500 3 0 {name=VIINN value=0
}
C {devices/vsource.sym} 520 -230 0 0 {name=V4 value=1.8
}
C {devices/gnd.sym} 520 -170 0 0 {name=l33 lab=GND}
C {devices/lab_pin.sym} 520 -300 1 0 {name=p61 sig_type=std_logic lab=di_pon}
C {devices/title.sym} 200 -80 0 0 {name=l3 author="Michael Koefinger"}
C {devices/gnd.sym} 920 -440 0 0 {name=l5 lab=GND}
C {devices/vdd.sym} 920 -710 0 0 {name=l6 lab=VDD}
C {devices/lab_pin.sym} 660 -660 1 1 {name=p6 sig_type=std_logic lab=vi_p}
C {devices/lab_pin.sym} 660 -500 3 1 {name=p7 sig_type=std_logic lab=vi_n}
C {devices/vcvs.sym} 810 -260 0 0 {name=E7 value=1}
C {devices/gnd.sym} 810 -200 0 0 {name=l50 lab=GND}
C {devices/lab_pin.sym} 740 -280 0 0 {name=l53 sig_type=std_logic lab=voutp
}
C {devices/lab_pin.sym} 740 -240 2 1 {name=l54 sig_type=std_logic lab=voutn
}
C {devices/capa.sym} 1140 -470 0 0 {name=CL2
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {amp.sym} 740 -760 0 0 {name=xamp1}
C {devices/lab_pin.sym} 880 -710 1 0 {name=p1 sig_type=std_logic lab=di_pon}
C {devices/capa.sym} 1140 -690 2 0 {name=CL1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1140 -740 2 0 {name=l1 lab=GND}
C {devices/gnd.sym} 1140 -420 0 0 {name=l7 lab=GND}
C {devices/lab_pin.sym} 1180 -540 2 0 {name=l8 sig_type=std_logic lab=voutp
}
C {devices/lab_pin.sym} 1180 -620 0 1 {name=l9 sig_type=std_logic lab=voutn
}
C {devices/lab_pin.sym} 860 -330 0 1 {name=p2 sig_type=std_logic lab=vout}
C {code.sym} 30 -290 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {devices/launcher.sym} 80 -1430 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; file mkdir $netlist_dir; write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save; xschem simulate"
}
C {devices/launcher.sym} 80 -1310 0 0 {name=h3
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw ac"
}
C {devices/launcher.sym} 80 -1370 0 0 {name=h4
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/code_shown.sym} 20 -1520 0 0 {name=SAVE only_toplevel=true
format="tcleval( @value )"
value="
.include [file rootname [file tail [xschem get schname]]].save
"}
C {devices/lab_wire.sym} 510 -660 0 0 {name=l10 sig_type=std_logic lab=vip}
C {devices/lab_wire.sym} 510 -500 0 0 {name=l11 sig_type=std_logic lab=vin
}
C {devices/gnd.sym} 340 -420 0 0 {name=l12 lab=GND}
C {single2dm.sym} 370 -580 0 0 {name=x1 gain=1}
C {devices/lab_wire.sym} 510 -580 0 0 {name=l20 sig_type=std_logic lab=vcmi}
C {devices/vsource.sym} 590 -230 0 0 {name=V2 value=0.9
}
C {devices/gnd.sym} 590 -170 0 0 {name=l14 lab=GND}
C {devices/lab_wire.sym} 590 -300 1 0 {name=l13 sig_type=std_logic lab=vcmi}
