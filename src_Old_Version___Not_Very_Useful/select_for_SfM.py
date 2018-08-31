import numpy as np
import cv2
import os
import json
from input_dir import INPUT_DIR



def create_images_SfM_folder(image_base_name, extension="jpg", stride=1):
    '''
        If non existant this function will create a folder INPUT_DIR/../images_SfM
        This folder will contain the 104 first images of INPUT_DIR
        The first input of this function is the base name of the images in INPUT_DIR and the extension
            Eg: if the images are like Tool1.jpg, Tool2.jpg ... then the base name is Tool
        The second input is the step between two successive images
            Eg: if the images are like Tool1.jpg, Tool2.jpg ... and the stride is 10
                Then the selected images will be Tool1.jpg, Tool11.jp, Tool21.jpg ...
    '''
    print("Taking the 104 first images to perform Structure from Motion\n\n")
    images_SfM_dir = os.path.join(INPUT_DIR, '../images_SfM')
    if not os.path.exists(images_SfM_dir):
        os.mkdir(images_SfM_dir)
        count = 0
        i = 0
        while count<104 and (i+stride)<len([os.path.join(INPUT_DIR, f).replace("\\","/") for f in os.listdir(INPUT_DIR)]):
            image_file = os.path.join(INPUT_DIR, image_base_name + str(i) + '.' + extension)
            while not os.path.exists(image_file):
                i += 1
                image_file = os.path.join(INPUT_DIR, image_base_name + str(i) + '.' + extension)
            image = cv2.imread(image_file)
            cv2.imwrite(os.path.join(images_SfM_dir, image_base_name + str(i) + '.' + extension), image)

            print("{} copied".format(image_base_name + str(i)))
            count += 1
            i += stride
    else:
        print("Folder images_SfM already exists")


if __name__ == "__main__":
    create_images_SfM_folder("frame", stride=5)
