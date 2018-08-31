import numpy as np
import os
import cv2


filename = './video.avi'
frames_per_second = 24
res = '720p'
print(cv2.__version__)
# Set resolution for the video capture
# Function adapted from https://kirr.co/0l6qmh
def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)

# Standard Video Dimensions Sizes
STD_DIMENSIONS =  {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}


# grab resolution dimensions and set video capture to it.
def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width,height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(cap, width, height)
    return width, height

# Video Encoding, might require additional installs
# Types of Codes: http://www.fourcc.org/codecs.php
VIDEO_TYPE = {
    #'avi': cv2.VideoWriter_fourcc(*'XVID'),
    #'mp4': cv2.VideoWriter_fourcc(*'H264'),
    #'mp4': cv2.VideoWriter_fourcc(*'XVID'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
    'avi': cv2.VideoWriter_fourcc(*'XVID')
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
      return  VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']


def take():
    cap = cv2.VideoCapture(0)
    out = cv2.VideoWriter(filename, get_video_type(filename), frames_per_second, get_dims(cap, res))

    while True:
        ret, frame = cap.read()
        #out.write(frame)
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    out.release()
    cv2.destroyAllWindows()

def save_frames():
    vidcap = cv2.VideoCapture('../vid.mp4')
    success,image = vidcap.read()
    count = 0
    while success:
      cv2.imwrite("../test/frame%d.jpg" % count, image)     # save frame as JPEG file
      success,image = vidcap.read()
      print('Read a new frame: ', success)
      count += 1

if __name__ == '__main__':
    save_frames()
