#!/usr/bin/python
import re
import Bio
from Bio.PDB import * 
import sys
import importlib
import os
sys.path.append('/workspace/source')
from default_config.masif_opts import masif_opts
from input_output.protonate import protonate

def extract_pdb_ids(filename):
    pdb_ids = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(">"):
                pdb_id = re.search(r'([A-Za-z0-9]{4})', line)
            else:
                continue
            if pdb_id:
                pdb_ids.append(pdb_id.group(0))
    return pdb_ids

if len(sys.argv) <= 1: 
    print("Usage: "+sys.argv[0]+" /path/to/RBP_in_PDB.txt")
    sys.exit(1)

if not os.path.exists(masif_opts['raw_pdb_dir']):
    os.makedirs(masif_opts['raw_pdb_dir'])

if not os.path.exists(masif_opts['tmp_dir']):
    os.mkdir(masif_opts['tmp_dir'])

pdb_ids=extract_pdb_ids(sys.argv[1])

for pdb in pdb_ids:
    in_fields = pdb.split('_')
    pdb_id = in_fields[0]
    # Download pdb 
    pdbl = PDBList(server='ftp://ftp.wwpdb.org')
    pdb_filename = pdbl.retrieve_pdb_file(pdb_id, pdir=masif_opts['tmp_dir'],file_format='pdb')

    ##### Protonate with reduce, if hydrogens included.
    # - Always protonate as this is useful for charges. If necessary ignore hydrogens later.
    protonated_file = masif_opts['raw_pdb_dir']+"/"+pdb_id+".pdb"
    protonate(pdb_filename, protonated_file)
    pdb_filename = protonated_file



