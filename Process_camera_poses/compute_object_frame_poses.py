'''
    This file's functions are useful for moving a set of camera poses from the SfM frame to the actual object frame (or any other frame actually)
'''


import numpy as np
import json
import os
import pprint
pp = pprint.PrettyPrinter(indent=2)

POSES_DIR = '/home/hpc/StructureFromMotion/OpenMVG_OpenMVS/LogicoolSmallTool3/output'
CORRESPONDANCES_JSON_PATH = os.path.join(POSES_DIR, 'correspondances_by_name.json')

def compute_new_axis(origin, up_point, forward_point):
    '''
        This function computes the X, Y and Z axiz defined by the given origin point, upward point and forward point
            The direction origin -> upward is assumed to be the Z axis
            The direction origin -> is assumed to be the X axis
            The Y axis is computed by cross-product between Z-axis and X-axis
    '''
    new_Z = (up_point - origin)/np.linalg.norm(up_point - origin)
    x_direction = (forward_point - origin)/np.linalg.norm(forward_point - origin)
    x_direction = x_direction - np.dot(x_direction, np.transpose(new_Z))*new_Z
    new_X = x_direction/np.linalg.norm(x_direction)
    new_Y = np.cross(new_Z, new_X)
    return [new_X, new_Y, new_Z]


def compute_tranfomation_mat(origin, up_point, forward_point):
    '''
        Given three 3D points this fuction return the tranformation matrix to apply in order
        to go from the initial frame to the frame defined by these 3 points
    '''
    # First compute the coordinates of the new x, y, and z  axis in the current frame
    axis_list = compute_new_axis(origin, up_point, forward_point)
    new_X = axis_list[0]
    new_Y = axis_list[1]
    new_Z = axis_list[2]
    # Construct the rotation matrix
    Rot = np.transpose(np.array([new_X, new_Y, new_Z]))
    #print('Rot: ', Rot)
    # Construct the transformation matrix to apply
    T = np.transpose(np.array([new_X.tolist()[0] + [0], new_Y.tolist()[0] + [0], new_Z.tolist()[0] + [0], ((1)*origin).tolist()[0] + [1]]))
    T = np.linalg.inv(T)
    #print('T: ', T)
    return T


def homogeneous(line_vector):
    '''
        This function takes an array or list as input and return the homogeneous eauivalent
    '''
    if type(line_vector) == np.ndarray:
        return np.array(line_vector.tolist()[0] + [1])
    elif type(line_vector) == list:
        return line_vector + [1]


def transform_poses(T):
    '''
        This function takes an array T as input that corresponds to a 4x4 transformation matrix and create
        a json file with the transformed locations
    '''

    ## Get the initial camera poses in correspondances_by_name.json
    with open(CORRESPONDANCES_JSON_PATH, encoding='utf-8') as json_file:
        correspondances = json.load(json_file)
    ## For each image/pose compute the transformed pose and replace the initial pose by the transformed one in the correspondances dict
        # To do that it apply th transformation T to the position and the multiply the rotation part of the transformation T to the rotation
    # And create a new json with the object pose in the frame of the camera
        # To do that it does the same as before to the poses in the object frame with a transformation
    correspondances_camera_frame = {}
    for image in correspondances:
        ## Compute the camera poses in the frame of the object
        # Camera pose in the object frame is computed by applying transformation T to its pose in the initial frame
        correspondances[image]['center'] = np.matmul(T, np.asarray(homogeneous(correspondances[image]['center']))).tolist()[:3]
        # Rotation in the frame of the object is computed by applying the rotation extracted from the transformation to the rotation
        # of the camera in the initial frame
        correspondances[image]['rotation'] = np.matmul(T[np.ix_([0,1,2],[0,1,2])], np.asarray(correspondances[image]['rotation'])).tolist()
        # Store the so used transformation for eventual future use
        correspondances[image]['transform'] = T.tolist()

        ## Compute the the object frame in the frame of the cameras
        # Transform to camera frame computed based on its position in the object frame and the column vector defined by the rotation
        # matrix in the object frame
        T_to_camera_frame = compute_tranfomation_mat(np.asarray([correspondances[image]['center']]),
            np.asarray(correspondances[image]['rotation'])[np.ix_([0,1,2],[2])].transpose(),
            np.asarray(correspondances[image]['rotation'])[np.ix_([0,1,2],[0])].transpose()
            )
        correspondances_camera_frame[image] = {}
        # Object in the frame of the camera is the transformation of (0,0,0) in the object frame
        correspondances_camera_frame[image]['center'] = np.matmul(T_to_camera_frame, homogeneous(np.zeros((1,3))).transpose()).tolist()[:3]
        # The rotation is extracted from the transformation matrix itself
        correspondances_camera_frame[image]['rotation'] = T_to_camera_frame[np.ix_([0,1,2],[0,1,2])].tolist()
        # Store the transformation used for possible future use
        correspondances_camera_frame[image]['transform'] = T_to_camera_frame.tolist()

    ## Finally store these transformed poses in a new json file
    with open(os.path.join(POSES_DIR, 'correspondances_centers_transformed_to_object_frame.json'), 'w') as new_json_file:
        json.dump(correspondances, new_json_file)
    print("A new json file (correspondances_centers_transformed_to_object_frame.json) has been created in the directory specified as POSES_DIR")
    with open(os.path.join(POSES_DIR, 'object_poses_in_cameras_frames.json'), 'w') as new_json_file:
        json.dump(correspondances_camera_frame, new_json_file)
    print("A new json file (object_poses_in_cameras_frames.json) has been created in the directory specified as POSES_DIR")



