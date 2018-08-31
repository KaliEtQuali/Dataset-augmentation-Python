'''
    This file creates pcd files based on the output of the Sfm pipeline and the output of the pose recovering with markers
    The only usage of this file is to compare the accuracy of the Sfm to the aruco markers' one
        Since it has been done on May 2nd 2018 this file should not be used anymore
            But since nobody knows what the future is made of I keep it just in case
'''


import os
import sys
sys.path.insert(0,'..')
import json
import numpy as np
from input_dir import INPUT_DIR
import pprint
import cv2
pp = pprint.PrettyPrinter(indent=2)


input_path = os.path.join(INPUT_DIR, "../correspondances_by_name.json")
output_path = os.path.join(INPUT_DIR, "..")
aruco_poses_dir = os.path.join(INPUT_DIR, "../../../ArucoResults/extrinsic_t")
aruco_rotations_dir = os.path.join(INPUT_DIR, "../../../ArucoResults/extrinsic")

pcd_file_name = "camera_poses.pcd"

header_string = "# .PCD v.7 - Point Cloud Data file format\nVERSION .7\nFIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F F\nCOUNT 1 1 1 1\nWIDTH {}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {}\nDATA ascii\n"

X_sfm = []
X_aruco = []

def from_extrinsic_t_to_pose(base_file_name, is_R_returned):
    t_path = os.path.join(aruco_poses_dir, base_file_name)
    angles_path = os.path.join(aruco_rotations_dir, base_file_name)
    # Read translation file
    with open(t_path) as t_file:
        t = t_file.read()
    # Convert translation file to float array
    t = t.split(" ")[1:]
    for i in range(3):
        t[i] = float(t[i].rstrip())
    # Read rotation file
    with open(angles_path) as angles_file:
        angles = angles_file.readlines()
        angles = [x.strip() for x in angles]
    # Convert rotation file to rotation matrix
    vector_pose = []
    for angle in angles:
        vector_pose.append(float(angle))
    vector_pose = np.asarray(vector_pose)
    R = np.zeros((3,3))
    cv2.Rodrigues(vector_pose, R)
    # Convert translations from the file to real camera translations
    real_t = np.matmul(1*np.linalg.inv(R), [-1*t2 for t2 in t])
    if is_R_returned:
        return real_t, R
    else:
        return real_t

with open(input_path, encoding='utf-8') as json_file:
    correspondances = json.load(json_file)

# read correspondances.json file extrinsic_t file and angles file and store Rs and ts from both sfm and markers in:
    # X_sfm variable, sfm_poses_pcd_file and R_sfm_file
    # X_aruco, aruco_poses_pcd_file and R_aruco_file
with open(os.path.join(output_path, "sfm_camera_poses2.pcd"), 'w') as sfm_poses_pcd_file:
    with open(os.path.join(output_path, "aruco_camera2_poses.pcd"), 'w') as aruco_poses_pcd_file:
        with open(os.path.join(output_path, "aruco_Rs2.txt"), 'w') as R_aruco_file:
            with open(os.path.join(output_path, "sfm_Rs2.txt"), 'w') as R_sfm_file:
                for (root_dir, dir_names, file_names) in os.walk(aruco_poses_dir):
                    header = header_string.format(len(file_names), len(file_names))
                    aruco_poses_pcd_file.write(header)
                    sfm_poses_pcd_file.write(header)
                    for file_name in file_names:
                        t , R_aruco = from_extrinsic_t_to_pose(file_name,1)
                        R_aruco = R_aruco.flatten()
                        aruco_poses_pcd_file.write("{} {} {} {}\n".format(t[0], t[1], t[2], 4.2108e+06))
                        R_aruco_file.write("{} {} {} {} {} {} {} {} {}\n".format(R_aruco[0], R_aruco[1], R_aruco[2], R_aruco[3], R_aruco[4], R_aruco[5], R_aruco[6], R_aruco[7], R_aruco[8]))
                        X_aruco.append([t[0], t[1], t[2]])

                        pose = correspondances[file_name.split('.')[0] + '.jpg']["center"]
                        rot = np.asarray(correspondances[file_name.split('.')[0] + '.jpg']["rotation"]).flatten()
                        sfm_poses_pcd_file.write("{} {} {} {}\n".format(pose[0], pose[1], pose[2], 4.808e+06))
                        R_sfm_file.write("{} {} {} {} {} {} {} {} {}\n".format(rot[0], rot[1], rot[2], rot[3], rot[4], rot[5], rot[6], rot[7], rot[8]))
                        X_sfm.append([pose[0], pose[1], pose[2]])
'''
# Compute transformations form sfm to markers and reverse
X_aruco = np.asarray(X_aruco)
X_sfm = np.asarray(X_sfm)

transform = np.matmul(np.linalg.pinv(X_aruco), X_sfm)
transform2 = np.matmul(np.linalg.pinv(X_sfm), X_aruco)

X_aruco_transformed = np.matmul(X_aruco, transform)
X_sfm_transformed = np.matmul(X_sfm, transform2)


with open(os.path.join(output_path, "sfm_camera_poses_transformed.pcd"), 'w') as sfm_poses_transformed_pcd_file:
    header = header_string.format(len(file_names), len(file_names))
    sfm_poses_transformed_pcd_file.write(header)
    for i in range(len(X_sfm_transformed)):
        sfm_poses_transformed_pcd_file.write("{} {} {} {}\n".format(X_sfm_transformed[i][0], X_sfm_transformed[i][1], X_sfm_transformed[i][2], 4.808e+06))

with open(os.path.join(output_path, "aruco_camera_poses_transformed.pcd"), 'w') as aruco_poses_transformed_pcd_file:
    header = header_string.format(len(file_names), len(file_names))
    aruco_poses_transformed_pcd_file.write(header)
    for i in range(len(X_aruco_transformed)):
        aruco_poses_transformed_pcd_file.write("{} {} {} {}\n".format(X_aruco_transformed[i][0], X_aruco_transformed[i][1], X_aruco_transformed[i][2], 4.2108e+06))


with open(os.path.join(output_path, "aruco_Rs.txt"), 'w') as R_aruco_file:
    for (root_dir, dir_names, file_names) in os.walk(aruco_poses_dir):
        for file_name in file_names:
            t, R_aruco = from_extrinsic_t_to_pose(file_name,1)
            R_aruco = np.matmul(R_aruco, transform)
            R_aruco = R_aruco.flatten()
            R_aruco_file.write("{} {} {} {} {} {} {} {} {}\n".format(R_aruco[0], R_aruco[1], R_aruco[2], R_aruco[3], R_aruco[4], R_aruco[5], R_aruco[6], R_aruco[7], R_aruco[8]))
'''
