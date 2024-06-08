import numpy as np
import cv2 as cv
import glob
import json

chessboardSize = (9,7)
size_of_chessboard_squares_mm = 20
frameSize = (1920,1080)

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)  

objp = np.zeros((chessboardSize[0]*chessboardSize[1],3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)

objp = objp * size_of_chessboard_squares_mm

objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('images/*.jpg')

for image in images:
  print("loaded...")
  img = cv.imread(image)
  gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

  ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)

  if ret == True:
    objpoints.append(objp)
    corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
    imgpoints.append(corners)

    cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
    cv.imshow('img', img)
    while True:
      if cv.waitKey(0) == 32:  # 32 es el código ASCII para la tecla de espacio
        break
    

cv.destroyAllWindows()

ret, cameraMatrix, distortionCoefficients, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, frameSize, None, None)

with open('camera_calib.json', 'w') as file:
  json.dump( { 'camera_matrix': cameraMatrix.tolist(),
  'distortion_coefficients': distortionCoefficients.tolist()}, file )
