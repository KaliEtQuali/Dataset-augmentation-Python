'''
    This file successively runs SfM_SequentialPipeline.py, then localize_plus_ultra_images.py, and then, depending on the arguments, Mesh_reconstruction.py
'''

import subprocess
import time
import argparse

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--do_MVS", action="store_true", help="If True the pipeline is gonna be using openMVS.\
                    \nThis means that it will not only compute the pointcloud and corresponding camera poses but also the mesh.\
                    \nThis is to be used for example when the 3D model is needed.")
parser.add_argument("-bn", "--base_name", default="YellowTool", help="Base name of the images.\
                    Eg if the images are like Tool1.jpg, Tool2.jpg ... then the base name is Tool")
parser.add_argument("-e", "--extension", default="jpg", help="Extension of the images files.")
parser.add_argument("-s", "--stride", default=1, help="Stide is the step with which the images are gonna be selected\
                    to perform structure from motion. Typically when running the pipeline on images from a video\
                    it would be good to have a step>1 because from one frame to the next there may be too much overlapping\
                    and 100 successive frame may not be enough to have 360degrees pictures of the object of interest")
args = parser.parse_args()

# First run the StructureFromMotion pipeline for a few images
pSfM = subprocess.Popen( ["python", "SfM_SequentialPipeline.py", "-bn", args.base_name, "-e", args.extension, "-s", args.stride])
pSfM.wait()

# Then localize the remaining images
pLocalize = subprocess.Popen( ["python", "localize_plus_ultra_images.py"])
pLocalize.wait()

if args.do_MVS:
    pOpenMVS = subprocess.Popen( ["python", "Mesh_reconstruction.py"])
    pOpenMVS.wait()

duration = (time.time() - start_time)/60
print("Really over and it took {} minutes".format(duration))
