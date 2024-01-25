#!/usr/bin/python
import numpy as np
import os
import Bio
import shutil
from Bio.PDB import * 
import sys
import importlib
from IPython.core.debugger import set_trace
sys.path.append('/workspace/source')
# Local includes
import default_config.masif_opts
from default_config.masif_opts import masif_opts
from triangulation.computeMSMS import computeMSMS
from triangulation.fixmesh import fix_mesh
import pymesh
from input_output.extractPDB import extractPDB
from input_output.save_ply import save_ply
from input_output.read_ply import read_ply
from input_output.protonate import protonate
from triangulation.computeHydrophobicity import computeHydrophobicity
from triangulation.computeCharges import computeCharges, assignChargesToNewMesh
from triangulation.computeAPBS import computeAPBS
from triangulation.compute_normal import compute_normal
from triangulation.computeBinding import *
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def extract_rbp_info(filename, pdb_id_query):
    binding_index = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(">"):
                pdb_id_key = line.split(">")[1:][0]
                if pdb_id_key == pdb_id_query:
                    #向下读取一行
                    line = file.readline().strip()
                    fasta_seq = line
                    #向下读取一行
                    line = file.readline().strip()
                    binding_index.append(line)
                    #向下读取一行
                    line = file.readline().strip()
                    binding_index.append(line)
                    break
            else:
                continue
    return fasta_seq, binding_index

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

if len(sys.argv) <= 1: 
    print("Usage: {config} "+sys.argv[0]+" PDBID_A")
    print("A or AB are the chains to include in this surface.")
    sys.exit(1)

