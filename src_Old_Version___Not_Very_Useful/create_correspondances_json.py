'''
    The execution of this file will read the views_n_extrinsics json file output by the SfM pipeline
    Based on this json it will then create the correspondances_by_name.json
    This file associates images' name to the corresponding 3D location
    The final json looks like the following:
        {
            'image_name1': {
                'center': [x,y,z],
                'rotation':[[r11,r12,r13],
                            [r21,r22,r23],
                            [r31,r32,r33]
                            ],
                'angles': [angleX, angleY, angleZ]
            },
            'image_name2':{
                ...
            },
            ...
        }
'''

import os
import subprocess
import sys
import json
import numpy as np
import cv2
import pprint
from input_dir import INPUT_DIR
pp = pprint.PrettyPrinter(indent=2)

if len(sys.argv) == 1:
    input_dir = os.path.join(INPUT_DIR, '../output/OpenMVG/reconstruction_sequential')
    output_dir = os.path.join(INPUT_DIR, '../output')
else:
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]


json_file_name = "views_n_extrinsics.json"


def from_R_to_angles(R):
    # Compute an axis angles vector from a 3x3 rotation matrix R
    R = np.asarray(R)
    angles = np.zeros((1,3))
    angles = cv2.Rodrigues(R)[0]
    return angles.tolist()

# Load the views_n_extrinsics json
with open(os.path.join(input_dir, json_file_name), encoding='utf-8') as json_file:
    views_n_extrinsics = json.load(json_file)

correspondances = {}
n = len(views_n_extrinsics['views'])
m = len(views_n_extrinsics['extrinsics'])
# If the number of views differs from the number of extrinsics then some went wrong, cannot continue
if m != n:
    print('The number of views ({}) and number of extrinsics ({}) are not equal'.format(n,m))

for i in range(m):
    index_view = views_n_extrinsics['extrinsics'][i]["key"]
    # Get the image file name
    image = views_n_extrinsics['views'][index_view]['value']['ptr_wrapper']['data']["filename"]
    # Get the corresponding pose (rotation matrix and translation vector)
    pose = views_n_extrinsics['extrinsics'][i]['value']
    # Add the rotation in axis angle format to the pose object
    pose['angles'] = from_R_to_angles(pose['rotation'])
    # Store this object in the correspondances dict variable
    correspondances[image] = pose

# Print the correspondances dict for quick checks
pp.pprint(correspondances)
# Store the correspondances dict object in a json file named correspondances_by_name.json
with open(os.path.join(output_dir, 'correspondances_by_name.json'), 'w') as outfile:
    json.dump(correspondances, outfile)
