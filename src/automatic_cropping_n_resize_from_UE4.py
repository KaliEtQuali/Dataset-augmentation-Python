'''
    This file is doing the exact same thing as automatic_cropping_n_resize.py, the only difference being that it creates a
    correspondances_by_name.json file before doing that and that it directly loads the instrinsincs from src/Intrinsics/UE4.yaml,
    useful fo cropping images rendered with UE4.
'''

import subprocess
from automatic_cropping_n_resize import *

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
K = []
PC = []
D = []
correspondances = []





if __name__ == '__main__':
    start_time = time.time()

    pJSON = subprocess.Popen(["python", "create_correspondances_json_from_files.py"])
    pJSON.wait()

    output_dir = os.path.join(INPUT_DIR, "../output").replace("\\","/")
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)

    print("Starting automatic cropping")
    Cropper = automatic_cropator()
    yml_dir = os.path.join(os.getcwd(),"Intrinsincs/UE4")
    Cropper.load_variables(yml_dir=yml_dir)
    Cropper.crop_images()
    pResize = subprocess.Popen( ["python", "resize_cropped_images.py"])
    pResize.wait()

    duration = (time.time() - start_time)/60
    print("Automatic cropping is over after ", duration, " minutes")
