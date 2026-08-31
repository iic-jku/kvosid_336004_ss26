v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {CACE template - distortion of the AAF} -40 -560 0 0 0.6 0.6 {}
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
m=1}
C {devices/lab_pin.sym} 820 -360 0 0 {name=l_rl_a sig_type=std_logic lab=vop}
C {devices/lab_pin.sym} 820 -300 0 0 {name=l_rl_b sig_type=std_logic lab=von}
C {devices/capa.sym} 920 -330 0 0 {name=CL
m=1
value=CACE\{cload\}
footprint=1206
device="ceramic capacitor"}
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
** transient tolerances: the tanh source of ota_fd_2pole will not converge with the
** AC-grade settings used by filter_tb_ac.sch
.options savecurrents reltol=1e-3 abstol=1e-12 vntol=1e-6 chgtol=1e-14 trtol=7
.control
save all
option numdgt=6

let t_sig  = 1/CACE\{fsig\}
let t_set  = 8*t_sig
let t_stop = t_set+16*t_sig
let t_step = t_sig/2000

** $& expands a value, it does not evaluate arithmetic, so precompute every argument
tran $&t_step $&t_stop $&t_set
linearize v(vout)

** the fourier command leaves thd11 (in percent) and fourier11 in the current plot
fourier CACE\{fsig\} v(vout)
** stay in the linearized transient plot: thd11 and thd_db live there, and
** switching to const would put them out of scope
let thd_db = 20*log10(thd11/100)
echo $&thd_db > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data
.endc
"}
