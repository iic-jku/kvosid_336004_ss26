v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {SS26 reference AAF: 3rd-order MFB low-pass, fully differential} -40 -560 0 0 0.5 0.5 {}
T {f_pass = 1 MHz, A_pass = 20 dB, Butterworth. Values from python/filter_design_ss26.py.} -40 -520 0 0 0.35 0.35 {}
T {C1 and C3 are DIFFERENTIAL bridging caps (half the single-ended value).} -40 -490 0 0 0.35 0.35 {}
T {R4/C3 is designed WITH the 560k || 5p ADC load; its 2.78 % dc loss is} -40 -460 0 0 0.35 0.35 {}
T {compensated by R2/R1 = 10.29 instead of 10.} -40 -430 0 0 0.35 0.35 {}
T {The OTA macro parameters come from .param gm_ota/ro_ota/co_ota/rp_ota/cp_ota/} -40 -400 0 0 0.35 0.35 {}
T {vcmo_ota/i0_ota, which the testbench or the CACE template must define.} -40 -370 0 0 0.35 0.35 {}
T {Output stage: unity-gain ACTIVE first-order section (R4 in, R6||C3 feedback,} -40 -340 0 0 0.35 0.35 {}
T {R6 = R4 -> gain 1, pole = 1/(2*pi*R6*C3) = 1 MHz). The ADC is driven by the} -40 -310 0 0 0.35 0.35 {}
T {OTA2 output, so there is no resistive divider against the external load.} -40 -280 0 0 0.35 0.35 {}
T {VDD/VSS are declared but unused: ota_fd_2pole is behavioural. They exist so a} -40 -250 0 0 0.35 0.35 {}
T {transistor-level OTA can be dropped in without changing the symbol or the TB.} -40 -310 0 0 0.35 0.35 {}
C {devices/ipin.sym} -40 -360 0 0 {name=p_vip lab=vip}
C {devices/ipin.sym} -40 -320 0 0 {name=p_vin lab=vin}
C {devices/opin.sym} -40 -280 0 0 {name=p_vop lab=vop}
C {devices/opin.sym} -40 -240 0 0 {name=p_von lab=von}
C {devices/ipin.sym} -40 -200 0 0 {name=p_vcm lab=vcm}
C {devices/iopin.sym} -40 -160 0 0 {name=p_VDD lab=VDD}
C {devices/iopin.sym} -40 -120 0 0 {name=p_VSS lab=VSS}
C {devices/res.sym} 60 -260 0 0 {name=R1
value=10.82k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 60 -290 0 0 {name=l_R1_a sig_type=std_logic lab=vin}
C {devices/lab_pin.sym} 60 -230 0 0 {name=l_R1_b sig_type=std_logic lab=n2}
C {devices/res.sym} 170 -260 0 0 {name=R11
value=10.82k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 170 -290 0 0 {name=l_R11_a sig_type=std_logic lab=vip}
C {devices/lab_pin.sym} 170 -230 0 0 {name=l_R11_b sig_type=std_logic lab=n1}
C {devices/res.sym} 280 -260 0 0 {name=R2
value=108.23k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 280 -290 0 0 {name=l_R2_a sig_type=std_logic lab=oo_p}
C {devices/lab_pin.sym} 280 -230 0 0 {name=l_R2_b sig_type=std_logic lab=n2}
C {devices/res.sym} 390 -260 0 0 {name=R21
value=108.23k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 390 -290 0 0 {name=l_R21_a sig_type=std_logic lab=n1}
C {devices/lab_pin.sym} 390 -230 0 0 {name=l_R21_b sig_type=std_logic lab=oo_n}
C {devices/res.sym} 500 -260 0 0 {name=R3
value=4.62k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 500 -290 0 0 {name=l_R3_a sig_type=std_logic lab=n2}
C {devices/lab_pin.sym} 500 -230 0 0 {name=l_R3_b sig_type=std_logic lab=oi_n}
C {devices/res.sym} 610 -260 0 0 {name=R31
value=4.62k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 610 -290 0 0 {name=l_R31_a sig_type=std_logic lab=n1}
C {devices/lab_pin.sym} 610 -230 0 0 {name=l_R31_b sig_type=std_logic lab=oi_p}
C {devices/capa.sym} 60 -40 0 0 {name=C1
m=1
value=25.30p
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 60 -70 0 0 {name=l_C1_a sig_type=std_logic lab=n2}
C {devices/lab_pin.sym} 60 -10 0 0 {name=l_C1_b sig_type=std_logic lab=n1}
C {devices/capa.sym} 170 -40 0 0 {name=C2
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 170 -70 0 0 {name=l_C2_a sig_type=std_logic lab=oo_p}
C {devices/lab_pin.sym} 170 -10 0 0 {name=l_C2_b sig_type=std_logic lab=oi_n}
C {devices/capa.sym} 280 -40 0 0 {name=C21
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 280 -70 0 0 {name=l_C21_a sig_type=std_logic lab=oi_p}
C {devices/lab_pin.sym} 280 -10 0 0 {name=l_C21_b sig_type=std_logic lab=oo_n}
C {devices/res.sym} 390 -40 0 0 {name=R4
value=159k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 390 -70 0 0 {name=l_R4_a sig_type=std_logic lab=oo_n}
C {devices/lab_pin.sym} 390 -10 0 0 {name=l_R4_b sig_type=std_logic lab=si_n}
C {devices/res.sym} 500 -40 0 0 {name=R41
value=159k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 500 -70 0 0 {name=l_R41_a sig_type=std_logic lab=oo_p}
C {devices/lab_pin.sym} 500 -10 0 0 {name=l_R41_b sig_type=std_logic lab=si_p}
C {devices/capa.sym} 610 -40 0 0 {name=C3
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 610 -70 0 0 {name=l_C3_a sig_type=std_logic lab=vop}
C {devices/lab_pin.sym} 610 -10 0 0 {name=l_C3_b sig_type=std_logic lab=si_n}
C {devices/capa.sym} 720 -40 0 0 {name=C31
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 720 -70 0 0 {name=l_C31_a sig_type=std_logic lab=si_p}
C {devices/lab_pin.sym} 720 -10 0 0 {name=l_C31_b sig_type=std_logic lab=von}
C {devices/res.sym} 830 -40 0 0 {name=R6
value=159k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 830 -70 0 0 {name=l_R6_a sig_type=std_logic lab=vop}
C {devices/lab_pin.sym} 830 -10 0 0 {name=l_R6_b sig_type=std_logic lab=si_n}
C {devices/res.sym} 940 -40 0 0 {name=R61
value=159k
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 940 -70 0 0 {name=l_R61_a sig_type=std_logic lab=si_p}
C {devices/lab_pin.sym} 940 -10 0 0 {name=l_R61_b sig_type=std_logic lab=von}
C {ota_fd_2pole.sym} 1120 -200 0 0 {name=xota2 GM=gm_ota RO=ro_ota CO=co_ota RP=rp_ota CP=cp_ota VCMO=vcmo_ota I0=i0_ota}
C {devices/lab_pin.sym} 1120 -150 0 0 {name=l_o2_VN sig_type=std_logic lab=si_n}
C {devices/lab_pin.sym} 1340 -120 0 0 {name=l_o2_IP sig_type=std_logic lab=vop}
C {devices/lab_pin.sym} 1340 -80 0 0 {name=l_o2_IN sig_type=std_logic lab=von}
C {devices/lab_pin.sym} 1120 -50 0 0 {name=l_o2_VP sig_type=std_logic lab=si_p}
C {devices/lab_pin.sym} 1120 -100 0 0 {name=l_o2_VCMI sig_type=std_logic lab=vcm}
C {ota_fd_2pole.sym} 780 -200 0 0 {name=xota1 GM=gm_ota RO=ro_ota CO=co_ota RP=rp_ota CP=cp_ota VCMO=vcmo_ota I0=i0_ota}
C {devices/lab_pin.sym} 780 -150 0 0 {name=l_ota_VN sig_type=std_logic lab=oi_n}
C {devices/lab_pin.sym} 1000 -120 0 0 {name=l_ota_IP sig_type=std_logic lab=oo_p}
C {devices/lab_pin.sym} 1000 -80 0 0 {name=l_ota_IN sig_type=std_logic lab=oo_n}
C {devices/lab_pin.sym} 780 -50 0 0 {name=l_ota_VP sig_type=std_logic lab=oi_p}
C {devices/lab_pin.sym} 780 -100 0 0 {name=l_ota_VCMI sig_type=std_logic lab=vcm}
