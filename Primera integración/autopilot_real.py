import numpy as np
import cv2 as cv
import json
from pynput.keyboard import Key, Controller
import time
import requests

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

def align_robot_to_target(tvec_robot, tvec_target, robot_orientation):
  # Calcula el vector de dirección desde el robot al objetivo
  direction = np.array(tvec_target) - np.array(tvec_robot)
  direction_norm = np.linalg.norm(direction)
  if direction_norm == 0:
      return 0  # El robot ya está en el objetivo, no necesita alineación

  # Normaliza el vector de dirección
  direction = direction / direction_norm

  # Producto punto para determinar si el frente del robot está alineado con el objetivo
  dot_product = np.dot(robot_orientation, direction)
  angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
  angle_deg = np.degrees(angle)

  # Producto cruz para determinar la dirección del giro
  cross_prod = np.cross(robot_orientation, direction)
  
  if cross_prod[2] > 0:
      send_command_to_robot(robot_id, 'move_right', 0.1)
  else:
      send_command_to_robot(robot_id, 'move_left', 0.1)

  return angle_deg

def approach_target(tvec_robot, tvec_target):
  # Asegúrate de que el robot esté alineado antes de moverse hacia adelante
  while True:
      alignment_angle = align_robot_to_target(tvec_robot, tvec_target, robot_orientation)
      if abs(alignment_angle) < 5:  # Asume un umbral de 5 grados para una alineación adecuada
          break
  
  # Mover hacia el objetivo
  distance = np.linalg.norm(np.array(tvec_target) - np.array(tvec_robot))
  while distance > 0.1:  # Asume que el robot debe detenerse a 10 cm del objetivo
      send_command_to_robot(robot_id, 'move_forward', 0.1)
      # Aquí deberías actualizar tvec_robot con nueva información de posición
      distance = np.linalg.norm(np.array(tvec_target) - np.array(tvec_robot))

def calculate_angle(tvec_robot, tvec_target):
    # Asegurándose de que los vectores son del tipo correcto
    vector_robot = np.array(tvec_robot, dtype='float32')
    vector_target = np.array(tvec_target, dtype='float32')

    # Vector de dirección desde el robot hacia el objetivo
    direction = vector_target - vector_robot

    # Vector de orientación del robot, necesitamos definirlo correctamente
    # Asumiendo que es un vector unitario que apunta hacia adelante
    robot_forward = np.array([1, 0, 0])  # Asumir que el robot mira inicialmente hacia el eje X

    # Normalizar los vectores
    direction_normalized = direction / np.linalg.norm(direction)

    # Calcular ángulo en radianes entre el frente del robot y el vector de dirección
    dot_product = np.dot(robot_forward, direction_normalized)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))

    # Calcular el producto cruz para determinar la dirección del giro
    cross_prod = np.cross(robot_forward, direction_normalized)

    # Convertir a grados para facilitar la interpretación
    angle_deg = np.degrees(angle)

    # Usar el componente Z para determinar la dirección del giro
    if cross_prod[2] < 0:
        angle_deg = -angle_deg

    return angle_deg

def midpoint(ptA, ptB):
  return (ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5

def get_marker_center(corner):
  corner = np.array(corner)
  x = int(corner[:, 0].mean())
  y = int(corner[:, 1].mean())
  return (x, y)

def send_command_to_robot(id, command):
  url = "http://192.168.1.73/command?cmd="
  
  if command == 'move_forward':
    requests.get(url + 'S')
    print("forward")
  
  elif command == 'move_backward':
    requests.get(url + 'Z')
    print("backward")

  elif command == 'move_left':
    requests.get(url + 'A')
    print("left")

  elif command == 'move_right':
    requests.get(url + 'D')
    print("right")
    
def control_robot_based_on_angle(angle, robot_id):
  threshold_angle = 5  # Ángulo en grados para decidir cuando girar

  if angle > threshold_angle:
      send_command_to_robot(robot_id, 'move_right')
  elif angle < -threshold_angle:
      send_command_to_robot(robot_id, 'move_left')
  else:
      send_command_to_robot(robot_id, 'move_forward')
  
def main():
  try:
    with open('../camera_calib.json') as file:
      data = json.load( file )
    camera_matrix = np.array(data['camera_matrix']) 
    dist_coeffs = np.array(data['distortion_coefficients'])
  except:
    print("File not valid")

  dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_ARUCO_MIP_36h12)
  arucoParams = cv.aruco.DetectorParameters()

  marker_id = 71
  robot_id = 72

  cap = cv.VideoCapture(1)

  camera_width = 1920
  camera_height = 1080
  camera_frame_rate = 30

  cap.set(3, camera_width)
  cap.set(4, camera_height)
  cap.set(5, camera_frame_rate)

  while True:
    ret, frame = cap.read()
    
    if not ret:
      print("Failed to grab frame")
      break

    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    corners, ids, rejected = cv.aruco.detectMarkers(gray_frame, dictionary, parameters=arucoParams)

    if ids is not None and len(ids) > 0:

      cv.aruco.drawDetectedMarkers(frame, corners, ids)

      rvecs, tvecs, _ = cv.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)
      
      centers = []

      centers_vector = [get_marker_center(corner[0]) for corner in corners]
      
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

      if marker_id in ids and robot_id in ids: 

        index_target = np.where(ids == marker_id)[0][0]
        index_robot = np.where(ids == robot_id)[0][0]
        
        center_target = centers_vector[index_target]
        center_robot = centers_vector[index_robot]
        cv.arrowedLine(frame, center_robot, center_target, (0, 255, 0), 2, tipLength=0.2)

        tvec_target = tvecs[index_target][0]
        tvec_robot = tvecs[index_robot][0]

        direction, distance = calculate_direction_and_distance(tvec_robot, tvec_target)
        
        direction[1] = direction[1] * -1
        print("X:", direction[0], " Y:", direction[1], " Dist:", distance)
        
        # Calcular ángulo
        angle = calculate_angle(tvec_robot, tvec_target)
        print(f"Ángulo: {angle} grados")

        # Decidir el movimiento basado en el ángulo
        # control_robot_based_on_angle(robot_id, angle)
        
        time.sleep(1)

    # frame = cv.flip(frame,1)
    cv.imshow('frame', frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
      break

  cap.release()
  cv.destroyAllWindows()

if __name__ == "__main__":
  main()