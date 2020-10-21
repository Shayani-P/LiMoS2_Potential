# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 20:45:51 2020

@author: Shayani
"""

from pymatgen.io.vasp.outputs import *
import numpy as np
import json
import ase
import ase.io
from ase import Atoms
import os

p=os.listdir(r'D:\Lab\SNAP\EOS_1T_Top_Mo\SNAP')

for i in p:
    os.chdir("D:\Lab\SNAP\EOS_1T_Top_Mo\SNAP\{}".format(i))
    #Get forces
    outcar = Outcar("OUTCAR")
    
    all_forces = outcar.read_table_pattern(
        header_pattern=r"\sPOSITION\s+TOTAL-FORCE \(eV/Angst\)\n\s-+",
        row_pattern=r"\s+[+-]?\d+\.\d+\s+[+-]?\d+\.\d+\s+[+-]?\d+\.\d+\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)",
        footer_pattern=r"\s--+",
        postprocess=lambda x: float(x),
        last_one_only=False
    )
    j_force=all_forces[-1]
    
    #Get charges
    all_charges = outcar.read_table_pattern(
        #header_pattern=r"\s+Hirshfeld\s+charges\:",
        header_pattern=r"------------------------------",
        row_pattern=r"\s+\d+\s+\w+\s+([\s-]?\d+\.\d+)",
        footer_pattern=r"\s+Atomic\s+reference\s+data\s+used\s+in\s+the\s+T-S\s+method\s+for\s+vdW\s+correction\:",
        postprocess=lambda x: float(x),
        last_one_only=False
    )
    
    j_charges=all_charges[-1]
    print(np.shape(j_charges))
    
    #Get coordinates of atoms
    atoms=ase.io.read('CONTCAR', format='vasp')
    positions=atoms.positions
    j_positions=np.ndarray.tolist(positions)
    
    #Get list of different atoms in order of coordinates
    j_atoms=Atoms.get_chemical_symbols(atoms)
    
    #Get total number of atoms
    tot_atoms=len(positions)
    
    #Get lattice parameters
    lattice=atoms.cell
    #j_lattice=np.ndarray.tolist(lattice)
    
    #Get total energy
    for line in reversed(open("OUTCAR").readlines()):
        if line.__contains__('free  energy   TOTEN'):
            e=line.split()
            j_energy=e[4]
    
    #Get stresses
    c=[]
    for line in reversed(open("OUTCAR").readlines()):
        if line.__contains__('in kB'):
            c=line.split()
            c.pop(0)
            c.pop(0)
            x=[float(c[0]),float(c[3]),float(c[5])]
            y=[float(c[3]),float(c[1]),float(c[4])]
            z=[float(c[5]),float(c[4]),float(c[2])]
            j_stress_mat=[x,y,z]
            break
    
    #Write to json file
    with open('MoS2_1T_{}.json'.format(i), 'w') as f:
        f.write('#Comment Line \n')
        f.write('{"Dataset": {')
        f.write('"Data": [')
        f.write('{')
        f.write('"NumAtoms": ' + str(tot_atoms) + ',')
        #json.dumps(tot_atoms, f)
    
        # Now, write the lattice vectors
        f.write('"Lattice": ')
        b='['
        for i in range(0,3):
            b+='['+','.join(map(str,lattice[i]))+']'
            if i<2: b+=','
        f.write(b+']')
        #json.dump(j_lattice, f)
    
        # Now, the Total energy
        b=', "Energy": ' + str(j_energy) + ','
        f.write(b)
    
        # Now, the stress tensor
        f.write(' "Stress": ')
        json.dump(j_stress_mat, f)
    
        # Now the atom types
        f.write(', "AtomTypes": ')
        json.dump(j_atoms, f)
    
        # Now the positions
        f.write(', "Positions": ')
        json.dump(j_positions, f)
    
        # Now, the forces
        f.write(', "Forces": ')
        json.dump(j_force, f)
    
        # Now, the charges
        f.write(', "Charges": ')
        json.dump(j_charges, f)
    
        f.write('}')
        f.write('],')
        f.write('"Label": "Example containing 1 configurations, each with ' + str(tot_atoms) + ' atoms",')
        f.write('"LatticeStyle": "angstrom",')
        f.write('"EnergyStyle": "electronvolt",')
        f.write('"StressStyle": "kB",')
        f.write('"AtomTypeStyle": "chemicalsymbol",')
        f.write('"PositionsStyle": "angstrom",')
        f.write('"ForcesStyle": "electronvoltperangstrom",')
        f.write('"ChargeStyle": "partial"')
    
        f.write('}')
        f.write('}')
    
    os.chdir("D:\Lab\SNAP\EOS_1T_Top_Mo\SNAP")
