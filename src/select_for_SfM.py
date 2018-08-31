'''
    This script will look into the folder specified as INPUT_DIR in input_dir.py and select 104 images according to the desired step
    The selected images will be stored in the folder INPUT_DIR/images_SfM
'''


import numpy as np
import cv2
import os
import json
import string
from input_dir import INPUT_DIR


def create_images_SfM_folder(step=1, base_name=None):
    '''
        If non existant this function will create a folder INPUT_DIR/../images_SfM
        This folder will contain the 104 first (depending on the step value) images of INPUT_DIR
        The first input of this function is the base name of the images in INPUT_DIR and the extension
            Eg: if the images are like Tool1.jpg, Tool2.jpg ... then the base name is Tool
        The third input is the step between two successive images
            Eg: if the images are like Tool1.jpg, Tool2.jpg ... and the step is 10
                Then the selected images will be Tool1.jpg, Tool11.jp, Tool21.jpg ...
    '''

    # Make sure that the INPUT_DIR has serveral images
    nb_images = len([os.path.join(INPUT_DIR, f).replace("\\","/") for f in os.listdir(INPUT_DIR)])
    if nb_images<2:
        print("There is not enough images in the INPUT_DIR directory")
        return False
    # Get the image_base_name
    if not base_name:
        image_base_name = os.listdir(INPUT_DIR)[0].split('.')[0].rstrip(string.digits)
    else:
        image_base_name = base_name
    # Get extension
    extension = os.listdir(INPUT_DIR)[0].split('.')[-1]

    print("Taking 104 images to perform Structure from Motion\n\n")
    images_SfM_dir = os.path.join(INPUT_DIR, '../images_SfM')
    if not os.path.exists(images_SfM_dir):
        os.mkdir(images_SfM_dir)
        count = 0
        i = 0
        while count<104 and (i+step)<nb_images:
            image_file = os.path.join(INPUT_DIR, image_base_name + str(i) + '.' + extension)
            while not os.path.exists(image_file):
                i += 1
                image_file = os.path.join(INPUT_DIR, image_base_name + str(i) + '.' + extension)
                if i>(nb_images+4):
                    print("Images seem not to be indexed correctly")
                    return False
            image = cv2.imread(image_file)
            cv2.imwrite(os.path.join(images_SfM_dir, image_base_name + str(i) + '.' + extension), image)

            print("{} copied".format(image_base_name + str(i)))
            count += 1
            i += step
        return True
    else:
        print("Folder images_SfM already exists")
        return False


if __name__ == "__main__":
    create_images_SfM_folder()
