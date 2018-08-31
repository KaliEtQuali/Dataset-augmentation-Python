#!/usr/bin/python
#! -*- encoding: utf-8 -*-

'''
    This file runs StructureFromMotion with OpenMVG and then mesh reconstruction with OpenMVS
    The OpenMVG part is the exact same one as for the file SfM_SequentialPipeline.py
'''

# Indicate the openMVG binary directory and the openMVG camera sensor width directory
from dirs import OPENMVG_SFM_BIN, OPENMVS_BIN, CAMERA_SENSOR_WIDTH_DIRECTORY
from input_dir import INPUT_DIR



import os
import subprocess
import sys
import time
import cv2
from select_for_SfM import create_images_SfM_folder



create_images_SfM_folder()


start_time = time.time()
input_dir = os.path.join(INPUT_DIR, '../images_SfM')
output_dir = os.path.join(INPUT_DIR, "../output")
openMVG_output_dir = os.path.join(output_dir, "OpenMVG")
matches_dir = os.path.join(output_dir, "OpenMVG/matches")
reconstruction_dir = os.path.join(output_dir, "OpenMVG/reconstruction_sequential")
camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")

print ("Using input dir  : ", input_dir)
print ("      output_dir : ", output_dir)

# Check if there is a K.txt file that specifies the intrinsics
# and if there is set a variable to be used as arguent in openMVG_main_SfMInit_ImageListing
# If there is not, then check if there is a yaml file that specifies the intrinsics
is_K_specified = False
if os.path.exists(os.path.join(INPUT_DIR, 'K.txt')):
    with open(INPUT_DIR + '/K.txt', 'r') as f:
        raw_txt = f.read()
        txt_list = raw_txt.split(" ")
        K_arg = ""
        tmp = []
        for number in txt_list:
            tmp += number.splitlines()
        for number in tmp:
            K_arg += number + ";"
        K_arg = K_arg[0:-1]
    is_K_specified = True
elif len([os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(('.yml', '.yaml'))])>0:
    yaml_file = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(('.yml', '.yaml'))][0]
    yaml_file = cv2.FileStorage(os.path.join(INPUT_DIR, yaml_file), cv2.FILE_STORAGE_READ)
    K = yaml_file.getNode("K").mat()
    D = yaml_file.getNode("D").mat()
    K_arg = ""
    for line in K:
        for nb in line:
            K_arg += str(nb) + ';'
    K_arg = K_arg[0:-1]
    is_K_specified = True

if is_K_specified:
    print('K is specified')
    print(K_arg)
else:
    print('K is not specified')


# Create the ouput/matches folder if not present
if not os.path.exists(output_dir):
  os.mkdir(output_dir)
if not os.path.exists(openMVG_output_dir):
    os.mkdir(openMVG_output_dir)
if not os.path.exists(matches_dir):
  os.mkdir(matches_dir)

print ("1. Intrinsics analysis")
if is_K_specified:
    pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-d", camera_file_params, "-k", K_arg] )
    pIntrisics.wait()
else:
    pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-d", camera_file_params] )
    pIntrisics.wait()

print ("2. Compute features")
pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT"] )
pFeatures.wait()

print ("3. Compute matches")
pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir] )
pMatches.wait()

# Create the reconstruction if not present
if not os.path.exists(reconstruction_dir):
    os.mkdir(reconstruction_dir)

print ("4. Do Sequential/Incremental reconstruction")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_IncrementalSfM"),  "-i", matches_dir+"/sfm_data.json", "-m", matches_dir, "-o", reconstruction_dir] )
pRecons.wait()

print ("5. Colorize Structure")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
pRecons.wait()

# optional, compute final valid structure from the known camera poses
print ("6. Structure from Known Poses (robust triangulation)")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", reconstruction_dir+"/sfm_data.bin", "-m", matches_dir, "-f", os.path.join(matches_dir, "matches.f.bin"), "-o", os.path.join(reconstruction_dir,"robust.bin")] )
pRecons.wait()

pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/robust.bin", "-o", os.path.join(reconstruction_dir,"robust_colorized.ply")] )
pRecons.wait()

# Create a json file containing the views and the extrinsincs
print("7. Extraction of camera poses")
pData = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ConvertSfM_DataFormat"), "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir, "views_n_extrinsics.json"), "-V", "-E"])
pData.wait()

pData = subprocess.Popen( ["python", "create_correspondances_json.py", reconstruction_dir, output_dir])
pData.wait()
print("Camera poses extracted in file views_n_extrinsics.json and correspondances extracted in correspondances.json")


openMVS_output_dir = os.path.join(output_dir, "OpenMVS")
if not os.path.exists(openMVS_output_dir):
    os.mkdir(openMVS_output_dir)

print("8. Creation of OpenMVS compatible file")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2openMVS"), "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(openMVS_output_dir,"scene.mvs"), "-d", os.path.join(openMVS_output_dir,"undistorted_images")])
pOpenMVS.wait()

print("9. Densify point cloud with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "DensifyPointCloud"), "-i", os.path.join(openMVS_output_dir, "scene.mvs"), "-o", "scene_dense", "-w", openMVS_output_dir])
pOpenMVS.wait()

print("10. Reconstruct mesh with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "ReconstructMesh"), "-i", "scene_dense.mvs", "-o", "scene_dense_mesh", "-w", openMVS_output_dir])
pOpenMVS.wait()

print("11. Refine mesh with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "RefineMesh"), "-i", "scene_dense_mesh.mvs", "-o", "scene_dense_mesh_refined", "-w", openMVS_output_dir])
pOpenMVS.wait()

print("12. Texture mesh with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "TextureMesh"), "-i", "scene_dense_mesh.mvs", "-o", "scene_dense_mesh_textured", "-w", openMVS_output_dir])
pOpenMVS.wait()

print("13. Texture mesh refined with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "TextureMesh"), "-i", "scene_dense_mesh_refined.mvs", "-o", "scene_dense_mesh_refined_textured", "-w", openMVS_output_dir, "--export-type", "obj"])
pOpenMVS.wait()
'''
print("14. Saving all the meshs into a Meshlab mlp file")
pMeshlab = subprocess.Popen( ["meshlabserver",
    "-i", os.path.join(reconstruction_dir, "robust_colorized.ply"),
    "-i", os.path.join(openMVS_output_dir, "scene_dense.ply"),
    "-i", os.path.join(openMVS_output_dir, "scene_dense_mesh.ply"),
    "-i", os.path.join(openMVS_output_dir, "scene_dense_mesh_refined.ply"),
    "-i", os.path.join(openMVS_output_dir, "scene_dense_mesh_textured.ply"),
    "-i", os.path.join(openMVS_output_dir, "scene_dense_mesh_refined_textured.obj"),
    "-w", os.path.join(output_dir, "result.mlp")
    ])
pMeshlab.wait()

print("15. Displaying the meshs in Meshlab")
pMeshlab = subprocess.Popen( ["meshlab", os.path.join(output_dir, "result.mlp")])
'''

print("IT IS ALL OVER")


duration = (time.time() - start_time)/60
print("And it took ", duration, " minutes")
