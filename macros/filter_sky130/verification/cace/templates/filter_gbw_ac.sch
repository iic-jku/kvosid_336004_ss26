v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {CACE template - GBW sweep, biquad pole pair (verifies the appendix proof)} -40 -560 0 0 0.6 0.6 {}
C {devices/vsource.sym} 60 -300 0 0 {name=VIN value="dc 0 ac 1 sin(0 CACE\{vamp\} CACE\{fsig\} 0 0)"}
C {devices/lab_pin.sym} 60 -330 0 0 {name=l_vin_a sig_type=std_logic lab=vid}
C {devices/gnd.sym} 60 -270 0 0 {name=l_vin_g lab=GND}
C {single2dm.sym} 220 -330 0 0 {name=x2 gain=1}
C {devices/lab_pin.sym} 140 -340 0 0 {name=l_s2d_i sig_type=std_logic lab=vid}
C {devices/gnd.sym} 190 -260 0 0 {name=l_s2d_g lab=GND}
C {devices/lab_pin.sym} 300 -370 0 0 {name=l_s2d_p sig_type=std_logic lab=sp}
C {devices/lab_pin.sym} 300 -330 0 0 {name=l_s2d_c sig_type=std_logic lab=vcm}
C {devices/lab_pin.sym} 300 -290 0 0 {name=l_s2d_n sig_type=std_logic lab=sn}
C {devices/vsource.sym} 60 -160 0 0 {name=VCM value=CACE\{vcm\}}
C {devices/lab_pin.sym} 60 -190 0 0 {name=l_vcm_a sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 60 -130 0 0 {name=l_vcm_g lab=GND}
C {filter.sym} 560 -330 0 0 {name=xdut}
C {devices/lab_pin.sym} 560 -420 0 0 {name=l_dut_vdd sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 560 -240 0 0 {name=l_dut_vss sig_type=std_logic lab=GND}
C {devices/vsource.sym} 200 -160 0 0 {name=VSUP value=CACE\{vdd\}}
C {devices/lab_pin.sym} 200 -190 0 0 {name=l_sup_a sig_type=std_logic lab=VDD}
C {devices/gnd.sym} 200 -130 0 0 {name=l_sup_g lab=GND}
C {devices/lab_pin.sym} 450 -370 0 0 {name=l_dut_sp_-110 sig_type=std_logic lab=sp}
C {devices/lab_pin.sym} 450 -330 0 0 {name=l_dut_sn_-110 sig_type=std_logic lab=sn}
C {devices/lab_pin.sym} 450 -290 0 0 {name=l_dut_vcm_-110 sig_type=std_logic lab=vcm}
C {devices/lab_pin.sym} 670 -370 0 0 {name=l_dut_vop_110 sig_type=std_logic lab=vop}
C {devices/lab_pin.sym} 670 -290 0 0 {name=l_dut_von_110 sig_type=std_logic lab=von}
C {devices/res.sym} 820 -330 0 0 {name=RL
value=CACE\{rload\}
footprint=1206
device=resistor
m=1
}
C {devices/lab_pin.sym} 820 -360 0 0 {name=l_rl_a sig_type=std_logic lab=vop}
C {devices/lab_pin.sym} 820 -300 0 0 {name=l_rl_b sig_type=std_logic lab=von}
C {devices/capa.sym} 920 -330 0 0 {name=CL
m=1
value=CACE\{cload\}
footprint=1206
device="ceramic capacitor"
}
C {devices/lab_pin.sym} 920 -360 0 0 {name=l_cl_a sig_type=std_logic lab=vop}
C {devices/lab_pin.sym} 920 -300 0 0 {name=l_cl_b sig_type=std_logic lab=von}
C {devices/vcvs.sym} 1060 -330 0 0 {name=EOUT value=1}
C {devices/lab_pin.sym} 1060 -360 0 0 {name=l_eo_o sig_type=std_logic lab=vout}
C {devices/gnd.sym} 1060 -300 0 0 {name=l_eo_g lab=GND}
C {devices/lab_pin.sym} 1020 -350 0 0 {name=l_eo_p sig_type=std_logic lab=vop}
C {devices/lab_pin.sym} 1020 -310 0 0 {name=l_eo_n sig_type=std_logic lab=von}
C {devices/code_shown.sym} 1300 -560 0 0 {name=MODEL only_toplevel=true
value="
.include CACE\{DUT_path\}
.temp CACE\{temp\}
.lib cornerMOSlv.lib mos_CACE\{corner_mos\}
.lib cornerMOShv.lib mos_CACE\{corner_mos\}
.lib cornerRES.lib res_CACE\{corner_r\}
.param gm_ota=CACE\{gm\} ro_ota=CACE\{ro\} co_ota=CACE\{co\}
.param rp_ota=CACE\{rp\} cp_ota=CACE\{cp\} i0_ota=CACE\{i0\}
.param vcmo_ota=CACE\{vcm\}
"}
C {devices/code_shown.sym} 1300 -300 0 0 {name=NGSPICE
simulator=ngspice
only_toplevel=false
value="
.options savecurrents reltol=1e-6 abstol=1e-15
.control
save all
option numdgt=8

* ---- MFB half-circuit values, taken from filter.sch ------------------------
* C1 bridges the two differential summing nodes, so the half circuit sees 2*C1
let r1  = 10.82e3
let r2  = 108.23e3
let r3  = 4.62e3
let c1h = 2*25.30e-12
let c2  = 1e-12
let g0  = r2/r1
let wn0 = 1/sqrt(r2*r3*c1h*c2)
let q0  = wn0*c1h/(1/r1+1/r2+1/r3)
let fn0 = wn0/(2*pi)

* ---- one-pole OTA: f_ug = GM/(2*pi*CO) -------------------------------------
let fug = CACE\{gm\}/(2*pi*CACE\{co\})

* ---- appendix, general form: dwn/wn = -(Q*fn/fug)*(1/beta0 + R2/R3)/2 ------
let dev_pred = -(q0*fn0/fug)*((1+g0)+r2/r3)/2
let fn_pred  = fn0*(1+dev_pred)

ac dec 2000 1e3 1e8
setplot ac1
let hbq    = (v(xdut.oo_p)-v(xdut.oo_n))/v(vid)
let hn     = -hbq
let reh    = real(hn)
let mag_db = 20*log10(mag(hbq))
settype decibel mag_db
* complete filter response (biquad + buffered RC), for the appendix figure
let htot    = (v(vop)-v(von))/v(vid)
let mag_tot = 20*log10(mag(htot))
settype decibel mag_tot

* f_n is where the biquad response is in quadrature, i.e. where its real part
* crosses zero. That is exact for a 2nd-order pole pair and independent of Q.
meas ac f_n    when reh=0
meas ac dc_db  find mag_db when frequency=1e4
meas ac pk_db  max mag_db from=1e5 to=1e7

* Q from the peaking of a 2nd-order low pass: 4Q^4 - 4r^2 Q^2 + r^2 = 0
let r    = 10^((pk_db-dc_db)/20)
let q_bq = sqrt((r^2+r*sqrt(r^2-1))/2)

wrdata CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.curve mag_db mag_tot

setplot const
let m_fn    = ac1.f_n
let m_q     = ac1.q_bq
let m_adc   = ac1.dc_db
let m_fug   = fug
let m_devm  = 100*(ac1.f_n/fn0-1)
let m_devp  = 100*dev_pred
let m_err   = 100*abs(ac1.f_n-fn_pred)/ac1.f_n

echo $&m_fn $&m_q $&m_adc $&m_fug $&m_devm $&m_devp $&m_err > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc
"}
