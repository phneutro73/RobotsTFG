import numpy as np
import cv2 as cv
import json

def calculate_marker_distance(tvec1, tvec2):
  # Calcular la distancia euclidiana entre dos marcadores
  tvec1_to_origin = np.array(tvec1).reshape((3, 1))
  tvec2_to_origin = np.array(tvec2).reshape((3, 1))
  return np.linalg.norm(tvec1_to_origin - tvec2_to_origin)

def midpoint(ptA, ptB):
  return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5

try:
  with open('camera_calib.json') as file:
    data = json.load( file )
  camera_matrix = np.array(data['camera_matrix'])
  dist_coeffs = np.array(data['distortion_coefficients'])
except:
  print("File not valid")

dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_ARUCO_MIP_36h12)
arucoParams = cv.aruco.DetectorParameters()

cap = cv.VideoCapture(1)

camera_width = 1280
camera_height = 720
camera_frame_rate = 30

cap.set(3, camera_width)
cap.set(4, camera_height)
cap.set(5, camera_frame_rate)

while True:
  ret, frame = cap.read()

  gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

  corners, ids, rejected = cv.aruco.detectMarkers(gray_frame, dictionary, parameters=arucoParams)

  if ids is not None and len(ids) > 0:

    cv.aruco.drawDetectedMarkers(frame, corners, ids)

    rvecs, tvecs, _ = cv.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)

    centers = []
    
    # Calcular los centros de los marcadores
    for i, corner in enumerate(corners):
      center = corner[0].mean(axis=0)
      centers.append(center)

    # Dibujar líneas entre los centros y mostrar la distancia
    for i in range(len(centers)):
      for j in range(i + 1, len(centers)):
        # Dibujar la línea entre los centros
        cv.line(frame, tuple(centers[i].astype(int)), tuple(centers[j].astype(int)), (255, 0, 0), 2)
        
        # Calcular la distancia entre marcadores en el espacio 3D
        distance = calculate_marker_distance(tvecs[i][0], tvecs[j][0])
        
        text_distance = f"{distance:.2f}m"

        # Encontrar el punto medio en la línea para el texto de la distancia
        mid_point = midpoint(centers[i], centers[j])
        
        # Poner el texto en el centro de la línea
        cv.putText(frame, text_distance, (int(mid_point[0]), int(mid_point[1])), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if distance < 0.1:
          collision_message = f"Collision between {ids[i][0]} and {ids[j][0]}"
          cv.putText(frame, collision_message, (int(mid_point[0] + 10), int(mid_point[1] + 20)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

  # frame = cv.flip(frame,1)
  cv.imshow('frame', frame)

  if cv.waitKey(1) & 0xFF == ord('q'):
    break

cap.release()
cv.destroyAllWindows()
