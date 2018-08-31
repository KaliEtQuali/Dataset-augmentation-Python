'''
    This script look for a mp4 file in the folde specified as VIDEO_DIR in dirs.py
    Then it extracts all the frames of this video into the folder VIDEO_DIR/images and set this folder as INPUT_DIR
    in order to prepare the use of select_for_SfM.py
'''
import numpy as np
import os
import cv2
from dirs import VIDEO_DIR


def save_frames(video_dir=VIDEO_DIR, video_base_name="vid", image_base_name="frame"):
    '''
        This function saves the frames of a mp4 video file
    '''
    output_dir = os.path.join(video_dir, 'images').replace("\\","/")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

        vidcap = cv2.VideoCapture(os.path.join(video_dir, video_base_name + '.mp4'))
        success,image = vidcap.read()
        count = 0
        while success:
          cv2.imwrite(os.path.join(output_dir, image_base_name + "{}.jpg".format(count)).replace("\\","/"), image)     # save frame as JPEG file
          success,image = vidcap.read()
          print('Read frame number {}: '.format(count), success)
          count += 1
    else:
        print("frames already extracted")

if __name__ == '__main__':
    video_path = [os.path.join(VIDEO_DIR, f).replace("\\","/") for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')][0]
    video_base_name = video_path.split('/')[-1].split('.')[0]
    save_frames(video_base_name=video_base_name)
    # Specify the INPUT_DIR as the directory in which we just saved the frames of the video
    with open("./input_dir.py", 'w') as f:
        f.write("INPUT_DIR = \"{}\"".format(os.path.join(VIDEO_DIR, 'images')))
