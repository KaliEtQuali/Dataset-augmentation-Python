import cv2
import cv2.aruco as aruco
dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
marker = aruco.drawMarker(dictionary, 11, 200)
cv2.imwrite('/home/hpc/StructureFromMotion/OpenMVG_OpenMVS/Comparing/test_4.jpg', marker)
board = aruco.CharucoBoard_create(4, 3, 0.06, 0.03,dictionary)
boardImg = board.draw((400,300))
cv2.imwrite('/home/hpc/StructureFromMotion/OpenMVG_OpenMVS/Comparing/test_board_1.jpg', boardImg)