def create_pcd_file():
    '''
        This function creates one pcd file that contains both the initial poses and the transformed ones
        To do that it needs both correspondances_by_name.json and correspondances_centers_transformed_to_object_frame.json
        So this function will work only if transform_poses(T) has been called at least once
    '''

    # Get the initial and transformed poses
    with open(CORRESPONDANCES_JSON_PATH, encoding='utf-8') as json_file:
        correspondances = json.load(json_file)
    with open(os.path.join(POSES_DIR, 'correspondances_centers_transformed_to_object_frame.json'), encoding='utf-8') as json_file:
        transformed_correspondances = json.load(json_file)
    # Set the header of the pcd file
    header_string = "# .PCD v.7 - Point Cloud Data file format\nVERSION .7\nFIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F F\nCOUNT 1 1 1 1\nWIDTH {}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {}\nDATA ascii\n"
    header = header_string.format(len(correspondances)*2, len(correspondances)*2)
    # For each image write the poses in the pcd file
    with open(os.path.join(POSES_DIR, 'poses_in_initial_and_object_frames2_t_inverted_plus_new_origin.pcd'), 'w') as pcd_file:
        pcd_file.write(header)
        for image in correspondances:
            t = correspondances[image]['center']
            pcd_file.write("{} {} {} {}\n".format(t[0], t[1], t[2], 4.2108e+06))
            transformed_t = transformed_correspondances[image]['center']
            pcd_file.write("{} {} {} {}\n".format(transformed_t[0], transformed_t[1], transformed_t[2], 4.808e+06))

        # just for testing by visualizing the axis
        origin = np.array([[-1.448722,-0.908291,6.824848]])
        up_point = np.array([[-1.001757,-2.184740,6.073571]])
        forward_point = np.array([[0.040013,0.792806,8.239107]])
        ts = compute_new_axis(origin, up_point, forward_point)
        for t in ts:
            t = t.tolist()[0]
            pcd_file.write("{} {} {} {}\n".format(t[0]+origin.tolist()[0][0], t[1]+origin.tolist()[0][1], t[2]+origin.tolist()[0][2], 5.2108e+06))
        pcd_file.write("{} {} {} {}\n".format(origin.tolist()[0][0], origin.tolist()[0][1], origin.tolist()[0][2], 5.2108e+06))
    print("A new pcd file (poses_in_initial_and_object_frames.pcd) has been created in the directory specified as POSES_DIR")


