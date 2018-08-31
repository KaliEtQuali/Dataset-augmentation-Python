'''
    This file runs the StructureFromMotion pipeline from a mp4 video file in the directory specified as VIDEO_DIR
    Depending on the --do_MVS argument it runs or not the OpenMVS reconstruction pipeline
'''


from dirs import VIDEO_DIR
from extract_images_from_video import save_frames
from shutil import copyfile
import subprocess
import argparse
import os
import time

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--do_MVS", action="store_true", help="If True the pipeline is gonna be using openMVS.\
                    \nThis means that it will not only compute the pointcloud and corresponding camera poses but also the mesh.\
                    \nThis is to be used for example when the 3D model is needed.")
parser.add_argument("-bn", "--base_name", default="YellowTool", help="Base name of the images that will be created.\
                    Eg if you want the images to be like Tool1.jpg, Tool2.jpg ... then the base name is Tool")
parser.add_argument("-e", "--extension", default="jpg", help="Extension of the images files.")
parser.add_argument("-s", "--stride", default=10, help="Stide is the step with which the images are gonna be selected\
                    to perform structure from motion. Typically when running the pipeline on images from a video\
                    it would be good to have a step>1 because from one frame to the next there may be too much overlapping\
                    and 100 successive frame may not be enough to have 360degrees pictures of the object of interest")
args = parser.parse_args()


# Load the video by searching for a mp4 file in the VIDEO_DIR
video_path = [os.path.join(VIDEO_DIR, f).replace("\\","/") for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')][0]
video_base_name = video_path.split('/')[-1].split('.')[0]

# Extract the frames of the video
save_frames(VIDEO_DIR, video_base_name, args.base_name)

# Copy the intrinsics file in the images directory
intrinsics_file = [os.path.join(VIDEO_DIR, f).replace("\\","/") for f in os.listdir(VIDEO_DIR) if f.endswith(("txt", "yml", "yaml"))][0]
intrinsics_file_name = intrinsics_file.split('/')[-1]
copyfile(intrinsics_file, os.path.join(VIDEO_DIR, 'images', intrinsics_file_name)).replace("\\","/")

# Specify the INPUT_DIR as the directory in which we just saved the frames of the video
with open("./input_dir.py", 'w') as f:
    f.write("INPUT_DIR = \"{}\"".format(os.path.join(VIDEO_DIR, 'images')))

# Perform the reconstruction
if args.do_MVS:
    pPipeline = subprocess.Popen( ["python", "Reconstruct_n_Localize.py", "-bn", args.base_name, "-e", args.extension, "-d", "-s", str(args.stride)])
    pPipeline.wait()
else:
    pPipeline = subprocess.Popen( ["python", "Reconstruct_n_Localize.py", "-bn", args.base_name, "-e", args.extension, "-s", str(args.stride)])
    pPipeline.wait()

duration = (time.time() - start_time)/60
print("Run from video is over after ", duration, " minutes")
