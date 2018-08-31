'''
    This file contains functions that were meant to be used only once or twice but that are practical enough to be kept just in case
'''

import numpy as np
import cv2
import os
import json
from shutil import copyfile
from input_dir import INPUT_DIR


def really_apply_masks():
    output_dir = os.path.join(INPUT_DIR, '../masked').replace("\\","/")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for (root_dir, dir_names, file_names) in os.walk(INPUT_DIR):
        nb_jpg = 0
        nb_png = 0
        for file_name in file_names:
            if file_name.endswith('.jpg'):

                image = cv2.imread(os.path.join(INPUT_DIR, file_name).replace("\\","/"))
                mask = cv2.imread(os.path.join(INPUT_DIR, file_name.split('.')[0] + '_mask.png').replace("\\","/"), 0)
                masked_image = cv2.bitwise_and(image,image,mask = mask)
                print(file_name)
                cv2.imwrite(os.path.join(output_dir, file_name.split('.')[0] + '_masked.jpg').replace("\\","/"), masked_image)
                while nb_jpg == 50:
                    # display the image and wait for a keypress
                    cv2.imshow("image", masked_image)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("c"):
                    	break
                '''
                nb_jpg+=1
                if os.path.exists(os.path.join(INPUT_DIR, file_name.split('.')[0] + '_mask.png')):
                    print('{} is masked'.format(file_name))
                else:
                    print('{} is not not not masked'.format(file_name))
            if file_name.endswith('.png'):
                nb_png+=1
        print('JPG: {}'.format(nb_jpg))
        print('PNG: {}'.format(nb_png))
                '''

def get_aruco_infos():
    ts_dir = '/home/hpc/StructureFromMotion/OpenMVG_OpenMVS/Comparing2/extrinsic_t/carpet/vertical/left'
    output_dir = '/home/hpc/StructureFromMotion/OpenMVG_OpenMVS/Comparing2'
    for (root_dir, dir_names, file_names) in os.walk(ts_dir):
        #with open(os.path.join(output_dir, 'aruco_ts.txt'))
        for file_name in file_names:
            with open(os.path.join(ts_dir, file_name).replace("\\","/")) as f:
                content = f.readlines()
                # you may also want to remove whitespace characters like `\n` at the end of each line
                content = [x.strip() for x in content]
            print(content)


def create_ts_n_Rs():
    input_path = os.path.join(INPUT_DIR, "../output/correspondances_by_name.json")
    output_path = os.path.join(INPUT_DIR, "../output/")

    X_sfm = []

    with open(input_path, encoding='utf-8') as json_file:
        correspondances = json.load(json_file)

    with open(os.path.join(output_path, "sfm_camera_poses.txt"), 'w') as t_sfm_file:
        with open(os.path.join(output_path, "sfm_Rs.txt"), 'w') as R_sfm_file:
            for file_name in correspondances:
                pose = correspondances[file_name]["center"]
                rot = np.asarray(correspondances[file_name]["rotation"]).flatten()
                t_sfm_file.write("{} {} {} {}\n".format(pose[0], pose[1], pose[2], 4.808e+06))
                R_sfm_file.write("{} {} {} {} {} {} {} {} {}\n".format(rot[0], rot[1], rot[2], rot[3], rot[4], rot[5], rot[6], rot[7], rot[8]))

def bestize_me(name=None):
    '''
        This function simply remind you that you are the best just to cheer you up and to boost your motivation
    '''
    if name:
        print("{} is the BEST!!!!".format(name))
    else:
        print("You are the BEST!!!!")


def unite_gan_images():
    output_dir = os.path.join(INPUT_DIR, 'all_images')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)


    for x in next(os.walk(INPUT_DIR))[1]:
        if x != 'all_images':
            path = os.path.join(INPUT_DIR, x, 'test_latest/images')
            image_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('fake_B.jpg','fake_B.png'))]
            for image_path in image_files:
                image = cv2.imread(image_path)
                image_name = image_path.split('/')[-1]
                output_path = os.path.join(output_dir, image_name)
                cv2.imwrite(output_path, image)
                print('File {} moved'.format(image_name))
            try:
                shutil.rmtree(path)
                print('Folder {} removed'.format(path))
            except (OSError, e):
                print ("Error: %s - %s." % (e.filename, e.strerror))



def adapt_bounding_boxes(object_class="Yellow_tool"):
    bb_dir = os.path.join(INPUT_DIR, "../output/bbs").replace("\\","/")
    bb_files = [os.path.join(bb_dir, f).replace("\\","/") for f in os.listdir(bb_dir) if f.endswith('.txt')]

    bb_dir2 = os.path.join(INPUT_DIR, "../output/bbs_for_yolo").replace("\\","/")
    if not os.path.exists(bb_dir2):
        os.mkdir(bb_dir2)

    i = 0
    nb_images = len(bb_files)
    for bb_file in bb_files:
        with open(bb_file) as f:
            text = f.read()
            coordinates = [int(nb) for nb in text.split(',')]
            x = coordinates[0]
            y = coordinates[1]
            width = coordinates[2] - x
            height = coordinates[3] - y

        txt = "{} {} {} {} {}".format(object_class, x, y, width, height)
        bb_file_name = bb_file.split('/')[-1].split('_')[0]
        with open(os.path.join(bb_dir2, bb_file_name).replace("\\","/"), 'w') as f:
            f.write(txt)
        print("Saved {}".format(bb_file_name))

