import cv2
import cv2.aruco as aruco
import numpy as np
import glob
import yaml


path ='C://Users//s1358//PycharmProjects//test_aruco//capture//test2\internal'
files = glob.glob(path + '//*.jpg') # ワイルドカードが使用可能
for file in files:
    print(file)

dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
board = aruco.CharucoBoard_create(5, 7, 0.04, 0.02,dictionary)


objp = np.zeros((4*6,3), np.float32)
p = 40 * np.mgrid[0:4:,0:6].T.reshape(-1,2)

objp[:,0] = p[:,1]
objp[:,1] = -p[:,0]

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.


numImage = len(files)
print(numImage)
imageSize = (0, 0)
charucoCorners = []
charucoIds = []
for file in files:
    image = cv2.imread(file)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    markers = aruco.detectMarkers(image, dictionary)
    if markers[1] is not None:
        refined=aruco.refineDetectedMarkers(gray, board, markers[0], markers[1], markers[2])
        charuco = aruco.interpolateCornersCharuco(refined[0], refined[1], gray, board)
        if charuco[1] is not None:
            if len(charuco[1])==24:
                charucoCorners.append(charuco[1])
                charucoIds.append(charuco[2])
                objpoints.append(objp)

        imageSize = (image.shape[0],image.shape[1])
    #print(imageSize)
    #cv2.imshow('test',image)



cameraMatrix= np.array([[1000, 0, 0.5*imageSize[0]], [0,1000,0.5*imageSize[1]], [0,0,1]])
distCoeffs= np.zeros((12,1))
#cameraParam = aruco.calibrateCameraCharuco(charucoCorners, charucoIds, board, imageSize, cameraMatrix, distCoeffs)
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, charucoCorners, gray.shape[::-1], None,None)
#ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
# It's very important to transform the matrix to list.
data = {'camera_matrix': np.asarray(mtx).tolist(), 'dist_coeff': np.asarray(dist).tolist()}

with open("calibration.yaml", "w") as f:
    yaml.dump(data, f)


# You can use the following 4 lines of code to load the data in file "calibration.yaml"
# with open('calibration.yaml') as f:
#     loadeddict = yaml.load(f)
# mtxloaded = loadeddict.get('camera_matrix')
# distloaded = loadeddict.get('dist_coeff')


#retval, rvec, tvec = aruco.estimatePoseCharucoBoard(charucoCorners, charucoIds, board, camera_matrix, dist_coeffs)  # posture estimation from a charuco board
#        if retval == True:
#            im_with_charuco_board = aruco.drawAxis(im_with_charuco_board, camera_matrix, dist_coeffs, rvec, tvec, 100)  # axis length 100 can be changed according to your requirement
#        else:
#            im_with_charuco_left = frame_remapped
#        cv2.imshow("charucoboard", im_with_charuco_board)
