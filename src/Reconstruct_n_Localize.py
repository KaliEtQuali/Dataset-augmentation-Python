'''
    This file successively runs SfM_SequentialPipeline.py, then localize_plus_ultra_images.py, and then, depending on the arguments, Mesh_reconstruction.py
'''

import subprocess
import time
import argparse

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

# First run the StructureFromMotion pipeline for a few images
pSfM = subprocess.Popen( ["python", "SfM_SequentialPipeline.py", "-s", args.step])
pSfM.wait()

# Then localize the remaining images
pLocalize = subprocess.Popen( ["python", "localize_plus_ultra_images.py"])
pLocalize.wait()

if not args.no_MVS:
    pOpenMVS = subprocess.Popen( ["python", "Mesh_reconstruction.py"])
    pOpenMVS.wait()

duration = (time.time() - start_time)/60
print("Really over and it took {} minutes".format(duration))
