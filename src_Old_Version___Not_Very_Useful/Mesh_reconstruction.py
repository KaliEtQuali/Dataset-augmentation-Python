from dirs import OPENMVG_SFM_BIN, OPENMVS_BIN, CAMERA_SENSOR_WIDTH_DIRECTORY
from input_dir import INPUT_DIR

'''
    Runs the OpenMVS reconstruction pipeline
    It assumes that the OpenMVG pipeline has has already been successfully ran
'''


import os
import subprocess
import sys
import time


start_time = time.time()
input_dir = os.path.join(INPUT_DIR, '../images_SfM')
output_dir = os.path.join(INPUT_DIR, "../output")
openMVG_output_dir = os.path.join(output_dir, "OpenMVG")
matches_dir = os.path.join(output_dir, "OpenMVG/matches")
reconstruction_dir = os.path.join(output_dir, "OpenMVG/reconstruction_sequential")
camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")

openMVS_output_dir = os.path.join(output_dir, "OpenMVS")
if not os.path.exists(openMVS_output_dir):
    os.mkdir(openMVS_output_dir)

print("10. Creation of OpenMVS compatible file")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2openMVS"), "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(openMVS_output_dir,"scene.mvs"), "-d", os.path.join(openMVS_output_dir,"undistorted_images")])
pOpenMVS.wait()

print("11. Densify point cloud with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "DensifyPointCloud"), "-i", os.path.join(openMVS_output_dir, "scene.mvs"), "-o", "scene_dense", "-w", openMVS_output_dir])
pOpenMVS.wait()

print("12. Reconstruct mesh with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "ReconstructMesh"), "-i", "scene_dense.mvs", "-o", "scene_dense_mesh", "-w", openMVS_output_dir])
pOpenMVS.wait()

print("13. Refine mesh with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "RefineMesh"), "-i", "scene_dense_mesh.mvs", "-o", "scene_dense_mesh_refined", "-w", openMVS_output_dir])
pOpenMVS.wait()

print("14. Texture mesh with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "TextureMesh"), "-i", "scene_dense_mesh.mvs", "-o", "scene_dense_mesh_textured", "-w", openMVS_output_dir])
pOpenMVS.wait()

print("15. Texture mesh refined with OpenMVS")
pOpenMVS = subprocess.Popen( [os.path.join(OPENMVS_BIN, "TextureMesh"), "-i", "scene_dense_mesh_refined.mvs", "-o", "scene_dense_mesh_refined_textured", "-w", openMVS_output_dir, "--export-type", "obj"])
pOpenMVS.wait()

print("16. Saving all the meshs into a Meshlab mlp file")
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

#print("15. Displaying the meshs in Meshlab")
#pMeshlab = subprocess.Popen( ["meshlab", os.path.join(output_dir, "result.mlp")])

duration = (time.time() - start_time)/60
print("Mesh reconstruction is over after ", duration, " minutes")