# RBP_list_path = sys.argv[1]
# Save the chains as separate files. 
# startidx=412
input_ids = [sys.argv[1]]
print(input_ids)
# print(input_ids)
# exit(1)
# input_ids = [['4qoz_C']]
for input in input_ids:
    in_fields = input.split("_")
    print(in_fields)
    pdb_id = in_fields[0]
    chain_ids1 = in_fields[1]
    # print(f"{startidx}:Processing "+pdb_id+"_"+chain_ids1)
    # if (len(sys.argv)>2) and (sys.argv[2]=='masif_ligand'):
    #     pdb_filename = os.path.join(masif_opts["ligand"]["assembly_dir"],pdb_id+".pdb")
    # else:
    #     pdb_filename = masif_opts['raw_pdb_dir']+pdb_id+".pdb"
    pdb_filename = masif_opts['raw_pdb_dir']+pdb_id+".pdb"
    tmp_dir= masif_opts['tmp_dir']
    protonated_file = tmp_dir+"/"+pdb_id+".pdb"
    protonate(pdb_filename, protonated_file)
    pdb_filename = protonated_file

    # Extract chains of interest.
    out_filename1 = tmp_dir+"/"+pdb_id+"_"+chain_ids1
    # print(out_filename1)
    extractPDB(pdb_filename, out_filename1+".pdb", chain_ids1)
    
    # Compute MSMS of surface w/hydrogens, 
    try:
        vertices1, faces1, normals1, names1, areas1 = computeMSMS(out_filename1+".pdb",\
            protonate=True)
    except:
        set_trace()
    
    # if masif_opts["RNA_contact"]:
    #     fasta_seq, binding_index = extract_rbp_info(RBP_list_path, input[0])
    #     # 第1条结合域信息
    #     RNA_binding1 = computeBinding(names1, out_filename1+".pdb", fasta_seq, binding_index[0])
    #     # 第2条结合域信息
    #     RNA_binding2 = computeBinding(names1, out_filename1+".pdb", fasta_seq, binding_index[1])

    # Compute "charged" vertices
    if masif_opts['use_hbond']:
        vertex_hbond = computeCharges(out_filename1, vertices1, names1)

    # For each surface residue, assign the hydrophobicity of its amino acid. 
    if masif_opts['use_hphob']:
        vertex_hphobicity = computeHydrophobicity(names1)

    # If protonate = false, recompute MSMS of surface, but without hydrogens (set radius of hydrogens to 0).
    vertices2 = vertices1
    faces2 = faces1

    # Fix the mesh.
    mesh = pymesh.form_mesh(vertices2, faces2)
    regular_mesh = fix_mesh(mesh, masif_opts['mesh_res'])

    # Compute the normals
    vertex_normal = compute_normal(regular_mesh.vertices, regular_mesh.faces)
    # Assign charges on new vertices based on charges of old vertices (nearest
    # neighbor)
    
    if masif_opts['RNA_contact']:
        vertex_RNA_binding = np.load(sys.argv[2]).reshape(-1, 1)[:, 0]
        for i in range(len(vertex_RNA_binding)):
            if vertex_RNA_binding[i] > 0.7:
                vertex_RNA_binding[i] = 1
                # print("vertex_RNA_binding", vertex_RNA_binding[i])
            else:
                vertex_RNA_binding[i] = 0
        print("load RNA_binding from "+sys.argv[2])

    if masif_opts['use_hbond']:
        vertex_hbond = assignChargesToNewMesh(regular_mesh.vertices, vertices1,\
            vertex_hbond, masif_opts)

    if masif_opts['use_hphob']:
        vertex_hphobicity = assignChargesToNewMesh(regular_mesh.vertices, vertices1,\
            vertex_hphobicity, masif_opts)

    if masif_opts['use_apbs']:
        vertex_charges = computeAPBS(regular_mesh.vertices, out_filename1+".pdb", out_filename1)

    # iface = np.zeros(len(regular_mesh.vertices))
    # if 'compute_iface' in masif_opts and masif_opts['compute_iface']:
    #     # Compute the surface of the entire complex and from that compute the interface.
    #     v3, f3, _, _, _ = computeMSMS(pdb_filename,\
    #         protonate=True)
    #     # Regularize the mesh
    #     mesh = pymesh.form_mesh(v3, f3)
    #     # I believe It is not necessary to regularize the full mesh. This can speed up things by a lot.
    #     full_regular_mesh = mesh
    #     # Find the vertices that are in the iface.
    #     v3 = full_regular_mesh.vertices
    #     # Find the distance between every vertex in regular_mesh.vertices and those in the full complex.
    #     kdt = KDTree(v3)
    #     d, r = kdt.query(regular_mesh.vertices)
    #     d = np.square(d) # Square d, because this is how it was in the pyflann version.
    #     assert(len(d) == len(regular_mesh.vertices))
    #     iface_v = np.where(d >= 2.0)[0]
    #     iface[iface_v] = 1.0
    #     # Convert to ply and save.
    #     save_ply(out_filename1+".ply", regular_mesh.vertices,\
    #                         regular_mesh.faces, normals=vertex_normal, charges=vertex_charges,\
    #                         normalize_charges=True, hbond=vertex_hbond, hphob=vertex_hphobicity,\
    #                         iface=iface, RNA_binding1=vertex_RNA_binding1, RNA_binding2=vertex_RNA_binding2)

    # else:
    #     # Convert to ply and save.
    #     save_ply(out_filename1+".ply", regular_mesh.vertices,\
    #                         regular_mesh.faces, normals=vertex_normal, charges=vertex_charges,\
    #                         normalize_charges=True, hbond=vertex_hbond, hphob=vertex_hphobicity,\
    #                         RNA_binding1=vertex_RNA_binding1, RNA_binding2=vertex_RNA_binding2)
    save_ply(out_filename1+".ply", regular_mesh.vertices,\
                            regular_mesh.faces, normals=vertex_normal, charges=vertex_charges,\
                            normalize_charges=True, hbond=vertex_hbond, hphob=vertex_hphobicity,\
                            RNA_binding1=vertex_RNA_binding)
    if not os.path.exists(masif_opts['ply_chain_dir']):
        os.makedirs(masif_opts['ply_chain_dir'])
    if not os.path.exists(masif_opts['pdb_chain_dir']):
        os.makedirs(masif_opts['pdb_chain_dir'])
    shutil.copy(out_filename1+'.ply', masif_opts['ply_chain_dir']) 
    shutil.copy(out_filename1+'.pdb', masif_opts['pdb_chain_dir'])
    # startidx+=1
