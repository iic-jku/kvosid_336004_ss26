v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 1640 -700 2440 -300 {flags=graph
y1=13
y2=180
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=-1
x2=10
divx=5
subdivx=8
xlabmag=1.0
ylabmag=1.0
node="\\"OL Phase; ph(vout)\\"
aol_arg"
color="4 10"
dataset=-1
unitx=1
logx=1
logy=0
linewidth_mult=4}
B 2 1640 -1120 2440 -720 {flags=graph
y1=-27
y2=32
ypos1=0
ypos2=2
divy=5
subdivy=4
unity=1
x1=-1
x2=10
divx=5
subdivx=8
xlabmag=1.0
ylabmag=1.0
node="\\"OL Magnitude; aol_db"
color=4
dataset=-1
unitx=1
logx=1
logy=0
linewidth_mult=4}
T {Common-Source Amp} 860 -1700 0 0 1 1 {}
N 1430 -1300 1430 -1260 {lab=VDD}
N 1430 -1200 1430 -1160 {lab=GND}
N 890 -1060 890 -1040 {lab=vin}
N 830 -1060 890 -1060 {lab=vin}
N 890 -1060 970 -1060 {lab=vin}
N 1430 -1060 1510 -1060 {lab=vout}
N 890 -980 890 -960 {lab=GND}
N 1330 -1060 1330 -1040 {lab=vout}
N 1270 -1060 1330 -1060 {lab=vout}
N 1430 -1060 1430 -1040 {lab=vout}
N 1330 -1060 1430 -1060 {lab=vout}
N 1330 -980 1330 -960 {lab=GND}
N 1430 -980 1430 -960 {lab=GND}
N 1120 -1140 1120 -1110 {lab=VDD}
N 1120 -1010 1120 -960 {lab=GND}
C {devices/code_shown.sym} 10 -1350 0 0 {name=NGSPICE
only_toplevel=true 
value="
.param VDD=\{\{ vdd \}\}
.param Vcm=VDD/2
.temp \{\{ temp \}\}
.param Cload= \{\{ cload \}\}
.param w_m1=\{\{ w_m1 \}\}
.param l_m1=\{\{ l_m1 \}\}
.param rload_cs= \{\{ rload \}\}
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15
.control

save all
* Operating Point Analysis
op
let vout = v(vout)
let id_1 = @n.xamp1.xm1.nsg13_lv_pmos[ids]
let gm_1 = @n.xamp1.xm1.nsg13_lv_pmos[gm]

ac dec 101 100 1G
let Aol = v(vout)/v(vin)		
let Aol_dB = vdb(Aol)
let Aol_arg = 180/PI*cphase(Aol)

quit
.endc
"
spice_ignore=true}
C {devices/launcher.sym} 1700 -1280 0 0 {name=h2
descr="Simulate" 
tclcommand="xschem save; xschem netlist; file mkdir $netlist_dir; write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save; xschem simulate"
}
C {title-3.sym} 0 0 0 0 {name=l2 author="M. Koefinger" rev=1.0 lock=true}
C {devices/launcher.sym} 1700 -1160 0 0 {name=h1
descr="Load waves" 
tclcommand="xschem raw_read $netlist_dir/[file rootname [file tail [xschem get current_name]]].raw ac"
}
C {devices/launcher.sym} 1700 -1220 0 0 {name=h3
descr="Annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/vsource.sym} 1430 -1230 0 0 {name=VDD value=\{VDD\}}
C {devices/gnd.sym} 1430 -1160 0 0 {name=l3 lab=GND}
C {vdd.sym} 1430 -1300 0 0 {name=l7 lab=VDD}
C {devices/lab_pin.sym} 1510 -1060 0 1 {name=l12 sig_type=std_logic lab=vout}
C {devices/vsource.sym} 890 -1010 0 1 {name=vin spice_ignore=False value="dc \{Vcm\} ac 1"
}
C {devices/lab_pin.sym} 830 -1060 0 0 {name=l22 sig_type=std_logic lab=vin}
C {devices/gnd.sym} 890 -960 0 0 {name=l26 lab=GND}
C {devices/gnd.sym} 1120 -960 0 0 {name=l1 lab=GND}
C {vdd.sym} 1120 -1140 0 0 {name=l4 lab=VDD}
C {devices/code_shown.sym} 10 -1470 0 0 {name=SAVE only_toplevel=true
format="tcleval( @value )"
value="
.include [file dirname [xschem get schname]]/simulations/[file rootname [file tail [xschem get schname]]].save
"
spice_ignore=true}
C {capa.sym} 1330 -1010 0 0 {name=C1
m=1
value=\{cload\}
footprint=1206
device="ceramic capacitor"
}
C {res.sym} 1430 -1010 0 0 {name=R1
value=\{Rload\}
footprint=1206
device=resistor
m=1
spice_ignore=true}
C {devices/gnd.sym} 1330 -960 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} 1430 -960 0 0 {name=l6 lab=GND}
C {amp_cs.sym} 1120 -1060 0 0 {name=xamp1}
C {code_shown.sym} 950 -690 0 0 {name=SWEEP_SETTINGS
only_toplevel=false
value="
**nr_workers=50
**sort_results_index=0
**results_plot_contour_index=
**results_plot_logx_index=
**results_plot_logy_index=

**parameter_sweep_begin
**w_m1=Auto:1u:10:10u
**rload_cs=Auto:3k:5:10k
**parameter_sweep_end

**results_plot_begin
**vout
**id
**gm
**results_plot_end
"
}
C {launcher.sym} 760 -285 0 0 {name=h4
descr=SimulatePARALLEL
tclcommand="
# Setup the default simulation commands if not already set up
# for example by already launched simulations.
set_sim_defaults
puts $sim(spice,1,cmd) 

# Change the Xyce command. In the spice category there are currently
# 5 commands (0, 1, 2, 3, 4). Command 3 is the Xyce batch
# you can get the number by querying $sim(spice,n)
set sim(spice,1,cmd) \{ngspice  \\"$N\\" -a\}

# change the simulator to be used (Xyce)
set sim(spice,default) 0

# Create FET and BIP .save file
file mkdir $netlist_dir
write_data [save_params] $netlist_dir/[file rootname [file tail [xschem get current_name]]].save

# run netlist and simulation
xschem netlist
exec >&@stdout python3 /foss/pdks/ihp-sg13g2/libs.tech/xschem/sg13g2_tests/ngspice_parallel_sweep.py [file tail [xschem get current_name]]
"}
C {devices/code_shown.sym} 40 -740 0 0 {name=SWEEP_SIM
only_toplevel=true 
value="
.param VDD=1.5
.param Vcm=VDD/2
.temp 27
.param cload=10p
.param Rload=1k
.param w_m1=20u
.param l_m1=0.5u
.param rload_cs=3.4k
.options savecurrents klu method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15
.control

save all


* Operating Point Analysis
op
let vout = v(vout)
let id  = @n.xamp1.xm1.nsg13_lv_pmos[ids]
let gm  = @n.xamp1.xm1.nsg13_lv_pmos[gm]

echo results_sweep_begin
print vout
print id
print gm
echo results_sweep_end


remzerovec
write @schname\\\\.raw

*quit
.endc
"
}
C {devices/code_shown.sym} 810 -810 0 0 {name=SAVE1 only_toplevel=true
format="tcleval( @value )"
value="
.include [file rootname [file tail [xschem get schname]]].save
"
}
C {simulator_commands_shown.sym} 420 -800 0 0 {
name=Libs_Ngspice
simulator=ngspice
only_toplevel=false
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
"
      }
C {devices/code_shown.sym} 740 -1320 0 0 {name=MODEL1 only_toplevel=true
format="tcleval( @value )"
value="
.lib cornerMOSlv.lib mos_\{\{ corner_mos \}\}
.lib cornerMOShv.lib mos_\{\{ corner_mos \}\}
.lib cornerRES.lib res_typ
.lib cornerDIO.lib dio_tt
"
spice_ignore=true}
