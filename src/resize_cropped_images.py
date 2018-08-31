'''
    This file's main function searchs for all the cropped images corresponding to the directory specified as INPUT_DIR in the dirs.py file
    It will resize each images according to the specified square_size
        For the resizing not to deform the image, the function will add a padding before resizing to form a square image
        The color of the padding is specified as the padding_color tuple
'''


import os
import numpy as np
import cv2
from input_dir import INPUT_DIR

cropped_dir = os.path.join(INPUT_DIR, "../output/cropped_images").replace("\\","/")
cropped_resized_dir = os.path.join(cropped_dir, "resized").replace("\\","/")
if not os.path.exists(cropped_resized_dir):
  os.mkdir(cropped_resized_dir)

square_size = 277
padding_color = (128,128, 128)

def show_image(image):
    cv2.namedWindow("image")
    while True:
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF

        # if the 'r' key is pressed, move on to the next image
        if key == ord("r"):
            break

if __name__ == '__main__':
    print("Begin resizing cropped images")
    for item in os.listdir(cropped_dir):
        if os.path.isfile(os.path.join(cropped_dir, item).replace("\\","/")):
            file_name = item
            image_path = os.path.join(cropped_dir, file_name).replace("\\","/")
            image = cv2.imread(image_path)
            clone = image.copy()
            height = image.shape[0]
            width = image.shape[1]
            if height>width:
                square_image = np.zeros((height, height),np.uint8)
                square_image = cv2.copyMakeBorder( image, 0, 0, (height-width)//2, (height-width)//2+(height-width)%2, cv2.BORDER_CONSTANT,value=padding_color)
                square_image = cv2.resize(square_image, (square_size,square_size))
            elif height<width:
                square_image = np.zeros((width, width),np.uint8)
                square_image = cv2.copyMakeBorder( image, (width-height)//2, (width-height)//2+(width-height)%2, 0, 0, cv2.BORDER_CONSTANT,value=padding_color)
                square_image = cv2.resize(square_image, (square_size,square_size))
            resized_path = os.path.join(cropped_resized_dir, file_name.split('_')[0] + '.png').replace("\\","/")
            cv2.imwrite(resized_path, square_image)
            print("Resized image {} saved".format(file_name.split('_')[0] + '.png'))
            #show_image(square_image)
    print("Resizing finished")
