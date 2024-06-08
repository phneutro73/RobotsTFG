import numpy as np
import cv2 as cv
import math
import requests
import time
import json

def send_command_to_robot(id, command):
  url = "http://192.168.159.31/command?cmd="
  
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

def calculate_angle(vector1, vector2):
    unit_vector1 = vector1 / np.linalg.norm(vector1)
    unit_vector2 = vector2 / np.linalg.norm(vector2)
    dot_product = np.dot(unit_vector1, unit_vector2)
    dot_product = np.clip(dot_product, -1.0, 1.0)
    angle_rad = math.acos(dot_product)
    # Usar el producto cruz para determinar la dirección del ángulo
    cross_product = np.cross(unit_vector1, unit_vector2)
    
    # Si el componente z del producto cruz es negativo, el ángulo debe ser ajustado a 360 grados menos el ángulo calculado
    if cross_product < 0:
        angle_deg = 360 - math.degrees(angle_rad)
    else:
        angle_deg = math.degrees(angle_rad)

    return angle_deg

def navigate_to_marker(robot_id, target_marker_id, centers, ids, direction_vector,distance_meters):
    index_robot = np.where(ids == robot_id)[0]
    index_marker = np.where(ids == target_marker_id)[0]

    if index_robot.size > 0 and index_marker.size > 0:
        center_robot = centers[index_robot[0]]
        center_marker = centers[index_marker[0]]
        
        # Asumimos que la dirección es paralela a la parte superior del marcador
        center_vector = center_marker - center_robot
        angle = calculate_angle(direction_vector, center_vector)
        
        # if abs(angle) > 4:
        #     if angle <= 180:
        #         send_command_to_robot(robot_id, 'move_right')
        #     else:
        #         send_command_to_robot(robot_id, 'move_left')
        # elif distance_meters >= 0.3:
            
        #     send_command_to_robot(robot_id, 'move_forward')
        # else:
        #     print("Reached target")
        #     return True  # Indica que ha llegado al marcador
        print (distance_meters, robot_id, target_marker_id, angle)
        
    return False  # Indica que aún no ha llegado al marcador

def main():
    try:
        with open('camera_calib.json') as file:
            data = json.load(file)
        camera_matrix = np.array(data['camera_matrix'])
        dist_coeffs = np.array(data['distortion_coefficients'])
    except:
        print("File not valid")

    dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_ARUCO_MIP_36h12)
    arucoParams = cv.aruco.DetectorParameters()
    cap = cv.VideoCapture(1)
    
    camera_width = 800
    camera_height = 600
    camera_frame_rate = 60

    cap.set(3, camera_width)
    cap.set(4, camera_height)
    cap.set(5, camera_frame_rate)

    robot_id = 71
    
    route = [73, 104, 73, 106]  # IDs de los marcadores por los que debe pasar
    current_target_index = 0  # Comienza con el primer marcador en la ruta

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        corners, ids, rejected = cv.aruco.detectMarkers(gray_frame, dictionary, parameters=arucoParams)
        
        if ids is not None:
            ids = ids.flatten()
            
        if ids is not None and len(ids) > 0:
            centers = [np.mean(corner[0], axis=0).astype(int) for corner in corners]
            
            rvecs, tvecs, _ = cv.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)
            cv.aruco.drawDetectedMarkers(frame, corners, ids)
            
            if current_target_index < len(route):
                target_marker_id = route[current_target_index]
                index_robot = np.where(ids == robot_id)[0]
                index_marker = np.where(ids == target_marker_id)[0]
                
                if index_robot.size > 0 and index_marker.size > 0:
                                        
                    center_robot = centers[index_robot[0]]
                    center_marker = centers[index_marker[0]]
                    
                    cv.line(frame, tuple(center_robot), tuple(center_marker), (255, 0, 0), 2)
                    distance_meters = np.linalg.norm(tvecs[index_robot][0] - tvecs[index_marker][0])
                    mid_point = (center_robot + center_marker) // 2
                    cv.putText(frame, f"{distance_meters:.2f}m", tuple(mid_point), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Asumimos que la dirección es paralela a la parte superior del marcador
                    robot_corners = corners[index_robot[0]][0]
                    top_right = robot_corners[1]
                    top_left = robot_corners[0]
                    direction_vector = top_right - top_left
                    end_point = center_robot + direction_vector
                    end_point = tuple(end_point.astype(int))
                    cv.arrowedLine(frame, tuple(center_robot), end_point, (0, 0, 255), 2, tipLength=0.2)
                    if navigate_to_marker(robot_id, target_marker_id, centers, ids, direction_vector, distance_meters):
                        current_target_index += 1  # Pasa al siguiente marcador en la ruta
                    time.sleep(0.5)
                
        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
