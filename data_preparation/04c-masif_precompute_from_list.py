import sys
import time
import os
import numpy as np
from IPython.core.debugger import set_trace
import warnings 
with warnings.catch_warnings(): 
    warnings.filterwarnings("ignore",category=FutureWarning)
sys.path.append('/workspace/source')
# Configuration imports. Config should be in run_args.py
from default_config.masif_opts import masif_opts

np.random.seed(0)

# Load training data (From many files)
from masif_modules.read_data_from_surface import read_data_from_surface, compute_shape_complementarity

def extract_pdb_ids(filename):
    pdb_ids = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(">"):
                pdb_id = line.split(">")[1:]
            else:
                continue
            if pdb_id:
                pdb_ids.append(pdb_id)
    return pdb_ids

# if len(sys.argv) <= 1:
#     print("Usage: {config} "+sys.argv[0]+" {masif_ppi_search | masif_site} PDBID_A")
#     print("A or AB are the chains to include in this surface.")
#     sys.exit(1)
# else:
#     print(sys.argv[2])

input_ids = extract_pdb_ids("/workspace/source/data_preparation/RBP_in_PDB.txt")
masif_app = 'masif_site'

if masif_app == 'masif_ppi_search': 
    params = masif_opts['ppi_search']
elif masif_app == 'masif_site':
    params = masif_opts['site']
    params['ply_chain_dir'] = masif_opts['ply_chain_dir']
elif masif_app == 'masif_ligand':
    params = masif_opts['ligand']
i=0
# ppi_pair_id = sys.argv[2]
for ppi_pair_id in input_ids:
    ppi_pair_id = ppi_pair_id[0]
    total_shapes = 0
    total_ppi_pairs = 0
    np.random.seed(0)
    print(f'{i}/{len(input_ids)}: Reading data from input {ppi_pair_id}.ply surface files.')

    all_list_desc = []
    all_list_coords = []
    all_list_shape_idx = []
    all_list_names = []
    idx_positives = []

    my_precomp_dir = params['masif_precomputation_dir']+ppi_pair_id+'/'
    if not os.path.exists(my_precomp_dir):
        os.makedirs(my_precomp_dir)

    # Read directly from the ply file.
    fields = ppi_pair_id.split('_')
    ply_file = {}
    ply_file['p1'] = masif_opts['ply_file_template'].format(fields[0], fields[1])

    if len (fields) == 2 or fields[2] == '':
        pids = ['p1']
    else:
        ply_file['p2']  = masif_opts['ply_file_template'].format(fields[0], fields[2])
        pids = ['p1', 'p2']
        
    # Compute shape complementarity between the two proteins. 
    rho = {}
    neigh_indices = {}
    mask = {}
    input_feat = {}
    theta = {}
    iface_labels1 = {}
    iface_labels2 = {}
    verts = {}

    for pid in pids:
        input_feat[pid], rho[pid], theta[pid], mask[pid], neigh_indices[pid], iface_labels1[pid], iface_labels2[pid], verts[pid] = read_data_from_surface(ply_file[pid], params)


    # Save data only if everything went well. 
    for pid in pids: 
        np.save(my_precomp_dir+pid+'_rho_wrt_center', rho[pid])
        np.save(my_precomp_dir+pid+'_theta_wrt_center', theta[pid])
        np.save(my_precomp_dir+pid+'_input_feat', input_feat[pid])
        np.save(my_precomp_dir+pid+'_mask', mask[pid])
        np.save(my_precomp_dir+pid+'_list_indices', neigh_indices[pid])
        np.save(my_precomp_dir+pid+'_iface_labels1', iface_labels1[pid])
        np.save(my_precomp_dir+pid+'_iface_labels2', iface_labels2[pid])
        # Save x, y, z
        np.save(my_precomp_dir+pid+'_X.npy', verts[pid][:,0])
        np.save(my_precomp_dir+pid+'_Y.npy', verts[pid][:,1])
        np.save(my_precomp_dir+pid+'_Z.npy', verts[pid][:,2])
    
    i+=1
