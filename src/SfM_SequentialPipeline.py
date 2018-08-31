#!/usr/bin/python
#! -*- encoding: utf-8 -*-
'''
    This file runs the Structure from Motion pipeline with OpenMVG
    It assume that the images and intrinsics are in the INPUT_DIR directory (this is done automatically when using run_from_video)
'''

# Indicate the openMVG binary directory and the openMVG camera sensor width directory
from dirs import OPENMVG_SFM_BIN, OPENMVS_BIN, CAMERA_SENSOR_WIDTH_DIRECTORY
from input_dir import INPUT_DIR



import os
import subprocess
import sys
import time
import cv2
import argparse
from select_for_SfM import create_images_SfM_folder

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--step", default=1, help="Stide is the step with which the images are gonna be selected\
                    to perform structure from motion. Typically when running the pipeline on images from a video\
                    it would be good to have a step>1 because from one frame to the next there may be too much overlapping\
                    and 100 successive frame may not be enough to have 360degrees pictures of the object of interest")
args = parser.parse_args()

start_time = time.time()
input_dir = os.path.join(INPUT_DIR, '../images_SfM')
output_dir = os.path.join(INPUT_DIR, "../output")
openMVG_output_dir = os.path.join(output_dir, "OpenMVG")
matches_dir = os.path.join(output_dir, "OpenMVG/matches")
reconstruction_dir = os.path.join(output_dir, "OpenMVG/reconstruction_sequential")
camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")

print ("Using input dir  : ", input_dir)
print ("      output_dir : ", output_dir)


# First we select a few images from the INPUT_DIR (between 100 and 200 idealy)
# This are the images with which the SfM will be perform (because as SfM my bug with too many images)
# The code of this function is in the file select_for_SfM.py
create_images_SfM_folder(int(args.step))

# Check if there is a K.txt or a YAML file that specifies the intrinsics
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
elif len([os.path.join(INPUT_DIR, '..',f) for f in os.listdir(os.path.join(INPUT_DIR, '..')) if f.endswith(('.yml', '.yaml'))])>0:
    yaml_file = [os.path.join(INPUT_DIR, '..', f) for f in os.listdir(os.path.join(INPUT_DIR, '..')) if f.endswith(('.yml', '.yaml'))][0]
    yaml_file = cv2.FileStorage(os.path.join(INPUT_DIR, '..', yaml_file), cv2.FILE_STORAGE_READ)
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

pData = subprocess.Popen( ["python", "create_correspondances_json.py", reconstruction_dir, os.path.join(output_dir, 'OpenMVG')])
pData.wait()
print("Camera poses extracted in file views_n_extrinsics.json and correspondances extracted in correspondances.json")

print("SFM IS ALL OVER")


duration = (time.time() - start_time)/60
print("And it took ", duration, " minutes")
