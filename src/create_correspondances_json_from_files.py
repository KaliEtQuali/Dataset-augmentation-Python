import numpy as np
import os
import cv2
import json
from input_dir import INPUT_DIR


def create_correspondances_json_from_files():
    rotations_file_dir = os.path.join(INPUT_DIR, '../output/Orientations').replace("\\","/")
    output_dir = os.path.join(INPUT_DIR, '../output').replace("\\","/")
    rotation_files = [os.path.join(rotations_file_dir, f).replace("\\","/") for f in os.listdir(rotations_file_dir) if f.endswith(('.txt'))]
    json_dic = {}

    for rotation_file in rotation_files:
        image_name = rotation_file.split('/')[-1].split('.')[0] + '.png'
        with open(rotation_file) as r_file:
            rotation = r_file.read()
        # Convert rotation file to float array
        rotation = rotation.split(" ")[1:]
        for i in range(3):
            rotation[i] = float(rotation[i].rstrip())
        R = np.zeros((3,3))
        cv2.Rodrigues(np.asarray(rotation), R)
        rotation_dic = {"angles": rotation, "rotation": R.tolist()}
        json_dic[image_name] = rotation_dic
        print("{} added".format(image_name))

    translations_file_dir = os.path.join(INPUT_DIR, '../output/Translations').replace("\\","/")
    translation_files = [os.path.join(translations_file_dir, f).replace("\\","/") for f in os.listdir(translations_file_dir) if f.endswith(('.txt'))]

    for translation_file in translation_files:
        image_name = translation_file.split('/')[-1].split('.')[0] + '.png'
        with open(translation_file) as t_file:
            translation = t_file.read()
        # Convert translation file to float array
        translation = translation.split(" ")[1:]
        for i in range(3):
            translation[i] = float(translation[i].rstrip())
        json_dic[image_name]["center"] = translation
        print("{} added".format(image_name))

    with open(os.path.join(output_dir, 'correspondances_by_name.json'), 'w') as outfile:
        json.dump(json_dic, outfile)

if __name__ == "__main__":
    create_correspondances_json_from_files()
