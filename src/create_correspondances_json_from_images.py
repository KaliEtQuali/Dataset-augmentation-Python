import numpy as np
import os
import json
import cv2
from input_dir import INPUT_DIR



def create_correspondances_json_from_images(im_dir_name='.'):
    images_dir = os.path.join(INPUT_DIR, im_dir_name)
    rotations_file_dir = os.path.join(INPUT_DIR, '../output/Orientations')
    translations_file_dir = os.path.join(INPUT_DIR, '../output/Translations').replace("\\","/")
    output_dir = os.path.join(INPUT_DIR, '../output')
    image_files = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg'))]
    json_dic = {}

    for image_file in image_files:
        image_name = image_file.split('/')[-1]
        image_base_name = image_name.split('.')[0].split('_')[0]

        rotation_file = os.path.join(rotations_file_dir, image_base_name + '.txt')
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

        translation_file = os.path.join(translations_file_dir, image_base_name + '.txt')
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
    create_correspondances_json_from_images()
