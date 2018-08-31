'''
    This file's main function reads all the images in the directory specified as INPUT_DIR in the dirs.py file
    or INPUT_DIR/../images_plus_ultra if it exists.
    Then, for each image, it automatically search the bounding box of the object of interest and crop the image
    according to the bonding box (bb).
        There are 2 methods for the bb search:
            The first one, search_bb_naive, requires that the object of interest is displayed in a monochrome background in the input images.
            The second one, search_bb, requires that you have a point cloud of the object of interest in the INPUT_DIR/../output folder.
                Which also means that you need to hav ran the SfM program beforehead, especially in order to have
                the correspondances_by_name.json file which is necessary for some of the following functions to run.
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
        .
    The refPt parameter that stores the bounding box information is used as follows:
        refPt = [[j_min, i_min], [j_max, i_max]]
            Where (i_min, j_min) are the pixel coordinates of the upper left point of the bounding box (height, width)
            and (i_max. j_max) the pixel coordinates of the bottom right point pf the bounding box (height, width).
'''

import os
import numpy as np
import cv2
import random
import math
import json
import time
import subprocess
import scipy.linalg as la
from plyfile import PlyData, PlyElement
from input_dir import INPUT_DIR
from ooi_dir import OOI_DIR

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
class automatic_cropator:
    def __init__(self, INPUT_DIR_=INPUT_DIR, OOI_DIR_=OOI_DIR):
        self.refPt = []
        self.cropping = False
        self.K = []
        self.PC = []
        self.D = []
        self.correspondances = []
        self.INPUT_DIR = INPUT_DIR_
        self.OOI_DIR = OOI_DIR_


    def distort_coordinates(self, point):
        '''
            This function takes a 1-dimension 3-coordinates (homogenous coordinates) numpy as input and
            applies the distortion coefficients to this point then return the result
        '''
        r2 = point[0]**2 + point[1]**2
        coeff = (1 + self.D[0]*r2 + self.D[1]*(r2**2) + self.D[4]*(r2**3))/(1 + self.D[5]*r2 + self.D[6]*(r2**2) + self.D[7]*(r2**3))
        point_distorted = [0,0,1]
        point_distorted[0] = point[0]*coeff + 2*self.D[2]*point[0]*point[1] + self.D[3]*(r2 + 2*point[0])
        point_distorted[1] = point[1]*coeff + 2*self.D[3]*point[0]*point[1] + self.D[2]*(r2 + 2*point[1])
        point_distorted = np.asarray(point_distorted)
        return point_distorted

    def handle_edges_in_bb(self, shape):
        '''
            This function assure that the coordinates of the bounding box in the refPt global variable
            do not excead the size of the image and stay positive (as everybody should, cause' positivity always win ;-) ).
        '''
        for i in range(2):
            for  j in range(2):
                self.refPt[i][j] = max(0, self.refPt[i][j])
                self.refPt[i][j] = min(self.refPt[i][j], shape[(j+1)%2])
        self.refPt = [(self.refPt[0][0],self.refPt[0][1]), (self.refPt[1][0],self.refPt[1][1])]

    def load_variables(self, obj_base_name="OOI_PC", extension='.obj', yml_dir=INPUT_DIR, json_path=(INPUT_DIR+"/../output/correspondances_by_name.json"), ooi_dir=OOI_DIR):
        '''
            This function loads the camera matrix, the distortion coefficients, the correspondances and the object of interest pointcloud
            into the global variables:
            K
            D
            correspondances
            PC
            The name and the extension of the object of interest can be specified
            The extension can be either obj or ply
            The pointcloud file needs to be in the folder INPUT_DIR/../output
        '''
        # Get the camera matrix distortion coefficient
        yaml_file = [os.path.join(yml_dir, f).replace("\\","/") for f in os.listdir(yml_dir) if f.endswith(('.yml', '.yaml'))][0]
        yaml_file = cv2.FileStorage(os.path.join(yml_dir, yaml_file).replace("\\","/"), cv2.FILE_STORAGE_READ)
        self.K = yaml_file.getNode("K").mat()
        self.D = yaml_file.getNode("D").mat()
        self.D = self.D[0].tolist()
        while len(self.D)<8:
            self.D.append(0)

        # Get the correspondances_by_name.json file's data
        with open(os.path.join(json_path).replace("\\","/"), encoding='utf-8') as json_file:
            self.correspondances = json.load(json_file)

        # Get the coordinates of the pointcloud of the tool
        input_path = os.path.join(ooi_dir, obj_base_name + extension).replace("\\","/")
        if input_path.endswith('ply'):
            with open(input_path, 'rb') as f:
                plydata = PlyData.read(f)
                PC_list = [[coord for coord in point][:3] + [1] for point in plydata['vertex']]
                self.PC = np.asarray(PC_list)
        else:
            with open(input_path) as f:
                PC_txt = f.read()
                PC_list = [[float(point) for point in point_str] + [1] for point_str in [point_txt.split(' ')[1:] for point_txt in PC_txt.splitlines()[13:] if point_txt[0] + point_txt[1] == 'v ']]
                self.PC = np.asarray(PC_list)



    def search_bb(self, image_name):
        '''
            This function computes the projection matrix for the pose corresponding to the specified image
            and applies this projectino to the point cloud in PC global variable.
            Then it uses the reprojected pointcloud to compute the bonding box of the object of interest in the specified image.
        '''
        # Get the camera translation and rotation
        R = np.array(self.correspondances[image_name]['rotation'])
        T = np.array([self.correspondances[image_name]['center']])

        # Compute the transformation matrix
        translation_part = np.concatenate((np.identity(3), -T.T), axis=1)
        translation_part = np.concatenate((translation_part, np.array([[0,0,0,1]])))
        rotation_part = np.concatenate((R, np.zeros((3,1))), axis=1)
        rotation_part = np.concatenate((rotation_part, np.array([[0,0,0,1]])))
        transform = np.matmul(rotation_part, translation_part)


        # Get 3D points in the frame of the camera
        points_in_camera_frame = np.matmul(transform, self.PC.T)[:3].T

        # Get 3D points homogenous coordinates in the camera frame
        points_in_camera_frame_homogenous = [[point[0]/point[2], point[1]/point[2], point[2]/point[2]] for point in points_in_camera_frame]
        points_in_camera_frame_homogenous = np.asarray(points_in_camera_frame_homogenous)

        # Distort coordinates
        points_in_camera_frame_homogenous_distorted = [self.distort_coordinates(point) for point in points_in_camera_frame_homogenous]
        points_in_camera_frame_homogenous_distorted = np.asarray(points_in_camera_frame_homogenous_distorted)

        # Project the points with the camera matrix
        points_projected = np.matmul(self.K, points_in_camera_frame_homogenous_distorted.T).T

        # Compute the bounding box based on the reprojection of the point cloud
        self.compute_bb_with_projected_points(points_projected)

        return points_projected


    def compute_bb_with_projected_points(self, points_projected, min_padding=10, max_padding=20):
        '''
            This function computes the bounding box around the specified projected points and sotres it in the refPt global variable
            and add a little random padding to it.
        '''
        #mask = np.zeros(shape,np.uint8)
        xs = points_projected[:, 0].tolist()
        ys = points_projected[:, 1].tolist()
        self.refPt = [[min(xs) - random.randint(min_padding, max_padding), min(ys) - random.randint(min_padding, max_padding)],[max(xs) + random.randint(min_padding, max_padding), max(ys) + random.randint(min_padding, max_padding)]]
        for i in range(2):
            for  j in range(2):
                self.refPt[i][j] = int(self.refPt[i][j])

    def is_bb_yolo_correct(self, min_height=300, min_width=300):
        '''
            Check if the bounding box is too small to used in yolo training
        '''
        if abs(self.refPt[0][0]-self.refPt[1][0])<min_width or abs(self.refPt[0][1]-self.refPt[1][1])<min_height:
            return False
        else:
            return True


    def create_crop(self, image, image_path):
        '''
            Function that creates a cropped image based on:
                the original image -> obviously useful to crop it
                the image path -> helpful for the path of the mask
            the function also relies on the global variable refPt that contains the information of the box mask for the current image
        '''
        cropped_dir = os.path.join(self.INPUT_DIR, "../output/cropped_images").replace("\\","/")
        if not os.path.exists(cropped_dir):
          os.mkdir(cropped_dir)
        cropped_name = image_path.split('/')[-1][0:-4] + "_cropped.png"
        cropped_path = os.path.join(cropped_dir, cropped_name).replace("\\","/")

        cropped = image[self.refPt[0][1]:self.refPt[1][1], self.refPt[0][0]:self.refPt[1][0]]
        cv2.imwrite(cropped_path, cropped)


    def create_bb(self, image_path, object_class="Yellow_tool"):
        '''
            This function stores the current bounding box in the refPt global variable into a txt file.
            The name of the file is the name of the corresponding image
            The file is stored in the directory INPUT_DIR/../output/bbs, that is created if non existant yet
        '''
        bb_dir = os.path.join(self.INPUT_DIR, "../output/bbs").replace("\\","/")
        if not os.path.exists(bb_dir):
          os.mkdir(bb_dir)
        bb_name = image_path.split('/')[-1][0:-4] + "_bb.txt"
        bb_path = os.path.join(bb_dir, bb_name).replace("\\","/")
        with open(bb_path, 'w') as f:
            f.write("{} {} {} {} {}".format(object_class ,self.refPt[0][0], self.refPt[0][1], self.refPt[1][0]-self.refPt[0][0], self.refPt[1][1]-self.refPt[0][1]))


    def do_cropping(self, image_path, nb_images, i, searching=False):
        '''
            This function looks if the current image has already been cropped,
            and if not it does the cropping of the current image.
            If the searching parameter is set to True then the function will use the search_bb_naive method to set the bounding box
            in the refPt global variable. Otherwise it will assume that the bounding box is already correctly stored in refPt.
        '''
        print("Start cropping of " + image_path.split('/')[-1][0:-4])
        cropped_name = image_path.split('/')[-1][0:-4] + "_cropped.png"
        cropped_dir = os.path.join(self.INPUT_DIR, "../output/cropped_images").replace("\\","/")
        cropped_path = os.path.join(cropped_dir, cropped_name).replace("\\","/")
        # Check if the image has already been cropped
        if not os.path.exists(cropped_path):
            image = cv2.imread(image_path)
            clone = image.copy()

            if searching:
                image2 = draw_edges(clone)
                self.search_bb_naive(image2)
                self.create_bb(image_path)
                print("BB " + image_path.split('/')[-1][0:-4] + " saved")

            if (self.refPt[0][1] == self.refPt[1][1]) or (self.refPt[0][0] == self.refPt[1][0]):
                print("The width or height of the bounding box is equals to 0, image ignored")
            else:
                self.create_crop(clone, image_path)
                print("Crop " + image_path.split('/')[-1][0:-4] + " saved")

            nb_star = math.floor(100*(i/nb_images))
            print('{}%'.format(nb_star))

            # Uncomment to visualize the bonding boxes
            #display_bb(clone)
        else:
            print("Stage: {}".format(i))
            print("Crop " + image_path.split('/')[-1][0:-4] + " already exists")



    def crop_images_using_bbs(self, bb_dir):
        '''
            Crop all the images in the input_dir using the bbs stored in the INPUT_DIR/../output/bbs directory.
        '''
        bb_files = [os.path.join(bb_dir, f).replace("\\","/") for f in os.listdir(bb_dir) if f.endswith('.txt')]
        if not os.path.exists(cropped_dir):
          os.mkdir(cropped_dir)

        i = 0
        nb_images = len(bb_files)
        for bb_file in bb_files:
            image_name = bb_file.split('/')[-1].split('.')[0][:-3]
            image_path = os.path.join(self.INPUT_DIR, image_name + '.jpg').replace("\\","/")
            if not os.path.exists(image_path):
                image_path = os.path.join(self.INPUT_DIR, image_name + '.png').replace("\\","/")
            with open(bb_file) as f:
                text = f.read()
                coordinates = text.split(',')
                self.refPt = []
                self.refPt.append((int(coordinates[0]), int(coordinates[1])))
                self.refPt.append((int(coordinates[2]), int(coordinates[3])))
            i += 1
            self.do_cropping(image_path, nb_images, i)


    def crop_images(self, save_bbs=True):
        '''
            Crop all the images in the input_dir using the search_bb method.
            If save_bbs is set to True it will also save the corresponding bounding boxes by adding them to the correspondances_by_name.json.
        '''
        # Set the image directory
        images_dir = self.INPUT_DIR
        if os.path.exists(os.path.join(self.INPUT_DIR, '../images_plus_ultra').replace("\\","/")):
            images_dir = os.path.join(self.INPUT_DIR, '../images_plus_ultra').replace("\\","/")


        # For every image referenced in the correspondances_by_name.json file
        nb_images = len(self.correspondances)
        i = 0
        for image_name in self.correspondances:
            # Search the bounding box
            self.search_bb(image_name)
            if not os.path.exists(os.path.join(self.INPUT_DIR, image_name).replace("\\","/")):
                image_name = image_name.split('.')[0] + '.png'
            # Load image
            image = cv2.imread(os.path.join(images_dir, image_name).replace("\\","/"))
            shape = image.shape

            # Adjust the bounding box to the image size
            self.handle_edges_in_bb(shape)

            # Visualize to see if the result is coherent
            #display_bb(image)

            # Crop
            image_path = os.path.join(images_dir, image_name).replace("\\","/")
            self.do_cropping(image_path, nb_images, i)
            if save_bbs:
                self.create_bb(image_path)

            # Increment the cropping progression
            i += 1
        print("Cropping finished")





    # /////////////////////////////  Debugging purpose  ///////////////////////////////

    def display_projection(self, points_projected, shape):
        '''
            This function displays the current bounding box on the current image.
            Mostly used for debugging purpose.
            What to do when keys are pressed needs to be manually specified in the code.
        '''
        cv2.namedWindow("image")
        # Uncomment for visualize the bounding boxes
        mask = np.zeros(shape,np.uint8)
        for point in points_projected:
            if 0<point[0]<1920 and 0<point[1]<1080:
                mask[int(point[1]), int(point[0])] = 255
                #print(point)
        kernel = np.ones((5,5), np.uint8)
        dilate = cv2.dilate(mask, kernel, iterations=1)
        closing = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel)
        closing = cv2.morphologyEx(closing, cv2.MORPH_CLOSE, kernel)
        # keep looping until the 'q' key is pressed
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", closing)
            key = cv2.waitKey(1) & 0xFF

            # if the 'c' key is pressed, break from the loop
            if key == ord("c"):
                break

            # if the 's' key is pressed, break from the loop
            elif key == ord("s"):
                break
        # close all open windows
        cv2.destroyAllWindows()


    def visualize_projection(self):
        '''
            Function to visualize the reprojection of the pointcloud
            Useful for debugging purpose
        '''

        images_dir = self.INPUT_DIR
        for image_name in self.correspondances:
            # Load image
            image = cv2.imread(os.path.join(images_dir, image_name).replace("\\","/"))
            shape = image.shape
            points_projected = self.search_bb(image_name)
            image_path = os.path.join(images_dir, image_name).replace("\\","/")
            print(image_name)
            self.display_projection(points_projected, shape)

    def display_bb(self, clone):
        '''
            This function displays the current bounding box on the current image.
            Mostly used for debugging purpose.
            What to do when keys are pressed needs to be manually specified in the code.
        '''
        cv2.namedWindow("image")
        # Uncomment for visualize the bounding boxes
        cv2.rectangle(clone, self.refPt[0], self.refPt[1], (0, 255, 0), 2)

        # keep looping until the 'q' key is pressed
        while True:
            # display the image and wait for a keypress
            cv2.imshow("image", clone)
            key = cv2.waitKey(1) & 0xFF

            # if the 'c' key is pressed, break from the loop
            if key == ord("c"):
                break

            # if the 's' key is pressed, break from the loop
            elif key == ord("s"):
                break
        # close all open windows
        cv2.destroyAllWindows()

    def create_obj_file_from_array(self, points, file_base_name='Test'):
        '''
            This function takes array as input. This array should have n lines and 3 columns as it
            represents a set of 3D points (a pointcloud).
            Then a obj file corresponding to this pointcloud is created in the INPUT_DIR/../output directory.
            The name of the created file can be specified, Test by default.
            This function has been created for debugging purpose and designed to be called within search_bb function
        '''
        txt = ""
        for point in points:
            txt += "v {} {} {}\n".format(point[0], point[1], point[2])
        with open(os.path.join(self.INPUT_DIR, '../output/'+ file_base_name + '.obj').replace("\\","/"), 'w') as f:
            f.write(txt)

    # /////////////////////////////////////////////////////////////////////////////////


if __name__ == '__main__':

    output_dir = os.path.join(INPUT_DIR, "../output").replace("\\","/")
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)

    print("Starting automatic cropping")
    start_time = time.time()
    Croper = automatic_cropator()
    Croper.load_variables(obj_base_name="OOI_original")
    Croper.crop_images(for_yolo=True)

    pResize = subprocess.Popen( ["python", "resize_cropped_images.py"])
    pResize.wait()

    duration = (time.time() - start_time)/60
    print("Automatic cropping is over after ", duration, " minutes")
