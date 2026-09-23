v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
T {Template Testbench for corner characterization - inverter LNA (CACE, ngspice)} 470 -1720 0 0 1.2 1.2 {}
T {Small signal only: op current, S11 from the ac input impedance, transconductance
into the 200 ohm mixer-side load, noise figure at 2.44 GHz with that load noiseless.
The pair self-biases through RF, so there is no bias source to sweep and no second set.
Every CACE\{...\} is a datasheet condition, the sizes among them written by lna_inv_sizing.py.} 470 -1680 0 0 0.4 0.4 {}
N 300 -590 370 -590 {lab=vsrc}
N 300 -530 300 -500 {lab=GND}
N 430 -590 500 -590 {lab=vin}
N 580 -670 580 -630 {lab=VDD}
N 580 -510 580 -480 {lab=GND}
N 660 -570 720 -570 {lab=vout}
N 720 -510 720 -480 {lab=GND}
N 1000 -1080 1000 -1040 {lab=VDD}
N 1000 -980 1000 -940 {lab=GND}
C {devices/code_shown.sym} 40 -1300 0 0 {name=NGSPICE
simulator=ngspice
only_toplevel=false
value="
.include CACE\{DUT_path\}
.temp CACE\{temp\}
.param WN=CACE\{WN\} LNCH=CACE\{LNCH\} NGN=CACE\{NGN\} WP=CACE\{WP\} LPCH=CACE\{LPCH\} NGP=CACE\{NGP\}
.param RF=CACE\{RF\} CPAD=CACE\{CPAD\} LSH=CACE\{LSH\} RLSH=CACE\{RLSH\} CD=CACE\{CD\}
.param CC=CACE\{CC\} CBLK=CACE\{CBLK\}
.param RFMODE=1
.options savecurrents reltol=1e-4 abstol=1e-15 gmin=1e-15
* no klu: ngspice-47 refuses a noise analysis under it
* Flag unsafe operating conditions (exceeds models' specified limits)
.option warn=1
.control

save all

* Operating point: supply current. Base units throughout, CACE scales by the datasheet unit
op
let idd_a = -vsup#branch

* Input impedance from the source's branch current (the resistor's ac current is not saved), transconductance at the load
ac lin 201 2.0G 3.0G
let iin = -vin1#branch
let zin = v(vin)/iin
let s11mag = db((zin-50)/(zin+50))
meas ac s11_db find s11mag at=2.44G
let vom = mag(v(vout))
meas ac vo find vom at=2.44G
let gm_s = vo/200/0.5

* Noise figure at the band centre: input-referred noise against the source's own 4kT*50
noise v(vout) vin1 lin 1 2.44G 2.44G
setplot noise1
let tk = CACE\{temp\} + 273.15
* inoise_spectrum is an amplitude density, V per root Hz, hence the square
let nf_db = 10*log10(inoise_spectrum[0]^2/(4*1.380649e-23*tk*50))
let idd_out = op1.idd_a
let s11_out = ac1.s11_db
let gm_out = ac1.gm_s

echo $&idd_out $&s11_out $&gm_out $&nf_db > CACE\{simpath\}/CACE\{filename\}_CACE\{N\}.data

.endc
"}
C {devices/code_shown.sym} 1220 -1250 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_CACE\{corner_mos\}
.lib cornerRES.lib res_CACE\{corner_r\}
.lib cornerCAP.lib cap_typ
"}
C {title-3.sym} 0 0 0 0 {name=l1 author="Michael Koefinger" rev=0.1 lock=true}
C {devices/vsource.sym} 300 -560 0 0 {name=vin1 value="dc 0 ac 1"}
C {devices/gnd.sym} 300 -500 0 0 {name=l2 lab=GND}
C {devices/res.sym} 400 -590 3 0 {name=rs
value=50
footprint=1206
device=resistor
m=1}
C {devices/lab_pin.sym} 300 -590 0 0 {name=l3 sig_type=std_logic lab=vsrc}
C {devices/lab_pin.sym} 500 -590 0 1 {name=l4 sig_type=std_logic lab=vin}
C {lna_inv.sym} 580 -570 0 0 {name=x1}
C {vdd.sym} 580 -670 0 0 {name=l7 lab=VDD}
C {devices/gnd.sym} 580 -480 0 0 {name=l8 lab=GND}
C {devices/lab_pin.sym} 720 -570 0 1 {name=l9 sig_type=std_logic lab=vout}
C {devices/res.sym} 720 -540 0 0 {name=rl
value="200 noisy=0"
footprint=1206
device="mixer-side load, noiseless"
m=1}
C {devices/gnd.sym} 720 -480 0 0 {name=l10 lab=GND}
C {vdd.sym} 1000 -1080 0 0 {name=l11 lab=VDD}
C {devices/vsource.sym} 1000 -1010 0 0 {name=vsup value=CACE\{vdd\}}
C {devices/gnd.sym} 1000 -940 0 0 {name=l12 lab=GND}