def apply_transformation_to_pcd(pcd_path, T, output_dir, output_name):
    '''
        This function apply a transformation T to the coordinates in the pcd file whom path is specified as pcd_path
        It creates a pcd file with the so generated point cloud and store in the directory specified as output_dir with name output_name
    '''
    ## Store all the coordinates of the pcd file in an numpy array
    # Read the file as a list of lines
    with open(pcd_path) as pcd_file:
        pcd_file_txt = pcd_file.readlines()
    # The 11 first lines are just a header so transform the other lines in a list of float that we store into a list pointcloud_list
    pointcloud_list = []
    for i in range(11,len(pcd_file_txt)):
        pointcloud_list.append([float(x) for x in pcd_file_txt[i].split(" ")[:3]])
    # Let this list be a list of homogenous coordinates vector, to facilitate further multiplication with the transformation matrix
    pointcloud_list = [homogeneous(x) for x in pointcloud_list]
    # Create a numpy array based on this list in order to easili\y perform matmul later on
    pointcloud_array = np.asarray(pointcloud_list).transpose()
    ## Apply the transformation by performing matrix multiplication
    pointcloud_transformed= np.matmul(T, pointcloud_array).transpose().tolist()
    ## Set the header of the pcd file
    header_string = "# .PCD v.7 - Point Cloud Data file format\nVERSION .7\nFIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F F\nCOUNT 1 1 1 1\nWIDTH {}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {}\nDATA ascii\n"
    header = header_string.format(len(pointcloud_transformed), len(pointcloud_transformed))
    ## Write the pcd file
    with open(os.path.join(output_dir, output_name), 'w') as pcd_transformed_file:
        pcd_transformed_file.write(header)
        for point in pointcloud_transformed:
            pcd_transformed_file.write("{} {} {} {}\n".format(point[0], point[1], point[2], 4.808e+06))
    print('PCD file saved at: ', os.path.join(output_dir, output_name))


def create_camera_frame_pcd_files(json_dir, pcd_path):
    '''
        This function reads the file object_poses_in_cameras_frames.json
        For each image it takes the transformation from the object frame to the frame of the corresponding camera pose
        and transform the whole point cloud in the frame of this corresponding camera, the result is stored in a pcd file
    '''
    # Read the object_poses_in_cameras_frames.json file
    with open(os.path.join(json_dir, 'object_poses_in_cameras_frames.json')) as file:
        json_file = json.load(file)
    # For each image extract the transformation, define an output_name and an output_dir and use apply_transformation_to_pcd function
    output_dir = os.path.join(POSES_DIR, 'camera_frames_pointclouds')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for image_name in json_file:
        print('Processing view of {}'.format(image_name))
        image_obj = json_file[image_name]
        T = image_obj['transform']
        T = np.asarray(T)
        output_name = image_name.split('.')[0] + '_pointcloud.pcd'
        apply_transformation_to_pcd(pcd_path, T, output_dir, output_name)
        print('\n')




def test():
    origin = np.array([[-1.448722,-0.908291,6.824848]])
    up_point = np.array([[-1.001757,-2.184740,6.073571]])
    forward_point = np.array([[0.040013,0.792806,8.239107]])
    T = compute_tranfomation_mat(origin, up_point, forward_point)
    print(T[np.ix_([0,1,2],[0,1,2])])

def run():
    '''
        Take the origin point, up point and forward point. Based on that compute the corresponding transformation matrice
        Transform the poses in the file specified as CORRESPONDANCES_JSON_PATH
            This will create new json files
        Create a corresponding pcd file to visualize the transformations with Point Cloud Library latter on
        But it can also do whatever the heck you want >=)
    '''
    origin = np.array([[-1.448722,-0.908291,6.824848]])
    up_point = np.array([[-1.001757,-2.184740,6.073571]])
    forward_point = np.array([[0.040013,0.792806,8.239107]])
    T = compute_tranfomation_mat(origin, up_point, forward_point)
    #transform_poses(T)
    #create_pcd_file()
    #apply_transformation_to_pcd(os.path.join(POSES_DIR, 'pointcloud.pcd'), T, POSES_DIR, 'pointcloud_object_frame.pcd')
    create_camera_frame_pcd_files(POSES_DIR, os.path.join(POSES_DIR, 'pointcloud_object_frame.pcd'))



if __name__ == '__main__':
    #test()
    run()
