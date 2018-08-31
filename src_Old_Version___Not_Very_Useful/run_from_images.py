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
parser.add_argument("-d", "--do_MVS", action="store_true", help="If True the pipeline is gonna be using openMVS.\
                    \nThis means that it will not only compute the pointcloud and corresponding camera poses but also the mesh.\
                    \nThis is to be used for example when the 3D model is needed.")
parser.add_argument("-bn", "--base_name", default="YellowTool", help="Base name of the images.\
                    Eg if the images are like Tool1.jpg, Tool2.jpg ... then the base name is Tool")
parser.add_argument("-e", "--extension", default="jpg", help="Extension of the images files.")
parser.add_argument("-s", "--stride", default=10, help="Stide is the step with which the images are gonna be selected\
                    to perform structure from motion. Typically when running the pipeline on images from a video\
                    it would be good to have a step>1 because from one frame to the next there may be too much overlapping\
                    and 100 successive frame may not be enough to have 360degrees pictures of the object of interest")
args = parser.parse_args()

# Perform the reconstruction
if args.do_MVS:
    pPipeline = subprocess.Popen( ["python", "Reconstruct_n_Localize.py", "-bn", args.base_name, "-e", args.extension, "-d", "-s", str(args.stride)])
    pPipeline.wait()
else:
    pPipeline = subprocess.Popen( ["python", "Reconstruct_n_Localize.py", "-bn", args.base_name, "-e", args.extension, "-s", str(args.stride)])
    pPipeline.wait()

duration = (time.time() - start_time)/60
print("Run from images is over after ", duration, " minutes")
