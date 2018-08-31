'''
    This file creates json files based with the rotations output from the SfM pipeline but supposingly in the frame of the aruco markers
    This is an attempt to align the point cloud from SfM to the one from aruco markers, but it kinda failed
    The only usage of this file is to compare the accuracy of the Sfm to the aruco markers' one
        Since it has been done on May 2nd 2018 this file should not be used anymore
            But since nobody knows what the future is made of I keep it just in case
'''

import os
import json
import numpy as np
import pprint
from input_dir import INPUT_DIR
import cv2
pp = pprint.PrettyPrinter(indent=2)


input_dir = os.path.join(INPUT_DIR, "../output")
output_dir = input_dir

json_file_name = "correspondances.json"
initial_pose_file_name = "initial_pose.txt"

# Load json correspondences file
with open(os.path.join(input_dir, json_file_name), encoding='utf-8') as json_file:
    correspondances = json.load(json_file)

# Load first pose of aruco markers images
with open(os.path.join(input_dir, initial_pose_file_name), encoding='utf-8') as f:
    initial_pose = f.readlines()
    initial_pose = [x.strip() for x in initial_pose]

# Construct rotation matrix corresponding to the first pose of aruco marker images
vector_pose = []
for angle in initial_pose:
    vector_pose.append(float(angle))
vector_pose = np.asarray(vector_pose)
rotation_mat_aruco = np.zeros((3,3))
cv2.Rodrigues(vector_pose, rotation_mat_aruco)

# Construct the matrix that changes SfM axis into aruco axis
rotation_mat_sfm = []
for line in correspondances[0]["pose"]["rotation"]:
    rotation_mat_sfm.append(line)
rotation_mat_sfm = np.asarray(rotation_mat_sfm)
change_axis_matrix = np.matmul(rotation_mat_aruco, np.linalg.inv(rotation_mat_sfm))

# Apply this matrix to every rotation matrix in correspondances.json
axis_angles = []
for view in correspondances:
    new_rot = np.matmul(change_axis_matrix, view["pose"]["rotation"])
    axis_angle = np.zeros((3,1))
    cv2.Rodrigues(new_rot, axis_angle)
    axis_angles.append({"image": view["image"], "angles":axis_angle.tolist()})
    view["pose"]["rotation"] = new_rot.tolist()

# Write these new poses in a aruco_correspondances.json file
with open(os.path.join(output_dir, 'aruco_correspondances.json'), 'w') as outfile:
    json.dump(correspondances, outfile)

with open(os.path.join(output_dir, 'axis_angles.json'), 'w') as outfile:
    json.dump(axis_angles, outfile)


print("over")
