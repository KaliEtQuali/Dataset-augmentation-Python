'''
    This file runs the StructureFromMotion pipeline from a mp4 video file in the directory specified as VIDEO_DIR
    Depending on the --do_MVS argument it runs or not the OpenMVS reconstruction pipeline
'''

import subprocess
import argparse
import os
import time

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--no_MVS", action="store_true", help="If specified the pipeline is gonna not be using openMVS.\
                    \nThis means that it will only compute the pointcloud and corresponding camera poses and not the mesh.\
                    \nThis is to be used for example when only the pointcloud is needed.")
parser.add_argument("-s", "--step", default=1, help="Stide is the step with which the images are gonna be selected\
                    to perform structure from motion. Typically when running the pipeline on images from a video\
                    it would be good to have a step>1 because from one frame to the next there may be too much overlapping\
                    and 100 successive frame may not be enough to have 360degrees pictures of the object of interest")
args = parser.parse_args()

# Perform the reconstruction
if args.no_MVS:
    pPipeline = subprocess.Popen( ["python", "Reconstruct_n_Localize.py", "-n", "-s", str(args.step)])
    pPipeline.wait()
else:
    pPipeline = subprocess.Popen( ["python", "Reconstruct_n_Localize.py", "-s", str(args.step)])
    pPipeline.wait()

duration = (time.time() - start_time)/60
print("Run from images is over after ", duration, " minutes")