def rename_files():
    rot_dir = os.path.join(INPUT_DIR, '../Orientations').replace("\\","/")
    tra_dir = os.path.join(INPUT_DIR, '../Translations').replace("\\","/")
    im_files = [os.path.join(INPUT_DIR, f).replace("\\","/") for f in os.listdir(INPUT_DIR) if f.endswith(('jpg', 'png'))]
    rot_files = [os.path.join(rot_dir, f).replace("\\","/") for f in os.listdir(rot_dir)]
    tra_files = [os.path.join(tra_dir, f).replace("\\","/") for f in os.listdir(tra_dir)]
    for im_file in im_files:
        new_path = '/'.join(im_file.split('/')[:-1]) + '/ToolYellow' + im_file.split('ool')[-1]
        os.rename(im_file, new_path)
    for rot_file in rot_files:
        new_path = '/'.join(rot_file.split('/')[:-1]) + '/ToolYellow' + rot_file.split('ool')[-1]
        os.rename(rot_file, new_path)
    for tra_file in tra_files:
        new_path = '/'.join(tra_file.split('/')[:-1]) + '/ToolYellow' + tra_file.split('ool')[-1]
        os.rename(tra_file, new_path)

def correct_translations():
    tra_dir = os.path.join(INPUT_DIR, '../output/Translations').replace("\\","/")
    tra_files = [os.path.join(tra_dir, f).replace("\\","/") for f in os.listdir(tra_dir) if f.startswith('YellowTool')]
    for tra_file in tra_files:
        with open(tra_file) as f:
            translation = f.read()
        translation = translation.split(" ")[1:]
        print(translation)
        for i in range(3):
            translation[i] = float(translation[i].rstrip())*(75/500)
        txt = ' {} {} {}'.format(translation[0], translation[1], translation[2])
        with open(tra_file, 'w') as f:
            f.write(txt)
        print('Wrote {}'.format(tra_file.split('/')[-1]))
def copy_stuff():
    result_dir = 'C:/Users/owner/Desktop/K/ToolWithMarkers/result'
    im_dir = 'C:/Users/owner/Desktop/K/ToolWithMarkers/Acquisition/output/cropped_images/resized'
    out_dir = 'C:/Users/owner/Desktop/K/ToolWithMarkers/images_localized_resized'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    images = os.listdir(result_dir)
    for image_name in images:
        image_file = os.path.join(im_dir, image_name.split('.')[0]+'.png')
        image = cv2.imread(image_file)
        cv2.imwrite(os.path.join(out_dir,image_name.split('.')[0]+'.png'), image)
        print("{} copied".format(image_name))


def create_correspondances_json_from_aruco_files():
    input_dir = 'C:/Users/owner/Desktop/K/Divs/ToolWithMarkers/ArucoResults/ToTestCNN'
    tra_dir = os.path.join(input_dir, 'extrinsic_t').replace("\\","/")
    rot_dir = os.path.join(input_dir, 'extrinsic').replace("\\","/")
    out_tra_dir = os.path.join(input_dir, 'Translations').replace("\\","/")
    out_rot_dir = os.path.join(input_dir, 'Orientations').replace("\\","/")

    correspondances = {}

    images = os.listdir(os.path.join(input_dir, 'result'))
    for image in images:
        correspondances[image] = {}
        with open(os.path.join(rot_dir, image.split('.')[0] + '.txt')) as f:
            content = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            content = [[float(x.strip())] for x in content]
            angles = np.asarray(content)
            rot = cv2.Rodrigues(angles)[0]
            correspondances[image]['angles'] = angles.tolist()
            correspondances[image]['rotation'] = rot.tolist()

        with open(os.path.join(tra_dir, image.split('.')[0] + '.txt')) as f:
            content = f.readlines()
            content = [float(x.strip()) for x in content]
            correspondances[image]['center'] = content

    with open(os.path.join(input_dir, 'correspondances_by_name.json'), 'w') as f:
        json.dump(correspondances, f)

def goloum():
    input_dir = ""
    out_dir = ""
    with open("C:/Users/owner/Desktop/K/test_names.txt") as f:
        names_raw = f.read()
        names = names_raw.splitlines()
    for name in names:
        image_path = os.path.join(input_dir, name)
        dest_path = os.path.join(out_dir, name)
        copyfile(image_path, dest_path)
if __name__ == '__main__':
    create_correspondances_json_from_aruco_files()
