'''
    This file contains function fuction that allows to create segmentation masks around the object of interest
        To do that is uses the 3D mesh of the object and reproject it to obtain the 2D coordinates of the OOI
        For these functions to work it is required to have:
            a YML file containing the intrinsics and distortion coefficients in the INPUT_DIR
            a mesh of the OOI in PLy or OBJ format in the INPUT_DIR/../output dir
            images of course
        The masks wiil be saved in the output directory in a directory named "masks" (very original isn't it? ^^)
'''


import os
import numpy as np
import cv2
import time
import math
from input_dir import INPUT_DIR
from automatic_cropping_n_resize import search_bb, load_global_variables, display_projection


def create_masks(obj_base_name="OOI_mesh"):
    '''
        Function that creates a mask of the OOI based on the reprojection of a dense point cloud of the OOI
    '''
    K, D, PC, correspondances = load_global_variables(obj_base_name=obj_base_name)
    images_dir = INPUT_DIR
    masks_dir = os.path.join(INPUT_DIR, "../output/masks")
    if not os.path.exists(masks_dir):
        os.mkdir(masks_dir)
    i = 0
    nb_images = len(correspondances)
    for image_name in correspondances:
        # Load image
        mask_name = image_name.split('.')[0] + "_mask.png"
        mask_path = os.path.join(masks_dir, mask_name)
        if not os.path.exists(mask_path):
            image = cv2.imread(os.path.join(images_dir, image_name))
            shape = image.shape
            points_projected = search_bb(image_name)

            mask = np.zeros(shape,np.uint8)
            for point in points_projected:
                if 0<point[0]<shape[1] and 0<point[1]<shape[0]:
                    mask[int(point[1]), int(point[0])] = 255
                    #print(point)
            kernel = np.ones((5,5), np.uint8)
            dilate = cv2.dilate(mask, kernel, iterations=1)
            closing = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
            closing = cv2.morphologyEx(closing, cv2.MORPH_CLOSE, kernel)

            image_path = os.path.join(images_dir, image_name)
            cv2.imwrite(mask_path, closing)

            percent = math.floor(100*(i/nb_images))
            print('{}%'.format(percent))

            # Uncomment to visualize the bonding boxes
            #display_bb(clone)
        else:
            print("Stage: {}".format(i))
            print("Mask " + mask_name + " already exists")
        i += 1

def add_segmentation_to_background():
    # Consider the right directories
    masks_dir = os.path.join(INPUT_DIR, "../output/masks")
    seg_dir = os.path.join(INPUT_DIR, "../output/segmented")
    bg_dir = os.path.join(INPUT_DIR, "../backgrounds")

    if  not os.path.exists(seg_dir):
        os.mkdir(seg_dir)

    # Load the masks and images paths
    masks_paths = [os.path.join(masks_dir, f) for f in os.listdir(masks_dir) if f.endswith('mask.png')]
    images_paths = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith('.jpg')]

    # Get images' shape
    shape = cv2.imread(images_paths[0]).shape

    # For each images extract tool and paste it on background
    cv2.namedWindow("image")
    for image_path in images_paths:
        image = cv2.imread(image_path)
        image_name = image_path.split('/')[-1].split('.')[0]
        mask_path = os.path.join(masks_dir, image_name + '_mask.png')
        if os.path.exists(mask_path):
            mask = cv2.imread(mask_path)
            mask_applied = cv2.bitwise_and(image, mask)

            while True:
                # display the image and wait for a keypress
                cv2.imshow("image", mask_applied)
                key = cv2.waitKey(1) & 0xFF

                # if the 'c' key is pressed, go to next image
                if key == ord("c"):
                	break
                elif key == ord('s'):
                    cv2.imwrite(os.path.join(seg_dir, image_name + ".png"), mask_applied)
                    print("{} segmented saved".format(image_name))
                    break

    # close all open windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    #create_masks()
    add_segmentation_to_background()
