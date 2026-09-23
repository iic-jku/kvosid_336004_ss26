v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 530 -770 530 -650 {lab=vdd}
N 210 -770 530 -770 {lab=vdd}
N 230 -620 490 -620 {lab=vin}
N 530 -560 530 -540 {lab=vout}
N 530 -480 530 -390 {lab=vss}
N 440 -390 530 -390 {lab=vss}
N 530 -560 640 -560 {lab=vout}
N 530 -570 530 -560 {lab=vout}
N 530 -620 560 -620 {lab=vdd}
N 530 -770 560 -770 {lab=vdd}
N 560 -770 560 -620 {lab=vdd}
N 440 -570 440 -530 {lab=vout}
N 440 -570 530 -570 {lab=vout}
N 530 -590 530 -570 {lab=vout}
N 440 -470 440 -390 {lab=vss}
N 250 -390 440 -390 {lab=vss}
C {title.sym} 170 -50 0 0 {name=l1 author="M. Koefinger"}
C {ipin.sym} 230 -620 0 0 {name=p1 lab=vin}
C {opin.sym} 640 -560 0 0 {name=p2 lab=vout}
C {iopin.sym} 210 -770 0 1 {name=p3 lab=vdd}
C {iopin.sym} 250 -390 0 1 {name=p4 lab=vss}
C {sg13cmos5l_pr/sg13_lv_pmos.sym} 510 -620 0 0 {name=M1
l=\{l_m1\}
w=\{w_m1\}
ng=1
m=1
mm_ok=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13cmos5l_pr/rhigh.sym} 530 -510 0 0 {name=R1
w=0.5e-6
l=0.96e-6
model=rhigh
body=vss
spiceprefix=X
b=0
 m=1
  mm_ok=1
value="expr_eng(  ( 1.6e-4 / @w + 1360.0 * ( (@b + 1)* @l + ( 1.081*( @w - 0.04e-6 ) + 0.18e-6 )*@b ) / ( @w - 0.04e-6 ) ) / @m  )"
spice_ignore=true}
C {res.sym} 440 -500 0 0 {name=R2
value=\{rload_cs\}
footprint=1206
device=resistor
m=1
}
C {sg13g2_pr/annotate_fet_params.sym} 670 -740 0 0 {name=annot1 ref=M1}
