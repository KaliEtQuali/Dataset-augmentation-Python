'''
    This file contain a main function that just delete all the mask images in the input directory specified as
    INPUT_DIR in dirs.py
    It is useful since the mask images have to be in the same directory than the rgb images.
    It allows the user to delete the masks without having to do it manually which would be a lot of labour work
'''


import os
import numpy as np
import cv2
from input_dir import INPUT_DIR

if __name__ == '__main__':
    # try to find all the files whom name finishes with 'mask.png', these are the masks images according to OpenMVG syntax
    try:
        image_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith('mask.png')]
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
    nb_removed = 0
    # If there actually are some masks then remove them one by one and print what has been removed each time
    if len(image_files)>1:
        for mask in image_files:
            os.remove(mask)
            print(mask.split('/')[-1] + "  has been removed")
            nb_removed += 1
    else:
        print("There is no mask in the input directory specified as INPUT_DIR")
    print(str(nb_removed) + " files were cleared")
