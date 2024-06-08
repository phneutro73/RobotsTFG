import numpy as np
import cv2 as cv
import json
from pynput.keyboard import Key, Controller
import time

# Inicializar el controlador de teclado de pynput
keyboard = Controller()

def calculate_marker_distance(tvec1, tvec2):
  # Calcular la distancia euclidiana entre dos marcadores
  tvec1_to_origin = np.array(tvec1).reshape((3, 1))
  tvec2_to_origin = np.array(tvec2).reshape((3, 1))
  return np.linalg.norm(tvec1_to_origin - tvec2_to_origin)

def calculate_direction_and_distance(tvec1, tvec2):
  # Extraer solo los componentes X e Y
  direction_3d = tvec2 - tvec1
  direction_2d = direction_3d[:2]  # Toma solo los componentes X e Y

  # Calcular la distancia en 2D
  distance_2d = np.linalg.norm(direction_2d)

  # Normalizar el vector 2D si no es el vector cero
  if distance_2d != 0:
      normalized_direction_2d = direction_2d / distance_2d
  else:
      normalized_direction_2d = direction_2d

  return normalized_direction_2d, distance_2d

def midpoint(ptA, ptB):
  return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5

def press_key(key):
  keyboard.press(key)
  time.sleep(0.1)
  keyboard.release(key)

def send_command_to_robot(id, command):
  if command == 'move_forward':
    press_key(Key.right)
    # print("right")
  
  elif command == 'move_backward':
    press_key(Key.left)
    # print("left")

  elif command == 'move_left':
    press_key(Key.up)
    # print("up")

  elif command == 'move_right':
    press_key(Key.down)
    # print("down")
    
def travel_to_code(marker_id, robot_id, tvecs, ids):
  marker = np.where(ids == marker_id)[0][0]
  robot = np.where(ids == robot_id)[0][0]

  tvec_0 = tvecs[marker][0]
  tvec_otro = tvecs[robot][0]

  direction, distance = calculate_direction_and_distance(tvec_otro, tvec_0)

  # Decidir el movimiento basado en la dirección
  if distance > 0.3:
    if direction[0] < 0:
      send_command_to_robot(robot, 'move_backward')
    elif direction[0] > 0:
      send_command_to_robot(robot, 'move_forward')

    # Luego, decidir avanzar o retroceder
    if direction[1] < 0:
      send_command_to_robot(robot, 'move_left')
    elif direction[1] > 0:
      send_command_to_robot(robot, 'move_right')
  else:
    print("Reached marker  ",marker_id)
    return True
  
def main():
  try:
    with open('camera_calib.json') as file:
      data = json.load( file )
    camera_matrix = np.array(data['camera_matrix']) 
    dist_coeffs = np.array(data['distortion_coefficients'])
  except:
    print("File not valid")

  dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_ARUCO_MIP_36h12)
  arucoParams = cv.aruco.DetectorParameters()

  marker_0 = [10, False]
  marker_1 = [11, False]
  marker_2 = [12, False]
  marker_3 = [13, False]
  marker_4 = [14, False]
   
  robot_id = 0

  # Inicializar la cámara, 0  por defecto
  cap = cv.VideoCapture(1)

  camera_width = 1280
  camera_height = 720
  camera_frame_rate = 30

  cap.set(3, camera_width)
  cap.set(4, camera_height)
  cap.set(5, camera_frame_rate)

  while True:
    _, frame = cap.read()

    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    corners, ids, rejected = cv.aruco.detectMarkers(gray_frame, dictionary, parameters=arucoParams)

    if ids is not None and len(ids) > 0:

      cv.aruco.drawDetectedMarkers(frame, corners, ids, borderColor=(255,255,0))

      _, tvecs, _ = cv.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)

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
          
          # Calcular la dirección y distancia entre marcadores en el espacio 3D
          distance = calculate_marker_distance(tvecs[i][0], tvecs[j][0])
          
          text_distance = f"{distance:.2f}m"

          # Encontrar el punto medio en la línea para el texto de la distancia
          mid_point = midpoint(centers[i], centers[j])
          
          # Poner el texto en el centro de la línea
          cv.putText(frame, text_distance, (int(mid_point[0]), int(mid_point[1])), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
      
      if marker_1[0] in ids and robot_id in ids and marker_1[1] == False:
        travel_to_code(marker_1[0], robot_id, tvecs, ids)
        if travel_to_code(marker_1[0], robot_id, tvecs, ids):
          marker_1[1] = True
          print(marker_1[1])
          
      elif marker_3[0] in ids and robot_id in ids and marker_1[1] == True:
        travel_to_code(marker_3[0], robot_id, tvecs, ids)
        if travel_to_code(marker_3[0], robot_id, tvecs, ids):
          marker_3[1] = True
          print(marker_3[1])
      
      elif marker_2[0] in ids and robot_id in ids and marker_3[1] == True:
        travel_to_code(marker_2[0], robot_id, tvecs, ids)
        if travel_to_code(marker_2[0], robot_id, tvecs, ids):
          marker_2[1] = True
          print(marker_2[1])
        
      
          
      # if marker_4[0] in ids and robot_id in ids and marker_3[1] == True:
      #   travel_to_code(marker_4[0], robot_id, tvecs, ids)
      #   if travel_to_code(marker_4[0], robot_id, tvecs, ids):
      #     marker_4[1] = True
      #     marker_1[1] = False
      #     print(marker_4[1])
      
      # if marker_1[0] in ids and robot_id in ids and marker_4[1] == True:
      #   travel_to_code(marker_1[0], robot_id, tvecs, ids)
      #   if travel_to_code(marker_1[0], robot_id, tvecs, ids):
      #     marker_1[1] = True
      #     print(marker_1[1])
              
    # frame = cv.flip(frame,1)
    cv.imshow('frame', frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
      break

  cap.release()
  cv.destroyAllWindows()

if __name__ == "__main__":
  main()