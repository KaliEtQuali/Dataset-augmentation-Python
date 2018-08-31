'''
    This file's main function reads all the images in the directory specified as INPUT_DIR in the dirs.py file
    Then, for each image, we can draw a box on it with the mouse
        Once the left button mouse is releasedm the box is drawn on the image, we can then:
            press 's' to save the corresponding mask and the corresponding cropped image
            press 'r' to cancel the selection and re do it again
            press 'c' to cancel and move on to the next image
        The cropped images are saved in another directory called 'cropped_images' as follows:
            .
            .
            .... INPUT_DIR
            .        .
            .        .
            .        .... image1
            .        .... image2
            .        .     .
            .        .     .
            .        .     .
            .        .... imageN
            .
            .
            .... cropped_images
'''

import os
import numpy as np
import cv2
from input_dir import INPUT_DIR

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        # draw a rectangle around the region of interest
        cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.imshow("image", image)


def create_crop(image, image_path):
    # Function that creates a cropped image based on:
    #   the original image -> obviously useful to crop it
    #   the image path -> helpful for the path of the mask
    # the function also relies on the global variable refPt that contains the information of the box mask for the current image
    global refPt
    cropped_dir = os.path.join(INPUT_DIR, "../output/cropped_images").replace("\\","/")
    if not os.path.exists(cropped_dir):
      os.makedirs(cropped_dir)
    cropped_name = image_path.split('/')[-1][0:-4] + "_cropped.png"
    cropped_path = os.path.join(cropped_dir, cropped_name).replace("\\","/")
    cropped = image[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
    cv2.imwrite(cropped_path, cropped)

if __name__ == '__main__':
    # setup the mouse callback function
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)

    # loading images
    image_files = [os.path.join(INPUT_DIR, f).replace("\\","/") for f in os.listdir(INPUT_DIR) if f.endswith(('.jpg','.png'))]
    i = 0

    for image_path in image_files:
        i += 1
        print("Stage: {}".format(i))
        image = cv2.imread(image_path)
        clone = image.copy()

        # keep looping until the 'q' key is pressed
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", image)
            key = cv2.waitKey(1) & 0xFF

            # if the 'r' key is pressed, reset the cropping region
            if key == ord("r"):
            	image = clone.copy()

            # if the 'c' key is pressed, break from the loop
            elif key == ord("c"):
            	break

            # if the 's' key is pressed, create and save a corresponding mask and a corresponding cropped image
            elif key == ord("s"):
                create_crop(clone, image_path)
                print("Crop " + image_path.split('/')[-1][0:-4] + " saved")
                break

    # close all open windows
    cv2.destroyAllWindows()
