import cv2
import cv2.aruco as aruco
import glob
import yaml
import time
import numpy as np
import pickle as cPickle
import os

def draw(img, corners, imgpts):

    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (0,0,255), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (255,0,0), 5)
    return img

objectClass = 'latte'
pathRoot = '/home/hpc/StructureFromMotion/OpenMVG_OpenMVS/Comparing2'

#path = pathRoot + '//' + 'capture//lipton//external' + '//' + sessionName

with open('calibration.yaml') as f:
    loadeddict = yaml.load(f)
camera_matrix = np.asarray(loadeddict.get('camera_matrix'))
dist_coeff = np.asarray(loadeddict.get('dist_coeff'))
objp = np.zeros((3*2,3), np.float32)
p = 60 * np.mgrid[0:3:,0:2].T.reshape(-1,2)
objp[:,0] = p[:,0]
objp[:,1] = p[:,1]
print("objp shape ", objp.shape)
print("objp ", objp)
print("p shape ", p.shape)
print("p ", p)
print("Don't leave me alone")

axis = 60*np.float32([[1,0,0], [0,1,0], [0,0,1]]).reshape(-1,3)
dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
board = aruco.CharucoBoard_create(4, 3, 0.06, 0.03,dictionary)

background = ['carpet', 'desk','tile']
orientation = ['vertical', 'horizontal']
marker_loc = ['left', 'right']

for b in background:
    for o in orientation:
        for l in marker_loc:

            sessionName = b + '//' + o + '//' + l
            path = pathRoot + '//image//' + sessionName

            files = glob.glob(path + '//*.jpg') #Wildcards can be used
            # for file in files:
            # print(file)
            print(path)
            numImage = len(files)
            print(numImage)
            if numImage == 0:
                continue

            pathSaveResult   = pathRoot + '//result//' + sessionName
            pathSaveCalib    = pathRoot + '//extrinsic//' + sessionName
            pathSaveCalib_t  = pathRoot + '//extrinsic_t//' + sessionName

            if not os.path.exists(pathSaveResult):
                os.makedirs(pathSaveResult)
            if not os.path.exists(pathSaveCalib):
                os.makedirs(pathSaveCalib)
            if not os.path.exists(pathSaveCalib_t):
                os.makedirs(pathSaveCalib_t)

            imageSize = (0, 0)
            charucoCorners = []
            charucoIds = []
            retval =0

            for file in files:
                image = cv2.imread(file)
                #cv2.imwrite(pathSaveImage + '//' + os.path.basename(file), image)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                markers = aruco.detectMarkers(gray, dictionary)
                im_with_charuco_board = image
                if markers[1] is not None:
                    refined=aruco.refineDetectedMarkers(gray, board, markers[0], markers[1], markers[2])
                    charuco = aruco.interpolateCornersCharuco(refined[0], refined[1], gray, board)
                    im_with_charuco_board = aruco.drawDetectedCornersCharuco(image, charuco[1], charuco[2], (0, 255, 0))

                    if charuco[1] is not None:
                        if len(charuco[1]) > 3:
                            corners = charuco[1]
                            ids = charuco[2]
                            retval, rvec, tvec = aruco.estimatePoseCharucoBoard(corners, ids, board, camera_matrix, dist_coeff)
                            corners3D = objp[ids,:]
                            est = cv2.solvePnP(corners3D, corners, camera_matrix, dist_coeff)
                            rvec =est[1]
                            tvec =est[2]

                            rvec_list = rvec.tostring()
                            #rvec_list.append(rvec[0].tostring())
                            #vec_list.append(rvec[1].tostring())
                            #rvec_list.append(rvec[2].tostring())

                            if retval == True:
                                imgpts, jac = cv2.projectPoints(axis, rvec, tvec, camera_matrix, dist_coeff)
                                image = draw(image, corners, imgpts)
                                cv2.imwrite(pathSaveResult + '//' + os.path.basename(file) , image)
                                #f = open("test.txt", "w")
                                #f.write(cPickle.dumps(rvec))
                                #f.close()
                                name, ext = os.path.splitext(os.path.basename(file))
                                np.savetxt(pathSaveCalib + '//' + name + '.txt', rvec, fmt=(' %.4f'))
                                np.savetxt(pathSaveCalib_t + '//' + name + '.txt', tvec, fmt=(' %.4f'))
                                #np.savetxt('test.txt',rvec, fmt='%.4f ')

                cv2.namedWindow('img', cv2.WINDOW_NORMAL)
                cv2.imshow('img', image)
                cv2.waitKey(1)
                cv2.destroyAllWindows()
