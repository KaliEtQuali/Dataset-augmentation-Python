'''
    This file recovers the camera poses of the images in INPUT_DIR that were not used for SfM (reminder:
    these are images of the exact same scene that the one reconstructed via SfM).
    After having localized the images, it replaces the correspondances_by_name.json file with a new one containing the new poses
    It also creates a Orientations directory and a Translations directory
        Those directories contains one txt file for each image
            The txt file as the same name as the corresponding image
            It respectively contains the orientation (axis angles) and the translation of the corresponding image
'''
# Indicate the openMVG binary directory and the openMVG camera sensor width directory
from dirs import OPENMVG_SFM_BIN, OPENMVS_BIN, CAMERA_SENSOR_WIDTH_DIRECTORY
from input_dir import INPUT_DIR



import os
import subprocess
import sys
import time
import json
from create_correspondances_json import from_R_to_angles
import pprint
pp = pprint.PrettyPrinter(indent=2)

input_dir = INPUT_DIR
output_dir = os.path.join(INPUT_DIR, "../output")
openMVG_output_dir = os.path.join(output_dir, "OpenMVG")
openMVS_output_dir = os.path.join(output_dir, "OpenMVS")
matches_dir = os.path.join(output_dir, "OpenMVG/matches")
reconstruction_dir = os.path.join(output_dir, "OpenMVG/reconstruction_sequential")
localization_output_dir = os.path.join(openMVG_output_dir, "localization")
localization_matches_dir = os.path.join(localization_output_dir, "matches")
localization_images_dir = INPUT_DIR



def create_txt_files_with_angles():
    output_path = os.path.join(INPUT_DIR, "../output/Orientations").replace("\\","/")
    input_path = os.path.join(INPUT_DIR, "../output/correspondances_by_name.json").replace("\\","/")
    localization_input_path = os.path.join(INPUT_DIR, "../output/OpenMVG/localization/correspondances_by_name.json").replace("\\","/")
    if os.path.exists(localization_input_path):
        input_path = localization_input_path
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    with open(input_path, encoding='utf-8') as json_file:
        correspondances = json.load(json_file)
    for file_name in correspondances:
        txt_file_name = file_name.split('.')[0] + '.txt'
        with open(os.path.join(output_path, txt_file_name).replace("\\","/"), 'w') as f:
            txt = ""
            for angle in correspondances[file_name]["angles"]:
                txt += " {}".format(angle[0])
            f.write(txt)
            print(txt)



def create_txt_files_with_ts():
    output_path = os.path.join(INPUT_DIR, "../output/Translations").replace("\\","/")
    input_path = os.path.join(INPUT_DIR, "../output/correspondances_by_name.json").replace("\\","/")
    localization_input_path = os.path.join(INPUT_DIR, "../output/OpenMVG/localization/correspondances_by_name.json").replace("\\","/")
    if os.path.exists(localization_input_path):
        input_path = localization_input_path
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    with open(input_path, encoding='utf-8') as json_file:
        correspondances = json.load(json_file)
    for file_name in correspondances:
        txt_file_name = file_name.split('.')[0] + '.txt'
        with open(os.path.join(output_path, txt_file_name).replace("\\","/"), 'w') as f:
            txt = ""
            for pos in correspondances[file_name]["center"]:
                txt += " {}".format(pos)
            f.write(txt)
            print(txt)


def copy_localized_images():
    output_dir = os.path.join(INPUT_DIR, "../output")
    openMVG_output_dir = os.path.join(output_dir, "OpenMVG")
    save_dir = os.path.join(INPUT_DIR, '../output/images_localized')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    with open(os.path.join(output_dir, 'correspondances_by_name.json'), encoding='utf-8') as json_file:
        correspondances = json.load(json_file)
    for image_name in correspondances:
        image_file = os.path.join(INPUT_DIR, '../images', image_name)
        image = cv2.imread(image_file)
        cv2.imwrite(os.path.join(save_dir, image_name), image)
        print("{} copied".format(image_name))


def create_rotation_n_translation_files():
    create_txt_files_with_ts()
    create_txt_files_with_angles()



if __name__ == "__main__":
    # Create the ouput/matches folder if not present
    if not os.path.exists(localization_output_dir):
        os.mkdir(localization_output_dir)
    if not os.path.exists(localization_matches_dir):
        os.mkdir(localization_matches_dir)

    # Run the relocalization
    print ("8. Localization of images")
    pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfM_Localization"),  "-i", reconstruction_dir+"/sfm_data.bin", "-m", matches_dir, "-o", localization_output_dir, "-u", localization_matches_dir, "-q", localization_images_dir, "-s"] )
    pFeatures.wait()

    print("9. Creation of the correspondances_by_name.json file based on the sfm_data_expanded.json file")
    # Load the json file
    with open(os.path.join(localization_output_dir, "sfm_data_expanded.json"), encoding='utf-8') as json_file:
        sfm_data_expanded = json.load(json_file)

    correspondances = {}
    n = len(sfm_data_expanded['views'])
    m = len(sfm_data_expanded['extrinsics'])
    # If the number of views differs from the number of extrinsics then some may went wrong
    if m != n:
        print('The number of views ({}) and number of extrinsics ({}) are not equal'.format(n,m))
    print(n, sfm_data_expanded['views'][-1]["key"])

    for i in range(m):
        index_view = sfm_data_expanded['extrinsics'][i]["key"]
        # Get the image file name
        image = sfm_data_expanded['views'][index_view]['value']['ptr_wrapper']['data']["filename"]
        # Get the corresponding pose (rotation matrix and translation vector)
        pose = sfm_data_expanded['extrinsics'][i]['value']
        # Add the rotation in axis angle format to the pose object
        pose['angles'] = from_R_to_angles(pose['rotation'])
        # Store this object in the correspondances dict variable
        correspondances[image] = pose
        print("{} added".format(image))

    # Print the correspondances dict for quick checks
    #pp.pprint(correspondances)

    # Store the correspondances dict object in a json file named correspondances_by_name_expanded.json
    with open(os.path.join(output_dir, 'correspondances_by_name.json'), 'w') as outfile:
        json.dump(correspondances, outfile)

    create_rotation_n_translation_files()

    print("Json created")
