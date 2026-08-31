v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {CACE template - AC and noise of the AAF} -40 -560 0 0 0.6 0.6 {}
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
option numdgt=6

let v_fs   = CACE\{vfs\}
let n_bits = CACE\{nbits\}
let a_pass = CACE\{apass\}
let v_lsb  = v_fs/2^n_bits
let v_qn   = v_lsb/sqrt(12)
let v_orms = v_fs/(2*sqrt(2))

ac dec 200 10 100e6
setplot ac1
let A       = v(vout)/v(vid)
let Amag_dB = vdb(A)
settype decibel Amag_dB
meas ac a_pass_db find Amag_dB when frequency=10e3
let a_3db = a_pass_db-3
meas ac f_pass find frequency when Amag_dB=a_3db
meas ac a_stop_db find Amag_dB when frequency=CACE\{fstop\}
meas ac a_peak_db max Amag_dB from=1e3 to=1e6
let att_db  = a_pass_db-a_stop_db
let peak_db = a_peak_db-a_pass_db
let eps_g   = abs(1-10^(a_pass_db/20)/const.a_pass)

noise v(vout) VIN dec 100 CACE\{fnmin\} CACE\{fnmax\}
setplot noise2
let v_on   = onoise_total
let snr_db = 10*log10(const.v_orms^2/(const.v_qn^2+v_on^2))

setplot const
let m_apass = ac1.a_pass_db
let m_fpass = ac1.f_pass
let m_att   = ac1.att_db
let m_peak  = ac1.peak_db
let m_epsg  = ac1.eps_g
let m_von   = noise2.v_on
let m_snr   = noise2.snr_db

echo $&m_apass $&m_fpass $&m_att $&m_peak $&m_epsg $&m_von $&m_snr > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc
"}
