import numpy as np
import cv2 as cv
import json

try:
  with open('camera_calib.json') as file:
    data = json.load( file )
  camera_matrix = np.array(data['camera_matrix'])
  dist_coeffs = np.array(data['distortion_coefficients'])
  print('Camera matrix:', camera_matrix)
  print('Distortion coefficients:', dist_coeffs)
except:
  print("File not valid")

dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_ARUCO_MIP_36h12)
arucoParams = cv.aruco.DetectorParameters()

cap = cv.VideoCapture(1)

camera_width = 1920
camera_height = 1080
camera_frame_rate = 30

cap.set(3, camera_width)
cap.set(4, camera_height)
cap.set(5, camera_frame_rate)

while True:
  ret, frame = cap.read()

  gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

  corners, ids, rejected = cv.aruco.detectMarkers(gray_frame, dictionary, parameters=arucoParams)

  

  if ids is not None and len(ids) > 0:
    # Dibujar el marco para cada marcador
    cv.aruco.drawDetectedMarkers(frame, corners, ids)

    # Estimar la pose de los marcadores
    rvecs, tvecs, _ = cv.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)

    for i in range(len(ids)):
      # Dibujar los ejes para cada marcador
      cv.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.05)

      # Calcular la distancia a la cámara y mostrarla junto con el ID del marcador
      x, y, z = tvecs[i][0]
      text_position = f"({x:.2f}, {y:.2f})"
      text_distance = f"Distance: {z:.2f}m"
      text_id = f"ID: {ids[i][0]}"
      corner = corners[i]
      bottom_left = tuple(corner[0][0].ravel().astype(int))
      # cv.putText(frame, text_id, (bottom_left[0], bottom_left[1]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255), 2)
      cv.putText(frame, text_position, (bottom_left[0], bottom_left[1]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
      # cv.putText(frame, text_distance, (bottom_left[0], bottom_left[1] + 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

  cv.imshow('frame', cv.flip(frame,1))

  if cv.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv.destroyAllWindows()
